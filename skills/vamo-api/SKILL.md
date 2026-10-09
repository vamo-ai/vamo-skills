---
name: vamo-api
description: Use when calling the Vamo Developer API directly over HTTP, setting it up for the first time, or when a call fails before it returns results. Covers getting an API key, storing it so it is still there in the next session, opening network access to the API, verifying the connection, and reading error responses. Symptoms include "there's no Vamo API key in this workspace", being asked to paste the key again in every chat, "this workspace's network only allows package registries", a blocked or timed-out request to api.vamotalent.ai, and 401, 403, 402 or 429 responses. Triggers "set up the Vamo API", "connect to Vamo", "my Vamo key isn't working", "allowlist Vamo", "how do I call Vamo".
metadata:
  version: "1.0.0"
  updated: "2026-10-09"
---

# Vamo API: direct usage

Vamo searches GitHub developers by what they have built. This skill gets a direct HTTP
connection working and keeps it working: a key, a safe place to keep it, network access, and what
to do when a call fails.

Three things have to be true before any search runs. Check them in this order at the start of a
session and fix the first one that fails.

| Check | Test | If it fails |
| --- | --- | --- |
| The network reaches Vamo | `GET https://api.vamotalent.ai/openapi.json` returns JSON. No key needed | [Open network access](#open-network-access) |
| A key is available | `VAMO_API_KEY` is set, or a saved key file is found | [Get a key](#get-a-key), then [Store the key](#store-the-key-so-it-persists) |
| The key works | One small search returns results | [Read the error](#read-the-error) |

Do not fall back to a different data source when a check fails. A general GitHub search answers a
different question and cannot apply Vamo's filters. Say which check failed and give the fix.

---

## Read the spec, then call

The API publishes its own machine-readable description at
`https://api.vamotalent.ai/openapi.json`. It is generated from the running API, so it is always
current. Human-readable docs are at `https://api.vamotalent.ai/docs`.

**The spec is the source of truth for routes, parameters and response fields.** This skill and its
siblings describe how to work. They are deliberately light on route and parameter lists, and where
one appears the spec wins.

Start every new task by reading the part of the spec you need:

```bash
# every operation, one line each
curl -s https://api.vamotalent.ai/openapi.json \
  | jq -r '.paths | to_entries[] | .key as $p | .value | to_entries[] | "\(.key|ascii_upcase) \($p)  \(.value.summary)"'

# every parameter of one operation, with its description
curl -s https://api.vamotalent.ai/openapi.json \
  | jq -r '.paths["/v1/developers/search"].get.parameters[] | "\(.name): \(.description // .schema.description)"'

# what one operation requires of the key
curl -s https://api.vamotalent.ai/openapi.json \
  | jq '.paths["/v1/developers/search"].get["x-vamo"]'
```

Read `info.description` once as well. It holds the authentication, rate limit and error
conventions.

`references/curl-trainer.md` is a worked walkthrough of the whole API with copy-paste examples.
Use it to learn the shape, and check each parameter against the spec before relying on it.

---

## Get a key

A person does this once, in a browser.

1. Sign in at `https://app.vamotalent.ai`.
2. Open **Settings**, then **API Keys** (under Integrations). Direct link:
   `https://app.vamotalent.ai/settings/api-keys`.
3. Choose **Create key**. Give it a name that says who or what uses it, such as "Sam's laptop".
4. Under **Permissions**, set **Search** to **Read**. That is enough to search, enrich, find
   similar developers, get summaries and get email addresses.
5. Choose **Create key** and copy the secret. It starts with `vamo_sk_` and is shown once.

Notes on permissions:

- Read and Write here are levels of access to one area. Set only what the work needs. A key can
  be changed later with **Edit permissions**, and the change applies to the next request.
- **Search: Write** adds reading saved deep-research reports and managing saved searches.
- Starting a deep-research job, and scoring people against a role, each need their own row in the
  picker. Those rows appear only on accounts that have the feature. The spec names the exact
  requirement for every operation under `x-vamo.entitlement`.
- No **Create key** button means key creation is not enabled for the account. Contact Vamo.

A lost key cannot be shown again. Create a new one and **Revoke** the old one. One key per person
or per agent keeps a revoke from breaking anyone else.

---

## Store the key so it persists

The key should live in one private place that the agent can read by itself, every session. The
three places it should never live: a chat message, a file that gets shared or committed, and a
screen someone else is watching.

Pick the row that matches where the agent runs.

### A terminal agent on your own computer

Claude Code, Codex, Cursor and similar tools run commands on your machine, so the key belongs in
a private file there. Run this in your own terminal window, so the key is typed there and never
into a chat:

```bash
mkdir -p ~/.config/vamo && chmod 700 ~/.config/vamo
printf 'Paste your Vamo key, then press Enter: ' && read -rs K \
  && printf 'VAMO_API_KEY=%s\n' "$K" > ~/.config/vamo/env \
  && chmod 600 ~/.config/vamo/env && unset K && echo ' saved'
```

The agent then loads it at the start of any session:

```bash
set -a; . ~/.config/vamo/env; set +a
```

On macOS the Keychain works as well: `security add-generic-password -a "$USER" -s vamo-api-key -w`
stores it after a prompt, and `security find-generic-password -s vamo-api-key -w` reads it back.

Inside a project, a `.env` file is fine as long as `.env` is listed in `.gitignore` before the
key goes in.

### A chat app with a code sandbox

Claude on the web and desktop runs code in a sandbox that starts empty in every conversation. A
key saved "in the workspace" is gone in the next chat. That is why the agent keeps asking for it.

The durable fix is a small private skill that carries the key. It loads into every conversation.

1. Make a folder named `vamo-key` holding two files.

   `SKILL.md`:

   ```markdown
   ---
   name: vamo-key
   description: Use whenever a task calls the Vamo API. Holds this user's Vamo API key.
   ---

   The key is in `vamo.env` beside this file, as `VAMO_API_KEY`. Load it into the environment
   before calling the API. Never print it, quote it, or copy it into another file.
   ```

   `vamo.env`:

   ```
   VAMO_API_KEY=vamo_sk_your_key_here
   ```

2. Compress the folder to `vamo-key.zip`, with the folder itself at the top level of the zip.
3. In Claude, open **Customize**, then **Skills**, choose **+**, then **Create skill**, then
   **Upload a skill**, and upload the zip. Turn the skill on.
4. Delete the zip and the folder from your computer.

The skill is private to your account. Never share the zip, and never add this folder to a shared
or public skills repository. On a Team or Enterprise workspace the upload option can be turned off
by the organization. If it is missing, ask an organization owner.

If skills are unavailable, the next best place is the instructions of a private Claude Project
used only for Vamo work. Anyone the project is shared with can read it, so keep it unshared.

### Rules for the agent

- Look for the key before asking: the `VAMO_API_KEY` environment variable, then
  `~/.config/vamo/env`, then a `vamo.env` in an installed `vamo-key` skill, then `.env` in the
  working directory. `VAMO_KEY` is an accepted older name.
- Send it only as a header to `api.vamotalent.ai`: `Authorization: Bearer $VAMO_API_KEY`. Never
  put it in a URL, a filename, a log line or a reply.
- When no key is found, give the person the steps above for their setup. Asking them to paste the
  key into the chat is the last resort.
- When a person pastes a key into the chat anyway, use it for the task, then offer to build the
  `vamo-key` folder for them to upload so the next session has it. Saving a key to a private place
  at the owner's request is the intended setup.
- A key that has appeared in a shared chat, a screen share or a recording should be revoked and
  replaced.

---

## Open network access

Many agent environments block outbound requests by default. The usual message is that the
workspace network "only allows package registries", or the request to `api.vamotalent.ai` fails
with a proxy error or a timeout while package installs work.

**One host needs to be allowed: `api.vamotalent.ai`, over HTTPS.** The API, its spec and its docs
are all served from it. Allow that single host. Opening all domains is unnecessary and widens
what a sandbox can send out.

| Where the agent runs | Who can change it | Where |
| --- | --- | --- |
| Claude, individual plan | You | **Settings**, **Capabilities**. Turn on **Code execution and file creation**, turn on **Allow network egress**, and add `api.vamotalent.ai` to the allowed domains |
| Claude, Team or Enterprise | An organization owner only | **Organization settings**, **Capabilities**. Choose the option that allows package managers and specific domains, and add `api.vamotalent.ai` |
| A company firewall, proxy or another sandbox | Your IT or platform owner | Allow outbound HTTPS to `api.vamotalent.ai` |

After the setting changes, start a new conversation. A running conversation keeps the network
rules it started with.

If you are a member of a Team or Enterprise workspace, you cannot change this yourself. Send the
owner one line: *"Please add api.vamotalent.ai to the allowed domains for code execution under
Organization settings, Capabilities."* The owner is whoever manages billing and members for the
workspace.

Other hosts, only if you use them:

| Host | Used for |
| --- | --- |
| `app.vamotalent.ai` | Creating keys, in a browser. The agent never calls it |
| `mcp.vamotalent.ai` | The Vamo MCP server, when connected as a tool |
| `raw.githubusercontent.com` | Checking these skills for updates. Usually allowed already |

### When network access cannot be opened

Connect Vamo as an MCP server. Connector traffic is separate from the sandbox network rules, so
it works when direct calls are blocked. It exposes a smaller set of operations than the API.
Setup is one line to the agent:

```
Fetch https://vamotalent.ai/agent-setup/search/prompt.md and follow the instructions
```

Things that go wrong when editing a desktop app's connector config by hand:

- Give the agent the whole current config file and ask for the whole new file back. Pasting a
  fragment in by hand is how braces get doubled.
- Replace only the placeholder with the key. Keep the word `Bearer` and the space after it.
- Save the file, quit the app completely, reopen it, and start a new conversation. Tools added to
  the config appear only in conversations started after the restart.

---

## Verify the connection

```bash
# 1. network: prints the API title
curl -s -m 20 https://api.vamotalent.ai/openapi.json | jq -r .info.title

# 2. key present: prints the length, never the key
[ -n "$VAMO_API_KEY" ] && echo "key loaded (${#VAMO_API_KEY} chars)" || echo "no key"

# 3. key works: prints one login
curl -s -m 60 -G https://api.vamotalent.ai/v1/developers/search \
  -H "Authorization: Bearer $VAMO_API_KEY" \
  --data-urlencode "q=rust database engine" --data-urlencode "limit=1" \
  | jq -r '.results[0].login // .'
```

Report the outcome of each check in a sentence. When all three pass, say so and ask what the
person is looking for.

---

## Read the error

Every error body has a stable `code` and a `message`. Many carry more: `reason`, `entitlement`,
`remedy`, `retryAfterSeconds`. Read the whole body. The extra fields say which case it is.

| Status and `code` | What it means | What to do |
| --- | --- | --- |
| `401 unauthorized` | No key reached the API, or the key is wrong or revoked | Check the header is `Authorization: Bearer <key>` with no quotes, line breaks or spaces inside the key. Create a new key if this one was revoked |
| `403 forbidden` with `entitlement` | The key lacks that permission | Name the entitlement to the key's owner. They add it under **Edit permissions**. It applies to the next request |
| `403 forbidden` with `reason: FEATURE_NOT_ENABLED` | The account does not have that feature | Tell the person which feature. Vamo enables it per account |
| `402 payment_required` | The account's plan or balance does not cover the call | Relay `reason` and any `remedy` to the account owner. Stop retrying |
| `429 too_many_requests` | A rate limit or usage limit was reached | Wait `retryAfterSeconds` or the `Retry-After` header, then continue. Run fewer calls in parallel |
| `409 conflict` on deep research | The account needs a linked GitHub connection for research jobs | The person links GitHub in the app, or contacts Vamo |
| `400` naming a parameter | The parameter or value is not in the spec | Re-read that operation in the spec. Check this skill is current |
| A network error before any status | The request never left the sandbox | [Open network access](#open-network-access) |

Slow is not broken. A search can take ten to twenty seconds. Set the request timeout to at least
sixty seconds and let one call finish before deciding to retry.

---

## Troubleshooting by symptom

| Symptom | Cause | Fix |
| --- | --- | --- |
| The agent asks for the key in every new chat | The sandbox starts empty each conversation | The `vamo-key` skill, or a private Project |
| "I won't write the key to a file" | The agent is being careful with a pasted secret | Tell it you own the key and want it saved privately, then follow the storage steps |
| "Network only allows package registries" | Outbound requests are limited | Allow `api.vamotalent.ai`, new conversation |
| The network setting cannot be found | You are a member, not an owner | Send the owner the one-line request |
| The domain was added and calls still fail | The conversation predates the change, or the setting did not save | New conversation. Ask the owner to confirm the entry is listed. Use the MCP connection meanwhile |
| The agent offers a "rougher pass" with another search | A check failed and it substituted | Fix the failing check. The substitute cannot apply Vamo's filters |
| Works in the terminal, fails in the chat app | They are separate environments with separate settings | Set up the key and the network in each one you use |
| MCP tools do not appear after editing the config | The app was not fully restarted, or the chat is old | Quit completely, reopen, new conversation |
| Very few results | A small default page, or a narrow filter combination | Ask for the number you want and page with the cursor. See `vamo-search` for which filters shrink the pool |
| School or employer filters return almost nobody | Those filters reach only people with a linked professional profile | Search on the work first, then use school or employer to rank. See `role-decomposition` |
| A parameter from an example is rejected | The API moved on | The spec wins. Update the skill |

Presenting on a shared screen: set up the key and run the verification before sharing. Creating
or pasting a key live puts it in the recording.

---

## Using the API well

The companion skills carry the method. In order of use:

- `role-decomposition` turns what a hiring team said into a search spec.
- `vamo-sourcing-agent` runs that spec into a qualified shortlist with an outreach angle.
- `vamo-search` covers choosing filters and reading results.
- `fanout-search` is the general method of covering a topic with many queries.

Habits that matter on any task:

- Describe the work in the query. Put every other requirement in its own filter, read from the
  spec.
- Say how many people you want. Ask for more pages when the first one is good.
- Search wide and light first. Add depth only for the people you keep.
- Confirm a hard requirement by reading the field on each person. A filter is a request.
- Say which checks you ran and what is still unknown.

---

## Staying current

This skill carries a version in its header. The list of current versions is `skills.json` at the
root of the skills repository, with changes described in `CHANGELOG.md`.

Check for a newer version:

- once a week when the skill is in regular use,
- when the API rejects a parameter or a field this skill mentions,
- when the spec and this skill disagree,
- before setting up a new person or a new machine.

Updating means replacing the skill folder with the newer one. In a chat app, upload the new zip
over the old skill. The `vamo-key` skill is separate and is never replaced by an update.
