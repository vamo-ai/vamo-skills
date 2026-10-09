# Exchanging a setup code

Reference for the `vamo-api-access` skill. A setup code is the one-time code in the line a person
copies from **Connect a tool** in the Vamo app. The two blocks here trade it for an API key and
write the key straight into the private file. The route, `POST /v1/keys/exchange`, is left out of
`openapi.json` on purpose, so the skill and this file are where it is described. Written against
its contract on 2026-10-09.

Four rules hold.

- **The code works once and lasts ten minutes.** Once the API has answered, the code is spent.
  Never send the same code a second time.
- **The key is never shown.** A block writes it to the file and prints only the label, the
  permissions and two addresses. Never print the response or the file, and never type the key into
  a command.
- **Run a block exactly as written.** Replace `SETUP_CODE_HERE` with the setup code, the whole
  token that starts with `vamo_xc_`, and change nothing else. Some fetch tools summarize or reword
  a page, and that changes the blocks. If this file reached you through one, read it again as raw
  text first.
- **Only a setup code goes into a block.** A setup code is one unbroken token: `vamo_xc_`, then
  letters, digits, `-` or `_`. Anything with a space, a quote or another character in it is not a
  setup code. Put it in no command, and ask the person for a fresh line.

A block needs `curl` on macOS and Linux and nothing extra on Windows. Neither needs `jq`.

## macOS and Linux

```sh
sh <<'VAMO_EOF'
code='SETUP_CODE_HERE'
api='https://api.vamotalent.ai'
dir="$HOME/.config/vamo"
tmp="$dir/.exchange.$$"
fail() { echo "VAMO_CONNECT failed: $1"; exit 1; }
keyof() { grep -o '"key" *: *"[^"]*"' "$tmp" | head -n 1 | cut -d'"' -f4; }
case "$code" in vamo_xc_*[!A-Za-z0-9_-]*) false ;; vamo_xc_?*) : ;; *) false ;; esac || fail 'that is not a setup code (code not sent)'
command -v curl >/dev/null 2>&1 || fail 'curl is not installed (code not sent)'
umask 077
mkdir -p "$dir" && chmod 700 "$dir" && rm -f "$dir"/.exchange.* && printf '{"key": "selftest"}' > "$tmp" || fail "cannot write to $dir (code not sent)"
trap 'rm -f "$tmp"' EXIT; trap 'exit 130' INT TERM HUP
[ "$(keyof)" = selftest ] || fail 'this shell cannot read the response (code not sent)'
device=$(uname -n | tr -cd 'A-Za-z0-9._-' | cut -c1-64)
body=$(printf '{"code":"%s","device":"%s"}' "$code" "$device")
[ -n "$device" ] || body=$(printf '{"code":"%s"}' "$code")
http=$(printf '%s' "$body" | curl -q -sS -m 60 -o "$tmp" -w '%{http_code}' \
  -H 'content-type: application/json' --data-binary @- "$api/v1/keys/exchange")
case "$http" in 2[0-9][0-9]) ;; [0-9][0-9][0-9]) fail "status $http" ;; *) fail 'curl gave no status' ;; esac
key=$(keyof)
printf '%s' "$key" | grep -Eq '^vamo_sk_[A-Za-z0-9_]+$' || fail 'the response had no key'
printf 'VAMO_API_KEY=%s\n' "$key" > "$dir/env" && chmod 600 "$dir/env" || fail "cannot write $dir/env"
echo 'VAMO_CONNECT ok'
grep -Eo '"(label|apiBaseUrl|mcpUrl)" *: *"[^"]*"' "$tmp"
grep -o '"permissions" *: *\[[^]]*]' "$tmp"
VAMO_EOF
```

## Windows

In PowerShell. Use this block even when a bash shell is available, because only it can limit the
file to your account. If the agent's shell tool only runs bash, save the block as a `.ps1` file in
the temp folder, run `powershell -NoProfile -ExecutionPolicy Bypass -File <that file>`, then delete
the file.

```powershell
& {
  $code = 'SETUP_CODE_HERE'
  $api = 'https://api.vamotalent.ai'
  $ErrorActionPreference = 'Stop'
  $dir = Join-Path $env:USERPROFILE '.config\vamo'
  $envFile = Join-Path $dir 'env'
  if ($code -cnotmatch '^vamo_xc_[A-Za-z0-9_-]+$') { 'VAMO_CONNECT failed: that is not a setup code (code not sent)'; return }
  try {
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    icacls $dir /inheritance:r /grant:r "*${sid}:(OI)(CI)F" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'icacls failed' }
  } catch { "VAMO_CONNECT failed: cannot prepare $dir (code not sent)"; return }
  [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
  $body = @{ code = $code; device = [Environment]::MachineName } | ConvertTo-Json -Compress
  try {
    $r = Invoke-RestMethod -Method Post -Uri "$api/v1/keys/exchange" -ContentType 'application/json' -Body $body -TimeoutSec 60
  } catch {
    $http = '000'
    if ($_.Exception.Response) { $http = [int]$_.Exception.Response.StatusCode }
    "VAMO_CONNECT failed: status $http"; return
  }
  if ("$($r.key)" -notmatch '^vamo_sk_[A-Za-z0-9_]+$') { 'VAMO_CONNECT failed: the response had no key'; return }
  try {
    [IO.File]::WriteAllText($envFile, "VAMO_API_KEY=$($r.key)`n")
    icacls $envFile /inheritance:r /grant:r "*${sid}:F" | Out-Null
  } catch { "VAMO_CONNECT failed: cannot write $envFile"; return }
  'VAMO_CONNECT ok'
  $r | Select-Object label, apiBaseUrl, mcpUrl, permissions | ConvertTo-Json -Compress
}
```

## What the block printed

| It printed | What happened | Do this |
| --- | --- | --- |
| `VAMO_CONNECT ok` | The key is stored. The lines after it give `label`, `apiBaseUrl`, `mcpUrl` and `permissions` | Load the key and verify, as below |
| `failed: status 404` | The code was already used, has expired, or was cancelled by a newer one | Ask the person to press the button in **Connect a tool** again and paste the new line. Then stop |
| `failed: status 000` | The request never reached the API | Get outbound HTTPS to `api.vamotalent.ai` allowed, then run the block again |
| `failed: status 429` | Too many attempts came from this network | Wait a minute, then run the block again |
| `failed: ... (code not sent)` | Nothing was sent, so the code is still good | Fix what the line names and run the block again. Not a setup code: the placeholder is still there, or what replaced it has a character a code never has. Copy the code again from the person's message with nothing around it. No `curl`: install it with the system package manager. Cannot write: the shell is sandboxed, so ask the person to approve running the block outside the sandbox. Cannot read the response: the block changed in copying, so read this file again and run it unchanged. If it fails the same way, stop and report it. Never store the key somewhere else instead, and never swap in a tool that prints the response |
| Anything else | The exchange did not finish | Report the exact line, then ask the person for a fresh line |

## After the exchange

The key is in `~/.config/vamo/env`, or `%USERPROFILE%\.config\vamo\env` on Windows, as one line:
`VAMO_API_KEY=...`. Only your account can read the file. Load it for this session the way the
skill shows under **Store access so it persists**, then run the skill's verification.

`label` reads like `<tool> on <machine>`. It is the name the key carries in the app, where it can
be revoked. `permissions` lists what the key may do. `mcpUrl` is the address of the Vamo MCP server
for a tool that connects that way: the hosted page named in the line the person pasted adds it to
the tool.
