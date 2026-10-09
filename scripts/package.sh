#!/usr/bin/env bash
# Build one upload-ready zip per skill into dist/, named <skill>-<version>.zip.
# Each zip has the skill folder at its top level, which is what a skill upload expects.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir dist
# every file a skill ships must be listed in skills.json, which is what hosted copies are built from
python3 - <<'CHECK'
import json, pathlib, sys
m = json.load(open("skills.json"))["skills"]
for name, s in m.items():
    on_disk = sorted(str(p.relative_to(s["path"])) for p in pathlib.Path(s["path"]).rglob("*.md"))
    if on_disk != sorted(s["files"]):
        sys.exit(f"skills.json files for {name} do not match disk: {on_disk}")
CHECK
for dir in skills/*/; do
  name=$(basename "$dir")
  version=$(sed -n 's/^  version: "\(.*\)"$/\1/p' "$dir/SKILL.md" | head -1)
  [ -n "$version" ] || { echo "no version in $dir/SKILL.md" >&2; exit 1; }
  (cd skills && zip -qr "../dist/${name}-${version}.zip" "$name" -x '*.DS_Store')
  echo "dist/${name}-${version}.zip"
done
