#!/usr/bin/env python3
"""Validate this repository's skills. Standard library only.

    python3 scripts/validate.py                  # check the tree
    python3 scripts/validate.py --base <git ref> # also check versions against that ref

Prints every failure, one per line, and exits non-zero if there is any.
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = "skills"
MANIFEST = "skills.json"
CHANGELOG = "CHANGELOG.md"
README = "README.md"
PLUGIN = ".claude-plugin/plugin.json"
MARKETPLACE = ".claude-plugin/marketplace.json"

# every skill entry in skills.json carries these
MANIFEST_FIELDS = ("title", "version", "updated", "path", "summary", "files")
# every SKILL.md header carries these under metadata
METADATA_FIELDS = ("version", "updated")
DESCRIPTION_MAX = 1024

EM_DASH = "—"
# a real key, as opposed to the "vamo_sk_..." placeholder the skills use
LIVE_KEY = re.compile(r"vamo_sk_[A-Za-z0-9_-]{8,}")
PEM_KEY = re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY")
# words skill text leaves out, each with what to write instead
BANNED_WORDS = (
    (re.compile(r"shortlist", re.IGNORECASE), 'say "list"'),
    (re.compile(r"\bcredits?\b", re.IGNORECASE), "skills do not talk about what a call spends"),
    (re.compile(r"reveal", re.IGNORECASE), 'say "get"'),
)

# YAML block scalar markers, and how their lines join
BLOCK_SCALARS = {">": " ", ">-": " ", ">+": " ", "|": "\n", "|-": "\n", "|+": "\n"}

failures = []


def fail(where, message):
    # file names and header values come from the change under review, so keep each failure on
    # one printable line
    text = f"{where}: {message}"
    failures.append("".join(c if c.isprintable() else "?" for c in text))


def read_text(path):
    """The file as text, or None after recording why it could not be read."""
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fail(path, "is not UTF-8 text")
    except OSError:
        fail(path, "is missing or unreadable")
    return None


def load_json(path):
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError as error:
        fail(path, f"does not parse as JSON ({error})")
        return None


def scalar(value):
    """One YAML value as text: surrounding quotes removed, nothing else interpreted."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        if value[0] == '"':
            try:
                return str(json.loads(value))
            except ValueError:
                pass
        return value[1:-1]
    return value


