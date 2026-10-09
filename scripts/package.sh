#!/usr/bin/env bash
# Build one upload-ready zip per skill into dist/, named <skill>-<version>.zip.
# Each zip has the skill folder at its top level, which is what a skill upload expects.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir dist
for dir in skills/*/; do
  name=$(basename "$dir")
  version=$(sed -n 's/^  version: "\(.*\)"$/\1/p' "$dir/SKILL.md" | head -1)
  [ -n "$version" ] || { echo "no version in $dir/SKILL.md" >&2; exit 1; }
  (cd skills && zip -qr "../dist/${name}-${version}.zip" "$name" -x '*.DS_Store')
  echo "dist/${name}-${version}.zip"
done
