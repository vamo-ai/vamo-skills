---
name: vamo-api-access
description: Use when an agent needs access to the Vamo Developer API over HTTP: first-time setup, a setup code to trade for a key, or a call that fails before it returns results. Covers getting API access (a one-time setup code that starts with vamo_xc_, or a key a person created), storing it so the next session still has it on macOS, Linux and Windows, opening network access to the API host, verifying the connection, and reading error responses. Works with any coding agent or chat assistant that can make HTTP requests. Symptoms include "no Vamo API key in this workspace", being asked for access again in every new session, "this workspace's network only allows package registries", a blocked or timed-out request to api.vamotalent.ai, and 401, 403, 402 or 429 responses. Triggers "set up Vamo", "connect to the Vamo API", "here is my Vamo setup code", "connect a tool", "Vamo access isn't working", "allowlist Vamo", "how do I call Vamo".
metadata:
  version: "1.2.0"
  updated: "2026-10-09"
---

# Vamo API access

Vamo searches GitHub developers by what they have built. This skill gets a direct HTTP
connection working and keeps it working in any agent: API access, a safe place to keep it, a
network path to the API, and what to do when a call fails.

Three things have to be true before any search runs. Check them in this order at the start of a
session and fix the first one that fails.

| Check | Test | If it fails |
| --- | --- | --- |
| The network reaches Vamo | `GET https://api.vamotalent.ai/openapi.json` returns JSON. No key needed | [Open network access](#open-network-access) |
| Access is available | The person's message carries a setup code, `VAMO_API_KEY` is set, or a saved access file is found | [Get access](#get-access), then [Store it](#store-access-so-it-persists) |
| Access works | One small search returns results | [Read the error](#read-the-error) |

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

## Get access

Access is an API key that starts with `vamo_sk_`. It reaches the agent in one of two ways, and the
right one depends on where the agent runs.

| The agent runs | How access arrives |
| --- | --- |
| On your own machine, with a lasting filesystem | A **setup code**. The Vamo app gives one line to paste, and the agent trades the code in it for a key and stores the key by itself. Nobody copies a key |
| In a sandbox that starts empty each session | A key a person creates in the Vamo app and places in the platform's private store |

Both come with a plan that includes API keys. On any other plan the account owner changes the plan
or contacts Vamo.

### With a setup code

A person does this in a browser, once for each tool on each machine.

1. Sign in at `https://app.vamotalent.ai`.
2. Open **Connect a tool** and pick the tool the agent runs in. Direct link:
   `https://app.vamotalent.ai/settings/mcp`.
3. Paste the line it gives into the agent. The line carries a setup code that starts with
   `vamo_xc_`.

A setup code works once and lasts ten minutes. Asking for a new one cancels the one before it. The
agent trades it for a key with one request, which needs no key of its own:

- `POST https://api.vamotalent.ai/v1/keys/exchange` with the JSON body
  `{"code": "<the code>", "device": "<this machine's hostname>"}`.
- A success carries `key`, `label`, `permissions`, `apiBaseUrl` and `mcpUrl`. `key` is the API
  key, and this is the only time it is returned. `label` names the tool and the machine, which is
  how the key is listed in the app.
- Every failure is the same `404`: the code was used, has expired or was cancelled by a newer one.
  Ask the person for a fresh line. Never send the same code twice.

This one route is left out of `openapi.json` on purpose. This skill is where it is described.

**The key goes from the response straight into the private file. It is never shown.** Run the block
for your system in `references/setup-code.md` exactly as written. It sends the code, writes the key
where [Store access](#store-access-so-it-persists) says it lives, and prints only the label, the
permissions and two addresses. Never make the request in a way that prints the response, and never
ask the person to read out or paste a key.

The line usually names a hosted page with the same steps. Exchange the code once: by following that
page, or with the block here, never both.

Use a setup code only where the home directory lasts between sessions. In a sandbox that starts
empty the stored key is gone when the session ends.

### With a key a person creates

For a sandbox that starts empty. A person does this once, in a browser.

1. Sign in at `https://app.vamotalent.ai`.
2. Open **Settings**, then **API Keys** (under Integrations). Direct link:
   `https://app.vamotalent.ai/settings/api-keys`.
3. Choose **Create key**. Give it a name that says who or what uses it, such as "Sam's laptop".
4. Under **Permissions**, set **Search** to **Read**. That is enough to search, enrich, find
   similar developers, get summaries and get email addresses.
5. Choose **Create key** and copy the secret into the platform's private store. It starts with
   `vamo_sk_` and is shown once.

Notes on permissions:

- Read and Write here are levels of access to one area. Set only what the work needs. A key can
  be changed later with **Edit permissions**, and the change applies to the next request.
- **Search: Write** adds reading saved deep-research reports and managing saved searches.
- Starting a deep-research job, and scoring people against a role, each need their own row in the
  picker. Those rows appear only on accounts that have the feature. The spec names the exact
  requirement for every operation under `x-vamo.entitlement`.

A lost key cannot be shown again. Get a fresh setup line, or create a new key, and **Revoke** the
old one. One key per person or per agent keeps a revoke from breaking anyone else.

---

## Store access so it persists

The API key is the account's access to Vamo. It should live in one private place that the agent
can read by itself in every session. It should never live in a chat message, in a file that gets
shared or committed, or on a screen someone else is watching.

Agents run in two kinds of environment, and the right place differs.

| The agent runs | Examples | Where access lives |
| --- | --- | --- |
| On your own machine, with a lasting filesystem | Terminal and editor coding agents | A private file in your home directory, or the operating system keychain |
| In a sandbox that starts empty each session | Chat assistants with a code sandbox, hosted and cloud agents | The platform's private, lasting store for your account: a personal skill, a private project, or an environment secret |

A sandbox that starts empty is why an agent asks for access again in every new session. Saving a
file "in the workspace" there lasts only for that conversation.

### On your own machine

The key lives in one private file per user. The format is the same on every system, so one reader
works everywhere.

| System | File | Kept private by |
| --- | --- | --- |
| macOS and Linux | `~/.config/vamo/env` | Directory mode `700`, file mode `600` |
| Windows | `%USERPROFILE%\.config\vamo\env` | Inheritance removed and access granted to your account only, with `icacls` |

The file holds one line, `VAMO_API_KEY=...`, ending in a single newline with no byte order mark.
A setup code exchange writes it for you. To save a key you created yourself, type it into your own
terminal, never into a chat: `references/platforms.md` has the block for each system.

Any agent on that machine loads it at the start of a session. Each form is an assignment, so
nothing is printed.

macOS and Linux:

```bash
set -a; . ~/.config/vamo/env; set +a
```

Windows, in PowerShell:

```powershell
$line = Get-Content (Join-Path $env:USERPROFILE '.config\vamo\env') | Where-Object { $_ -like 'VAMO_API_KEY=*' } | Select-Object -First 1
$env:VAMO_API_KEY = "$line" -replace '^VAMO_API_KEY=', ''
```

An operating system keychain or a secrets manager works the same way: store the value once and
have the agent read it into `VAMO_API_KEY`. Keep the key out of project `.env` files, shell
profiles and repositories.

### In a sandbox that starts empty

Use whatever the platform offers for private, lasting, per-account data. In order of preference:

1. **An environment secret**, where the platform has them. Name it `VAMO_API_KEY`. The agent sees
   it as an environment variable and nothing else is needed.
2. **A private access skill**, where the platform supports personal skills. It is a folder named
   `vamo-access` with two files, uploaded once to your own account.

   `SKILL.md`:

   ```markdown
   ---
   name: vamo-access
   description: Use whenever a task calls the Vamo API. Provides this account's Vamo API access.
   ---

   Access is in `vamo.env` beside this file, as `VAMO_API_KEY`. Load it into the environment
   before calling the API. Never print it, quote it, or copy it into another file.
   ```

   `vamo.env`:

   ```
   VAMO_API_KEY=<paste the value here>
   ```

   Compress the folder with the folder itself at the top level of the zip, upload it as a
   personal skill, then delete the zip and the folder from your computer.
3. **A private project's instructions**, used only for Vamo work and shared with nobody.

Whichever you use, it is yours alone. Never share the zip, and never add `vamo-access` to a
shared or public skills repository.

`references/platforms.md` has the exact menu paths for the products we have checked.

### Rules for the agent

- Look before asking, in this order on every system:
  1. A setup code in the person's message. Exchange it, then load the file. The key it returns
     replaces whatever was stored or set before.
  2. The `VAMO_API_KEY` environment variable. `VAMO_KEY` is an accepted older name.
  3. The private file: `~/.config/vamo/env`, or `%USERPROFILE%\.config\vamo\env` on Windows.
  4. A `vamo.env` in an installed `vamo-access` skill.
  5. `.env` in the working directory.
- Send it only as a header to `api.vamotalent.ai`: `Authorization: Bearer $VAMO_API_KEY`. Never
  put it in a URL, a filename, a log line or a reply.
- Never print it. Read a file into a variable, never onto the screen, and confirm access is
  present by its length.
- When nothing is found, work out which kind of environment you are in. On the person's own
  machine, ask for a setup line: "Open Connect a tool in the Vamo app, pick this tool, and paste the
  line it gives you here." In a sandbox that starts empty, give the storage steps above. Never ask
  for the key itself.
- When a person pastes it into the chat anyway, use it for the task, then offer to prepare the
  `vamo-access` folder or the env file so the next session has it. Saving access to a private
  place at the owner's request is the intended setup.
- Access that has appeared in a shared chat, a screen share or a recording should be revoked and
  replaced.

---

## Open network access

Many agent environments restrict outbound requests by default. The usual signs: a message that
the workspace network "only allows package registries", or a request to `api.vamotalent.ai` that
fails with a proxy error or a timeout while package installs work.

**One host needs to be allowed: `api.vamotalent.ai`, over HTTPS.** The API, its spec and its docs
are all served from it. Allow that single host. Opening all domains is unnecessary and widens
what a sandbox can send out.

Every environment that restricts the network has a setting for allowed hosts. What differs is the
name of the setting and who is permitted to change it.

| Who administers the environment | What to do |
| --- | --- |
| You (a personal account, your own machine) | Find the agent's network or sandbox setting and add `api.vamotalent.ai` to its allowed hosts |
| A workspace or organization admin | You cannot change it yourself. Send the admin one line: *"Please add api.vamotalent.ai to the allowed domains for the agent's code execution environment."* |
| IT (a company proxy or firewall) | Ask for outbound HTTPS to `api.vamotalent.ai` |

After the setting changes, start a new session. A running session keeps the network rules it
started with.

`references/platforms.md` gives the setting's name and location for the products we have checked.

Other hosts, only if you use them:

| Host | Used for |
| --- | --- |
| `app.vamotalent.ai` | Connect a tool and API keys, in a browser. The agent never calls it |
| `vamotalent.ai` | Reading these skills and the setup prompts as hosted pages |
| `mcp.vamotalent.ai` | The Vamo MCP server, when connected as a tool |

### When network access cannot be opened

Connect Vamo as an MCP server. On most platforms, connector traffic is governed separately from
the sandbox's network rules, so it works when direct calls are blocked. It exposes a smaller set
of operations than the API. Setup is one line to the agent:

```
Fetch https://vamotalent.ai/agent-setup/search/prompt.md and follow the instructions
```

Things that go wrong when editing an app's connector config by hand:

- Give the agent the whole current config file and ask for the whole new file back. Pasting a
  fragment in by hand is how braces get doubled.
- Replace only the placeholder with your value. Keep the word `Bearer` and the space after it.
- Save the file, quit the app completely, reopen it, and start a new session. Tools added to the
  config appear only in sessions started after the restart.

---

## Verify the connection

```bash
# 1. network: prints the API title
curl -s -m 20 https://api.vamotalent.ai/openapi.json | jq -r .info.title

# 2. access present: prints the length, never the value
[ -n "$VAMO_API_KEY" ] && echo "access loaded (${#VAMO_API_KEY} chars)" || echo "no access found"

# 3. access works: prints one login
curl -s -m 60 -G https://api.vamotalent.ai/v1/developers/search \
  -H "Authorization: Bearer $VAMO_API_KEY" \
  --data-urlencode "q=rust database engine" --data-urlencode "limit=1" \
  | jq -r '.results[0].login // .'
```

On Windows, `references/platforms.md` has the same three checks in PowerShell.

Report the outcome of each check in a sentence. When all three pass, say so and ask what the
person is looking for.

---

## Read the error

Every error body has a stable `code` and a `message`. Many carry more: `reason`, `entitlement`,
`remedy`, `retryAfterSeconds`. Read the whole body. The extra fields say which case it is.

| Status and `code` | What it means | What to do |
| --- | --- | --- |
| `401 unauthorized` | No key reached the API, or the key is wrong or revoked | Check the header is `Authorization: Bearer <key>` with no quotes, line breaks or spaces inside the key. Get a fresh setup line, or create a new key, if this one was revoked |
| `404` from `/v1/keys/exchange` | The setup code was used, has expired or was cancelled by a newer one | Ask the person for a fresh line from **Connect a tool**. Never send the same code again |
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
| The agent asks for access in every new session | The sandbox starts empty each session | An environment secret, the `vamo-access` skill, or a private project |
| The agent asks you to paste a key | It found no stored access | On your own machine, give it a setup line from **Connect a tool** instead |
| The setup code is refused | It was used, ten minutes passed, or a newer code cancelled it | Press the button in **Connect a tool** again and paste the new line |
| `curl` behaves differently in PowerShell | In Windows PowerShell, `curl` is another command | Call `curl.exe`, or use the PowerShell forms in `references/platforms.md` |
| "I won't write that to a file" | The agent is being careful with a pasted secret | Tell it the access is yours and you want it saved privately, then follow the storage steps |
| "Network only allows package registries" | Outbound requests are limited | Allow `api.vamotalent.ai`, new session |
| The network setting cannot be found | An admin controls it | Send the admin the one-line request |
| The host was added and calls still fail | The session predates the change, or the setting did not save | New session. Ask the admin to confirm the entry is listed. Use the MCP connection meanwhile |
| The agent offers a "rougher pass" with another search | A check failed and it substituted | Fix the failing check. The substitute cannot apply Vamo's filters |
| Works in one agent, fails in another | They are separate environments with separate settings | Set up access and the network in each one you use |
| MCP tools do not appear after editing the config | The app was not fully restarted, or the session is old | Quit completely, reopen, new session |
| Very few results | A small default page, or a narrow filter combination | Ask for the number you want and page with the cursor. See `vamo-search` for which filters shrink the pool |
| School or employer filters return almost nobody | Those filters reach only people with a linked professional profile | Search on the work first, then use school or employer to rank. See `role-decomposition` |
| A parameter from an example is rejected | The API moved on | The spec wins. Update the skill |

Presenting on a shared screen: set up access and run the verification before sharing. Creating
or pasting an API key live puts it in the recording.

---

## Using the API well

The companion skills carry the method. In order of use:

- `role-decomposition` turns what a hiring team said into a search spec.
- `vamo-search` runs the search: choosing filters, covering a role with many angles, reading and
  qualifying results.
- `vamo-enrich` starts from people you already have: a strength read, location, contact details,
  a research report.
- `vamo-workflows` makes any of it repeatable: your own agents, recurring searches, hand-offs to
  other tools.
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

Updating means replacing the skill folder with the newer one, or uploading the new zip over the
old skill. Your private `vamo-access` skill is separate and is never replaced by an update.