def frontmatter(text):
    """The header of a SKILL.md as a dict.

    Reads the subset of YAML the skills use: one-line values, block scalars, and one level of
    nesting. Raises ValueError on anything else.
    """
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        raise ValueError("does not start with ---")
    end = next((i for i, line in enumerate(lines) if i and line.rstrip() == "---"), None)
    if end is None:
        raise ValueError("is not closed with ---")
    body = lines[1:end]
    data = {}
    i = 0
    while i < len(body):
        line = body[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, colon, value = line.partition(":")
        if line[0] in " \t" or not colon:
            raise ValueError(f"has an unreadable line {i + 1}")
        value = value.strip()
        # the indented lines that belong to this key
        nested = []
        while i < len(body) and (not body[i].strip() or body[i][0] in " \t"):
            if body[i].strip():
                nested.append(body[i].strip())
            i += 1
        if value in BLOCK_SCALARS:
            data[key.strip()] = BLOCK_SCALARS[value].join(nested)
        elif value:
            data[key.strip()] = scalar(" ".join([value, *nested]))
        else:
            child = {}
            for item in nested:
                if item.startswith("#"):
                    continue
                child_key, colon, child_value = item.partition(":")
                if not colon:
                    raise ValueError(f'has an unreadable line under "{key.strip()}"')
                child[child_key.strip()] = scalar(child_value)
            data[key.strip()] = child
    return data


def check_header(name, entry):
    path = f"{SKILLS_DIR}/{name}/SKILL.md"
    text = read_text(path)
    if text is None:
        return
    try:
        header = frontmatter(text)
    except ValueError as error:
        fail(path, f"header {error}")
        return
    if header.get("name") != name:
        fail(path, f'name is "{header.get("name")}", the folder is "{name}"')
    description = header.get("description")
    if not isinstance(description, str) or not description:
        fail(path, "has no description")
    elif len(description) > DESCRIPTION_MAX:
        fail(path, f"description is {len(description)} characters, the limit is {DESCRIPTION_MAX}")
    metadata = header.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    for field in METADATA_FIELDS:
        if not metadata.get(field):
            fail(path, f"has no metadata.{field}")
    version = metadata.get("version")
    if version and version != entry.get("version"):
        fail(path, f'metadata.version is "{version}", {MANIFEST} says "{entry.get("version")}"')


def check_skill(name, entry):
    where = f"{MANIFEST} ({name})"
    if not isinstance(entry, dict):
        fail(where, "is not an object")
        return
    for field in MANIFEST_FIELDS:
        if not entry.get(field):
            fail(where, f'has no "{field}"')
    folder = f"{SKILLS_DIR}/{name}"
    if entry.get("path") != folder:
        fail(where, f'path is "{entry.get("path")}", expected "{folder}"')
    if not (ROOT / folder).is_dir():
        fail(where, f"has no folder at {folder}")
        return
    on_disk = sorted(
        p.relative_to(ROOT / folder).as_posix() for p in (ROOT / folder).rglob("*.md") if p.is_file()
    )
    listed = entry.get("files")
    if not isinstance(listed, list) or sorted(str(f) for f in listed) != on_disk:
        fail(where, f"files do not match the markdown files in {folder}: {', '.join(on_disk)}")
    check_header(name, entry)


def check_manifest(manifest):
    """Check skills.json against the folders. Returns the skills it lists."""
    skills = manifest.get("skills") if isinstance(manifest, dict) else None
    if not isinstance(skills, dict):
        fail(MANIFEST, 'has no "skills" object')
        skills = {}
    for folder in sorted(p for p in (ROOT / SKILLS_DIR).iterdir() if p.is_dir()):
        if folder.name not in skills:
            fail(f"{SKILLS_DIR}/{folder.name}", f"is not listed in {MANIFEST}")
    for name, entry in skills.items():
        check_skill(name, entry)
    return skills


def check_plugin(manifest):
    plugin = load_json(PLUGIN)
    marketplace = load_json(MARKETPLACE)
    block = manifest.get("plugin") if isinstance(manifest, dict) else None
    expected = block.get("name") if isinstance(block, dict) else None
    if not expected:
        fail(MANIFEST, "has no plugin.name")
        return
    if isinstance(plugin, dict) and plugin.get("name") != expected:
        fail(PLUGIN, f'name is "{plugin.get("name")}", {MANIFEST} plugin.name is "{expected}"')
    if isinstance(marketplace, dict):
        listed = marketplace.get("plugins")
        names = [p.get("name") for p in listed if isinstance(p, dict)] if isinstance(listed, list) else []
        if expected not in names:
            fail(MARKETPLACE, f'lists no plugin named "{expected}"')


def skill_files():
    """Every file under skills/, as repository paths."""
    found = []
    for folder, dirs, files in os.walk(ROOT / SKILLS_DIR):
        dirs.sort()
        for name in sorted(dirs + files):
            path = pathlib.Path(folder, name)
            relative = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                fail(relative, "is a symbolic link, and skills ship regular files only")
            elif path.is_file() and name != ".DS_Store":
                found.append(relative)
    return found


def check_policy(path, words):
    """The contents policy for one file. The word rules apply to skill text only."""
    text = read_text(path)
    if text is None:
        return
    for number, line in enumerate(text.splitlines(), 1):
        where = f"{path}:{number}"
        if EM_DASH in line:
            fail(where, "has an em dash")
        # never echo the match: a real key would land in a public log
        if LIVE_KEY.search(line):
            fail(where, "has what looks like a live key, write the placeholder as vamo_sk_...")
        if PEM_KEY.search(line):
            fail(where, "has a private key header")
        if not words:
            continue
        for pattern, instead in BANNED_WORDS:
            found = pattern.search(line)
            if found:
                fail(where, f'has the word "{found.group(0)}", {instead}')


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def check_base(ref, skills):
    """A skill that changed since ref has a new version, and the changelog changed with it."""
    resolved = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if ref.startswith("-") or resolved.returncode != 0:
        fail("--base", f'"{ref}" is not a commit in this checkout')
        return
    base = resolved.stdout.strip()
    diff = git("diff", "--name-only", "--no-renames", "-z", base, "--", SKILLS_DIR, CHANGELOG)
    new = git("ls-files", "--others", "--exclude-standard", "-z", "--", SKILLS_DIR)
    if diff.returncode != 0 or new.returncode != 0:
        fail("--base", f'could not compare the tree with "{ref}"')
        return
    changed = set(filter(None, (diff.stdout + new.stdout).split("\0")))
    try:
        base_skills = json.loads(git("show", f"{base}:{MANIFEST}").stdout)["skills"]
    except (ValueError, KeyError, TypeError):
        base_skills = {}  # no readable manifest at the base, so every skill is new
    changed_skills = sorted(
        {p.split("/")[1] for p in changed if p.startswith(f"{SKILLS_DIR}/") and p.count("/") > 1}
    )
    for name in changed_skills:
        before = base_skills.get(name)
        now = skills.get(name)
        # a skill that is new, or removed, has no version to raise
        if not isinstance(before, dict) or not isinstance(now, dict):
            continue
        if now.get("version") == before.get("version"):
            fail(
                f"{SKILLS_DIR}/{name}",
                f'changed since {ref} but its version in {MANIFEST} is still "{before.get("version")}"',
            )
    if changed_skills and CHANGELOG not in changed:
        fail(CHANGELOG, f"did not change, but these skills changed since {ref}: {', '.join(changed_skills)}")


def main():
    parser = argparse.ArgumentParser(description="Validate this repository's skills.")
    parser.add_argument(
        "--base",
        metavar="REF",
        help="also require a new version and a changelog change for every skill that differs from REF",
    )
    args = parser.parse_args()

    manifest = load_json(MANIFEST)
    skills = check_manifest(manifest)
    check_plugin(manifest)
    for path in (README, CHANGELOG):
        check_policy(path, words=False)
    skill_text = [MANIFEST, *skill_files()]
    for path in skill_text:
        check_policy(path, words=True)
    if args.base:
        check_base(args.base, skills)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        print(f"\n{len(failures)} failed", file=sys.stderr)
        return 1
    print(f"ok: {len(skills)} skills, {len(skill_text) + 2} files checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
