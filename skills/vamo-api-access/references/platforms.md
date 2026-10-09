# Platform notes

Reference for the `vamo-api-access` skill. The skill's rules are the same everywhere: one private,
lasting place for access, and one allowed host, `api.vamotalent.ai`. This file gives the names
and locations of those two settings in products we have checked. Menu labels change, so each
section carries the date it was checked. If a label has moved, look for the nearest setting about
skills, secrets, sandbox or network.

## Which kind of environment am I in?

An agent can find out by itself:

```bash
# does anything last between sessions? run once, then again in a new session
ls ~/.config/vamo 2>/dev/null || echo "nothing saved here"

# can I reach the API host? no access needed
curl -s -m 20 -o /dev/null -w '%{http_code}\n' https://api.vamotalent.ai/openapi.json
```

A home directory that keeps files between sessions is a machine of your own. One that comes back
empty is a sandbox. `200` means the network path is open. Anything else, or no answer, means the
host needs allowing.

## Any terminal or editor coding agent on your own machine

- **Access:** `~/.config/vamo/env` holding `VAMO_API_KEY=...`, file mode `600`, loaded at the
  start of a session. An operating system keychain or a secrets manager is equally good.
- **Network:** usually open. If the agent runs commands inside a network sandbox, add
  `api.vamotalent.ai` to that sandbox's allowed hosts in the agent's settings.
- **Skills:** copy each skill folder into the directory your agent reads skills from. Agents
  that have no skills directory can be pointed at the hosted markdown page for a skill and told
  to follow it.

## Hosted and cloud coding agents

These run in a fresh container per task.

- **Access:** an environment secret named `VAMO_API_KEY`, set in the environment's or workspace's
  secret settings.
- **Network:** the environment has a network or internet access setting, often with levels such
  as none, package registries only, a custom allowlist, or all. Choose the custom allowlist and
  add `api.vamotalent.ai`.

## Claude on the web and desktop apps

Checked 2026-10-09 against Anthropic's help center.

- **Sandbox:** code runs in a sandbox that starts empty in each conversation.
- **The Vamo skills:** **Customize**, **Plugins**, **Add**, **Add marketplace**, enter
  `vamo-ai/vamo-skills`, and install **vamo**. Updates sync from the repository.
- **Personal skills** (for your private `vamo-access` skill): **Customize**,
  **Skills**, **+**, **Create skill**, **Upload a skill**, then upload a zip with the skill
  folder at its top level. Skills need **Code execution and file creation** turned on under
  **Settings**, **Capabilities**. On Team and Enterprise workspaces an owner can turn off
  user-created skills. If the upload option is missing, ask an owner.
- **Network, individual plans:** **Settings**, **Capabilities**. Turn on **Allow network
  egress** and add `api.vamotalent.ai` to the allowed domains. You control this yourself.
- **Network, Team and Enterprise:** only an organization owner can change it, under
  **Organization settings**, **Capabilities**. The option to choose allows package managers and
  specific domains. Add `api.vamotalent.ai`.
- **MCP connectors** keep working whatever the network setting is, which makes the Vamo MCP
  server the fallback while an owner is being asked.
- Start a new conversation after any of these change.

## Claude Code

Checked 2026-10-09.

- **Access:** it runs on your machine, so use `~/.config/vamo/env` as above.
- **Skills:** `/plugin install vamo --marketplace vamo-ai/vamo-skills`, then invoke a skill as
  `/vamo:<skill>`. Update with `/plugin marketplace update vamo-skills`. Copying a skill folder
  into `~/.claude/skills/` or a project's `.claude/skills/` also works.

## A platform not listed here

Ask the two questions the skill is built on. Where can one account keep a private value that is
still there next session? Where is the list of hosts the agent may reach? Put `VAMO_API_KEY` in
the first and `api.vamotalent.ai` in the second, then run the verification in the skill.
