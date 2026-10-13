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

The same two questions on Windows, in PowerShell:

```powershell
Test-Path (Join-Path $env:USERPROFILE '.config\vamo')
(Invoke-WebRequest -UseBasicParsing -Uri https://api.vamotalent.ai/openapi.json -TimeoutSec 20).StatusCode
```

A home directory that keeps files between sessions is a machine of your own. One that comes back
empty is a sandbox. `200` means the network path is open. Anything else, or no answer, means the
host needs allowing.

## Any terminal or editor coding agent on your own machine

- **Access:** a setup code from **Connect a tool** in the Vamo app, traded for a key with the
  block in `setup-code.md`. The key lands in `~/.config/vamo/env` holding `VAMO_API_KEY=...`, file
  mode `600`, and is loaded at the start of a session. On Windows the file is
  `%USERPROFILE%\.config\vamo\env`. An operating system keychain or a secrets manager is equally
  good.
- **Network:** usually open. If the agent runs commands inside a network sandbox, add
  `api.vamotalent.ai` to that sandbox's allowed hosts in the agent's settings.
- **Skills:** copy each skill folder into the directory your agent reads skills from. Agents
  that have no skills directory can be pointed at the hosted markdown page for a skill and told
  to follow it.

## Windows

Checked 2026-10-09 against Microsoft's documentation for `icacls` and for the file and web
commands. Everything here is PowerShell, written for Windows PowerShell 5.1 and PowerShell 7.

- **Where access lives:** `%USERPROFILE%\.config\vamo\env`, one line, `VAMO_API_KEY=...`. It is
  the same format as on macOS and Linux: a single newline at the end and no byte order mark. A
  bash shell on Windows whose home directory is your user profile reads it as `~/.config/vamo/env`.
- **Who can read it:** your account only. The setup code block removes inherited permissions from
  the folder and the file and grants your account alone, with `icacls`. To check, run
  `icacls (Join-Path $env:USERPROFILE '.config\vamo\env')`: it lists one account.
- **Loading it, without showing it:**

  ```powershell
  $line = Get-Content (Join-Path $env:USERPROFILE '.config\vamo\env') | Where-Object { $_ -like 'VAMO_API_KEY=*' } | Select-Object -First 1
  $env:VAMO_API_KEY = "$line" -replace '^VAMO_API_KEY=', ''
  ```

- **`curl`:** in Windows PowerShell, `curl` is a different command. Call `curl.exe` to get the one
  the examples use, or use `Invoke-RestMethod`, which reads the JSON for you.
- **Two helpers**, the same as the ones in `curl-trainer.md`:

  ```powershell
  function vamo($path) { Invoke-RestMethod -Uri "https://api.vamotalent.ai$path" -Headers @{ Authorization = "Bearer $env:VAMO_API_KEY" } -TimeoutSec 60 }
  function vamoPost($path, $json) { Invoke-RestMethod -Method Post -Uri "https://api.vamotalent.ai$path" -Headers @{ Authorization = "Bearer $env:VAMO_API_KEY" } -ContentType 'application/json' -Body $json -TimeoutSec 60 }
  ```

- **The three checks** from the skill:

  ```powershell
  # 1. network: prints the API title
  (Invoke-RestMethod -Uri https://api.vamotalent.ai/openapi.json -TimeoutSec 20).info.title

  # 2. access present: prints the length, never the value
  if ($env:VAMO_API_KEY) { "access loaded ($($env:VAMO_API_KEY.Length) chars)" } else { 'no access found' }

  # 3. access works: prints one login
  (Invoke-RestMethod -Uri 'https://api.vamotalent.ai/v1/developers/search?q=rust+database+engine&limit=1' -Headers @{ Authorization = "Bearer $env:VAMO_API_KEY" } -TimeoutSec 60).results[0].login
  ```

## Saving a key you created yourself

A setup code is the usual way in on your own machine, and it needs none of this. If you hold a key
you created in the app, type it into your own terminal window, never into a chat.

macOS and Linux:

```bash
mkdir -p ~/.config/vamo && chmod 700 ~/.config/vamo
printf 'Paste your Vamo API key, then press Enter: ' && read -rs K \
  && printf 'VAMO_API_KEY=%s\n' "$K" > ~/.config/vamo/env \
  && chmod 600 ~/.config/vamo/env && unset K && echo ' saved'
```

Windows, in PowerShell:

```powershell
& {
  $ErrorActionPreference = 'Stop'
  $dir = Join-Path $env:USERPROFILE '.config\vamo'
  $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  icacls $dir /inheritance:r /grant:r "*${sid}:(OI)(CI)F" | Out-Null
  $secure = Read-Host -AsSecureString 'Paste your Vamo API key, then press Enter'
  $key = (New-Object System.Net.NetworkCredential('', $secure)).Password
  [IO.File]::WriteAllText((Join-Path $dir 'env'), "VAMO_API_KEY=$key`n")
  icacls (Join-Path $dir 'env') /inheritance:r /grant:r "*${sid}:F" | Out-Null
  'saved'
}
```

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

## OpenAI Codex

Checked 2026-10-09 against OpenAI's documentation.

- **Skills:** Codex reads skills from `~/.agents/skills/` for every project, or from
  `.agents/skills/` inside a repository. Copy the folders under `skills/` there. Run one with
  `/skills`, or by typing `$` and its name, such as `$vamo-api-access`. Codex in the terminal, the
  editor extension and the ChatGPT desktop app all read the same folders.
- **Access, on your own machine:** `~/.config/vamo/env` as above.
- **Network, on your own machine:** commands run in a sandbox with the network off by default.
  The setting is `network_access = true` under `[sandbox_workspace_write]` in
  `~/.codex/config.toml`. It opens the network for commands as a whole. Restart Codex after
  editing the file.
- **Codex cloud:** each task runs in a fresh container with internet access off once setup
  finishes. In the environment's settings, turn on agent internet access with a domain allowlist
  and add `api.vamotalent.ai`. Give the environment `VAMO_API_KEY` as an environment variable, or
  as a network secret limited to `api.vamotalent.ai` where that option is offered. A plain secret
  is available to setup scripts only and is gone by the time the agent runs.

## ChatGPT

Checked 2026-10-09 against OpenAI's documentation.

- **Skills:** in beta and switched on per workspace by its owners. Where they are on, a skill
  built elsewhere can be uploaded, and you run one by typing `@` and picking it. Each release of
  the skills repository carries one zip per skill.
- **Without Skills:** tell ChatGPT to read a skill's hosted page and follow it.
- **Calling the API:** a chat reaches outside services through the tools and apps the workspace
  has connected. If a chat cannot reach `api.vamotalent.ai` directly, connect the Vamo MCP server
  as an app and use the skills with it, or run the same skills in Codex.

## A platform not listed here

Ask the two questions the skill is built on. Where can one account keep a private value that is
still there next session? Where is the list of hosts the agent may reach? Put `VAMO_API_KEY` in
the first and `api.vamotalent.ai` in the second, then run the verification in the skill.
