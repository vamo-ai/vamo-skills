---
name: vamo-troubleshooting
description: Use when Vamo is set up and something fails, or when a person asks whether Vamo is connected, and the agent should find the cause by itself. Covers working out which route is in use (the Vamo MCP tools, or the Developer API over HTTP with a key), three checks in order, what every API error means and what to tell the person, the MCP cases (tools missing or signed out, "This Vamo account cannot run that right now", an expired read_more page), and what to pass on to Vamo when it cannot be fixed. Works in any agent. Symptoms include 400, 401, 402, 403, 404, 409, 422, 429 and 5xx responses, unauthorized, forbidden, too_many_requests, Vamo tools that do not show up, a search that worked before and fails now, and a setup code that was refused. Triggers "check my Vamo connection", "is Vamo connected", "Vamo isn't working", "Vamo stopped working", "why did that Vamo call fail", "what does this Vamo error mean", "debug Vamo".
metadata:
  version: "1.2.0"
  updated: "2026-10-14"
---

# Vamo troubleshooting

Use this when a Vamo call fails, or when a person asks whether Vamo is connected. You find the
cause yourself. Then you tell the person in plain words what is wrong and who can fix it.

Work in this order.

1. [Find the route in use](#find-the-route-in-use).
2. [Run the three checks](#run-the-three-checks). Stop at the first one that fails.
3. [Read the error](#read-the-error), or find the [MCP case](#mcp-cases).
4. Tell the person what is wrong, in one or two sentences, and what happens next.
5. When you cannot fix it, give them [what to pass on to Vamo](#what-to-pass-on-to-vamo).

The [rules](#rules) apply at every step. Read them before you run anything.

---

## Find the route in use

An agent reaches Vamo in one of two ways. Each fails differently, so name yours first.

| Route | You are on it when | Who holds the credential |
| --- | --- | --- |
| Vamo MCP tools | Your tool list has `search_docs`, `search_execute` and `read_more` | The AI tool. It signed in through a browser, or it sends an API key in a header. You never see either |
| Developer API over HTTP | You make the requests yourself, to `api.vamotalent.ai` | You hold an API key, usually in `VAMO_API_KEY` |

A skill that calls Vamo uses the HTTP route. So does a key that arrived through a setup code.

Some agents have both routes. Check the one the failing call used, and say which one you checked.
A working route does not prove the other one works.

---

## Run the three checks

Run them in order. Each one only means something once the one before it passes.

| Check | Developer API over HTTP | Vamo MCP tools |
| --- | --- | --- |
| 1. Vamo is reachable | `GET https://api.vamotalent.ai/openapi.json` returns JSON. It needs no key | The three Vamo tools are in your tool list, and `search_docs` answers |
| 2. A credential is present | `VAMO_API_KEY` is set, or the saved access file is found. Confirm it by its length | The tool holds it. A call that answers `401`, or a prompt to sign in, means it is missing |
| 3. One call succeeds | `GET /v1/me` with the key answers. Then one `POST /v2/developers/search` with `"limit": 1` answers | One `search_execute` that asks for a single result answers |

What each check tells you:

- **Check 1 fails over HTTP.** The request never left your environment. No status came back.
  `vamo-api-access` covers opening the network path.
- **Check 1 fails with the MCP tools.** The tool is not connected. See [MCP cases](#mcp-cases).
- **Check 2 fails over HTTP.** Look in the environment, then in `~/.config/vamo/env`.
  `vamo-api-access` covers getting access and keeping it between sessions.
- **Check 3 fails.** You have a status and a `code`. [Read the error](#read-the-error).

`GET /v1/me` is the connection test for the HTTP route. It works with any key. It returns the
account, the key's label, the plan and the key's permissions. It is not offered through the MCP
tools.

The one search for check 3:

```bash
curl -s -m 60 -X POST https://api.vamotalent.ai/v2/developers/search \
  -H "Authorization: Bearer $VAMO_API_KEY" -H "content-type: application/json" \
  -d '{"rank_by": ["v", "ANN", ["Embed", "rust database engine"]], "limit": 1}'
```

**A `404` or `503` from a `/v2/developers` route on production is not a broken connection.** The
v2 engine is not switched on for that host yet. Run the same check on the v1 route
(`GET /v1/developers/search?q=rust+database+engine&limit=1`). When v1 answers, the connection is
fine: say in one line that searches run on v1 for now, and carry on there.

Before a search, read the fields it may use at `GET /v2/developers/fields`, and check a body you
are unsure of with `POST /v2/developers/search/validate`. The API wins over
this file.

Slow is not broken. A search can take ten to twenty seconds. Allow sixty seconds, and let one
call finish before you decide it failed.

When all three pass, say so in one sentence for each check. Then ask the person what they saw.
The connection is fine, so the problem is in the request. `vamo-search` covers thin results.

A setup code that is refused is a separate case. A code works once and lasts ten minutes. Ask the
person for a fresh line from **Connect a tool** in the Vamo app. Never send the same code twice.

---

## Read the error

Every error body has a stable `code`, a `message` and the `status`. Many carry more detail. Read
the whole body, because the detail says which case it is. Every response also has an
`x-request-id` header. Keep it.

| Status and `code` | What it means | Detail to read | What to tell the person |
| --- | --- | --- | --- |
| `400 bad_request` | The request is malformed | `validation.issues[]`, each with a `path` and a `message` | Nothing yet. Fix the call from the spec and run it again |
| `400` with `ok: false`, `error` and `hint` | A `/v2/developers` search body is wrong: an unknown or disabled field, an unknown place, company or repository, a guard (lanes, limit) | `hint` says what to change, and names the closest known value | Nothing yet. Apply the hint. `POST /v2/developers/search/validate` checks the fix without running it |
| `401 unauthorized` | No key reached Vamo, or the key is wrong or revoked | None | "Vamo did not accept this key. It may have been revoked. Please create a new one on the API keys page in the Vamo app." Check the header yourself first |
| `401 signature_required` | This key is set to require signed requests | None | "This key only accepts signed requests, and this call was not signed. Whoever created the key decides how it is used." |
| `402 payment_required` | The plan does not include this, the account cannot cover it, or a quota is reached | `entitlement` and `plan`, or `reason`, or `quota` | "This Vamo account cannot run that right now. The account owner can sort it out under Billing in the Vamo app." Stop retrying |
| `403 forbidden` | The key or the person's role lacks a permission, or a feature is off | `entitlement` names the missing permission. Otherwise `reason` | Name the permission. "The key's owner can add it on the API keys page." With `reason`, say which feature is off for the account |
| `404 not_found` | No such route or record | None | Check the path against the spec first. On a `/v2/developers` route on production, the v2 engine is not on yet: use the v1 route and say so in one line. Otherwise say which record Vamo could not find |
| `409` with `reason: GITHUB_CONNECTION_REQUIRED` | Deep research needs a GitHub account connected for the member the key acts for | `instruction`, `connectUrl`, and `action` when present | Give the person `instruction` and `connectUrl` as they are. They open the link in any browser and approve on GitHub. No Vamo sign-in is needed. Wait until they say it is done, then send the same request again. The link works for 15 minutes and connects one account: if it ran out, the next refusal carries a new one. With `action`, `GET /v1/actions/{id}` reads `completed` once they are connected. No `connectUrl` means there is no one to connect for: say what `message` says |
| `409 conflict` | The request conflicts with the current state | `message`, and anything else in the body | Say what `message` says. Do not send the same request again unchanged |
| `422 unprocessable_entity` | The request is well formed, and Vamo cannot process it | `message`, and anything else in the body | Say what `message` says. Change the input before you try again |
| `429 too_many_requests` | A rate limit, a quota, or a cap the account owner set | `retryAfterSeconds` and the `Retry-After` header. Otherwise `quota` or `reason` | With a wait, nothing. Wait that long, then continue with fewer calls at once. With `quota` or `reason`: "This account reached a limit. The owner can see it on the Usage page in the Vamo app." |
| `503` on a `/v2/developers` route | The v2 engine is not available on this host | `Retry-After` | Use the v1 route of the same name and say in one line that the call ran on v1 |
| `5xx internal_error` | Vamo failed | None. Keep the request ID | "Vamo had a problem on its side." Try once more after a short wait. Then pass it on |
| No status at all | The request never left your environment | The error your HTTP client printed | "This environment cannot reach Vamo yet." `vamo-api-access` covers the fix |
| Any other status or `code` | Read `code` and `message` | The whole body | Say what `message` says, and pass it on if it is unclear |

Notes on reading them:

- **`401`.** Check the header before you tell anyone. It is `Authorization: Bearer <key>`, with no
  quotes, line breaks or spaces inside the key. A key cannot be shown again or rotated. The
  person creates a new one and revokes the old one. A read-only member cannot create keys.
- **`403` on something the app does.** An API key reaches search, research, ranking, lists and
  contacts. Projects, outreach, members, billing and key management are done in the Vamo app.
  Tell the person that, and stop.
- **A body with an `action`.** Some steps only the person can take, such as connecting GitHub.
  The refused call then carries `action.url`. Give them that link and say what it is for. Run
  the call again when they say it is done.
- **`429`.** A key can read the account's quotas. The spec lists the operation.
- **Stop on `401`, `402` and `403`.** The same call gives the same answer until a person changes
  something.

---

## MCP cases

With the MCP tools, the AI tool holds the credential and makes the connection. You see less. You
cannot see the request ID. You cannot read account, usage or billing information.

| What you see | What it means | What to tell the person |
| --- | --- | --- |
| The Vamo tools are missing from your tool list | The tool is not connected, or this session began before it was | "Vamo is not connected in this tool. Open **Connect a tool** in the Vamo app and follow the steps for this tool. Then start a new session." |
| A call answers `401`, or the tool asks to sign in | The sign-in ended or was removed, or the key in the tool was revoked | "Vamo needs you to connect again. Open **Connect a tool** in the Vamo app." |
| `This Vamo account cannot run that right now. The account owner can sort it out under Billing in the Vamo app.` | The account cannot run it for a plan or billing reason. The server does not say which | Say that sentence as written. Do not guess the reason. Stop retrying |
| `read_more` says there are no pages for that token | The page expired. Pages are kept for a short time | Nothing. Run the search again and read the new pages straight away |
| A refused call carries an `action` with a `url` | A step only the person can take | Give them the link and say what it is for. Run the call again when they say it is done |
| Any other refused call | It carries the same `status` and `code` as the API | Use the table in [Read the error](#read-the-error) |

What is behind the first two rows:

- A tool that signed in stays connected while it is used. After 90 days without use it signs in
  again.
- Connecting needs a plan that includes API keys. On other plans the API keys page says so.
- Tools appear in sessions that start after the tool is connected. A session that was already
  open does not get them.
- The page that lists API keys also lists **Connected tools**. The person can see there whether
  this tool is still connected, and who approved it.
- A connection can be limited to fewer permissions than the task needs. That reads as `403`.

Results are paged, never cut. To get less back, filter inside the code you run.

---

## What to pass on to Vamo

When the checks and the tables do not settle it, stop. Give the person a short report they can
send. They send it with **Feedback** in the Vamo app's user menu.

Put in it:

- **The tool.** The name of the AI tool or agent, and its version if you know it.
- **The route.** The MCP tools, or the Developer API over HTTP.
- **The time** of the failing call, with the time zone.
- **The visible message.** The status, the `code` and the `message`, or the text the tool showed,
  word for word.
- **The request ID,** on the HTTP route. It is the `x-request-id` response header. On the MCP
  route there is none to give, so say that. Never make one up.
- **Which checks passed,** and what you tried.

Never put the key in it. That covers any part of the key and the `Authorization` header. The
key's label from `GET /v1/me` is safe to include, and it tells Vamo which key it was.

---

## Rules

- **Never print a key.** Read it into a variable. Confirm it by its length. Keep it out of
  replies, logs, URLs and file names.
- **Never ask for a key in the chat.** When no access is found, `vamo-api-access` says how the
  person provides it safely.
- **Never install software or change a setting without asking.** Say what you want to change and
  why, then wait for a yes. That includes config files, network settings and stored access.
- **Never suggest a personal account to get around company controls.** When an admin controls
  the setting, the admin is the fix. Give the person one line they can send to that admin.
- **Never switch to another data source without saying so.** A general web or GitHub search
  answers a different question. Say which check failed.
- **Say what you could not verify.** A guess about someone's plan, billing or permissions sends
  them to the wrong person.
- **Keep the mechanics short.** Tell the person what is wrong and what to do. Leave raw error
  bodies out unless they ask.

---

## Staying current

This skill carries a version in its header. `skills.json` at the root of the skills repository
lists every current version. `CHANGELOG.md` says what changed. Check for a newer version when an
error here does not match what the API returns. The spec wins.
