# Setting up each tool

Reference for the `vamo-setup` skill. One section per tool: how to tell you are in it, the route
to choose, and the exact steps. Products rename their menus often, so each section carries the
date it was checked against the vendor's documentation. If a label has moved, look for the
nearest setting named connectors, MCP, plugins, skills or capabilities.

Two addresses come up everywhere:

- The Vamo MCP server: `https://mcp.vamotalent.ai/mcp/search`
- The skills repository: `vamo-ai/vamo-skills` (`https://github.com/vamo-ai/vamo-skills`)

| Tool | Default route | Skills install | Name a skill |
| --- | --- | --- | --- |
| [Claude Code](#claude-code) | MCP with sign-in | Plugin command | `/vamo:<skill>` |
| [Claude on the web or desktop](#claude-on-the-web-or-desktop) | MCP with sign-in (a connector) | Plugin marketplace, by clicks | Type `/` and pick it |
| [Cursor](#cursor) | MCP with sign-in | One terminal command | Type `/` in Agent chat |
| [Codex](#codex) | MCP with sign-in | One terminal command | `$<skill>` |
| [ChatGPT](#chatgpt) | MCP with sign-in (a custom app) | Workspace admin import, or upload | Type `@` and pick it |
| [Gemini](#gemini) | MCP in Gemini CLI | One terminal command | Automatic, with a prompt to allow it |
| [Any other agent](#any-other-agent) | MCP if it has a connector setting | One terminal command, or hosted pages | By name, or automatic |

Wherever sign-in is not offered or fails, the same tool can use **MCP with a setup code**: the
person copies one line from **Connect a tool** in the Vamo app and pastes it to you. The page the
line names has the steps for Claude Code, Codex, Cursor, Gemini CLI and Claude Desktop. A hosted
chat app has no machine to store a key on, so it has no setup code route.

---

## Claude Code

Checked 2026-10-12. You know you are Claude Code: you run in a terminal and have a Bash tool.

**Connect, with sign-in.** Run:

```sh
claude mcp add --transport http --scope user vamo https://mcp.vamotalent.ai/mcp/search
```

Then the person types `/mcp` in Claude Code, picks `vamo`, and signs in to Vamo in the browser
page that opens. `claude mcp list` shows whether it connects.

- Use `--scope user`, so Vamo works in every project. Never `--scope project`: that writes the
  setup into the repository.
- If a `vamo` server already exists, run `claude mcp list` before changing it. To replace it, run
  `claude mcp remove vamo --scope user` first, then add.
- Never run `claude mcp get vamo` on a server added with a setup code. It prints the key.

**Add the skills.**

```
/plugin install vamo --marketplace vamo-ai/vamo-skills
```

Older versions use two steps: `/plugin marketplace add vamo-ai/vamo-skills`, then
`/plugin install vamo@vamo-skills`. Updates arrive through the marketplace.

**Network.** Open by default. If the person has turned on Claude Code's sandbox, the direct API
needs `api.vamotalent.ai` in the sandbox's allowed domains. The MCP route does not.

**Restart.** New MCP servers and plugins load in the next session.

---

## Claude on the web or desktop

Checked 2026-10-12 against Anthropic's help center. You know you are in a Claude app when you are
chatting in claude.ai or the Claude desktop app, with no terminal of the person's own.

**Connect, with sign-in.** The person does this in the app:

1. **Customize**, then **Connectors**, then **+ Add**, then **Add custom connector**.
2. Name: `Vamo`. URL: `https://mcp.vamotalent.ai/mcp/search`. Choose **Add**.
3. Choose **Connect** and sign in to Vamo in the page that opens.

On a Team or Enterprise workspace, an owner may need to add the connector first, under
**Organization settings**, **Connectors**. Members then choose **Connect** on it. Write the owner
a two-line message with the name and URL. The Free plan allows one custom connector.

**Add the skills.**

1. **Customize**, then **Plugins**, then **Add**, then **Add marketplace**.
2. Enter `vamo-ai/vamo-skills`, then install **vamo**.

Skills need **Code execution and file creation** turned on under **Settings**, **Capabilities**.
On Team and Enterprise an owner controls whether members can add plugins.

**Network.** Claude runs skill code in a sandbox whose network is closed to most hosts. That is
fine: with the connector, the Vamo tools make the calls and the skills supply the method. Only the
direct API from the sandbox needs `api.vamotalent.ai` allowed, and on Team and Enterprise only an
owner can do that, under **Organization settings**, **Capabilities**.

**Setup code route.** The Claude desktop app also reads a local config file, so the setup code
line works there when sign-in does not. Quit the app fully and reopen it afterwards.

**Restart.** Start a new chat after adding a connector or plugin.

---

## Cursor

Checked 2026-10-12 against Cursor's documentation. You know you are Cursor: you run inside the
Cursor editor's Agent chat.

**Connect, with sign-in.** Add Vamo to `~/.cursor/mcp.json` in the home directory, keeping any
servers already there:

```json
{ "mcpServers": { "vamo": { "url": "https://mcp.vamotalent.ai/mcp/search" } } }
```

Then the person opens Cursor's settings, finds Vamo in the MCP section and signs in. Never use a
project's `.cursor/mcp.json` for Vamo: it is shared with the repository.

**Add the skills.** In a terminal (needs Node.js):

```sh
npx skills add vamo-ai/vamo-skills -g -a cursor -y
```

Cursor also reads skills installed for Claude Code (`~/.claude/skills`) and Codex
(`~/.agents/skills`). If the person installed them for one of those, Cursor has them already.

**Network.** Cursor's sandboxed terminal blocks most hosts. Only the direct API needs it opened,
in `~/.cursor/sandbox.json`:

```json
{ "networkPolicy": { "default": "deny", "allow": ["api.vamotalent.ai"] } }
```

**Restart.** Reload the window after adding the server or skills.

---

## Codex

Checked 2026-10-12 against OpenAI's documentation. You know you are Codex: the Codex CLI, its
editor extension, or the ChatGPT desktop app's Codex.

**Connect, with sign-in.** Run:

```sh
codex mcp add vamo --url https://mcp.vamotalent.ai/mcp/search
codex mcp login vamo
```

The login opens a browser page to sign in to Vamo. If Codex asks for a client id, or the login
does not open, use the setup code route.

**Add the skills.** In a terminal (needs Node.js):

```sh
npx skills add vamo-ai/vamo-skills -g -a codex -y
```

They land in `~/.agents/skills`, which Codex reads for every project. Restart Codex if they do
not appear. Run one with `$vamo-search`, or list them with `/skills`.

**Network.** Commands Codex runs have the network off by default. The MCP route does not need
it. The direct API does: in `~/.codex/config.toml`,

```toml
[sandbox_workspace_write]
network_access = true
```

then restart Codex.

---

## ChatGPT

Checked 2026-10-12 against OpenAI's documentation. You know you are ChatGPT: the person is chatting
at chatgpt.com or in the ChatGPT app.

**Connect, with sign-in.** Custom MCP servers need developer mode, on Plus, Pro, Business,
Enterprise and Edu, on the web:

1. **Settings**, then turn on **Developer mode**.
2. **Plugins**, then **+**, then **Add custom MCP server**.
3. Name: `Vamo`. URL: `https://mcp.vamotalent.ai/mcp/search`. Authentication: OAuth.
4. Create it, sign in to Vamo, then type `@` in a new chat and pick Vamo.

On a Business or Enterprise workspace an admin may have to allow custom servers first. Write them
the message.

**Add the skills.** Skills in ChatGPT are for Business, Enterprise and Edu workspaces.

- An admin can add all of them at once: **Admin**, **Plugins**, **Add**, **Import marketplace**,
  with the source `https://github.com/vamo-ai/vamo-skills`.
- A person can upload one skill at a time from **Plugins**, **Skills**, **Create**, using the zips
  from the repository's latest release.

On other plans, skip the skills. Read a skill's hosted page when a task needs it.

**Network.** Assume a chat cannot call the Vamo API directly. Use the Vamo app.

**No sign-in available?** ChatGPT has no setup code route. Offer a coding agent on the person's
own machine instead, such as Codex.

---

## Gemini

Checked 2026-10-12 against Google's documentation.

**Gemini CLI.** You know you are Gemini CLI: you run in a terminal as `gemini`.

```sh
gemini mcp add --transport http vamo https://mcp.vamotalent.ai/mcp/search
```

Then the person types `/mcp auth vamo` in Gemini CLI and signs in. Add the skills with:

```sh
npx skills add vamo-ai/vamo-skills -g -a gemini-cli -y
```

Gemini uses a skill when its description matches the ask, after asking the person to allow it.
`/skills list` shows what is installed. The network is open by default.

**Antigravity CLI.** Personal Google accounts moved from Gemini CLI to Antigravity CLI in June
2026. It reads skills from `.agents/skills` in a workspace, and remote MCP servers from
`~/.gemini/config/mcp_config.json` with a `serverUrl` entry. Its sign-in support for remote
servers was not documented when checked, so use the setup code route if sign-in does not start.

**The Gemini app.** It can hold an uploaded skill, but its scripts cannot reach the internet and
it has no custom connector for Vamo. Searches cannot run there. Suggest Gemini CLI, or another
tool from this list.

---

## Any other agent

- **Connect:** look for a setting named connectors, MCP servers or tools that takes a URL. Add
  `https://mcp.vamotalent.ai/mcp/search` under the name `vamo` and sign in. If it only takes a
  header, use the setup code route.
- **Skills:** `npx skills add vamo-ai/vamo-skills` asks which agent to install for and supports
  most of them. If the agent has no skills folder, read a skill's hosted page when a task needs
  it: `https://vamotalent.ai/skills/<skill>.md`, or on GitHub at
  `https://raw.githubusercontent.com/vamo-ai/vamo-skills/main/skills/<skill>/SKILL.md`.
- **Direct API:** `direct-api.md` covers any agent that can make HTTP requests.
