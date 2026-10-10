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
# a version is three integers, as in 1.2.3
VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")

EM_DASH = "—"
# a real key or agent token, as opposed to the "vamo_sk_..." placeholder the skills use
LIVE_KEY = re.compile(r"vamo_(?:sk|at)_[A-Za-z0-9_-]{8,}")
PEM_KEY = re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY")
# Words skill text leaves out, each with what to write instead. They match inside route and
# field names too, on purpose: a skill points at the spec for those.
BANNED_WORDS = (
    (re.compile(r"shortlist", re.IGNORECASE), 'say "list", in route and field names too'),
    # The word on its own and inside a name (creditsCharged, credits_used, totalCredits), but
    # not inside another word (accredited) and not as a verb about authorship (credited).
    (
        re.compile(r"(?:(?<![A-Za-z])(?:credit|CREDIT)|Credit)(?!(?i:ed|ing)\b)\w*"),
        'skills do not talk about what a call spends. For authorship write "credited"',
    ),
    (re.compile(r"reveal", re.IGNORECASE), 'say "get", in route and field names too'),
)

# YAML block scalar markers, and how their lines join
BLOCK_SCALARS = {">": " ", ">-": " ", ">+": " ", "|": "\n", "|-": "\n", "|+": "\n"}
# a "key: value" line of a header, and a "- item" line of a list
KEY_LINE = re.compile(r"([A-Za-z0-9_.-]+)\s*:(?:\s+(.*))?$")
LIST_ITEM = re.compile(r"-(?:\s+(.*))?$")
# an unquoted YAML value cannot start with one of these
RESERVED_START = "!&*{}[]|>%@`,"

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
        # the wording rules cannot read an image or a PDF, so a skill does not ship one
        skill_file = path.startswith(f"{SKILLS_DIR}/")
        fail(path, "is not UTF-8 text" + (", and skills ship text files only" if skill_file else ""))
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


def quoted(key, value):
    """A value that opens with a quote, as its text and whatever follows the closing quote."""
    quote = value[0]
    end = 1
    while end < len(value):
        if quote == '"' and value[end] == "\\":
            end += 2  # an escaped character
        elif value[end] != quote:
            end += 1
        elif quote == "'" and value[end + 1 : end + 2] == "'":
            end += 2  # two single quotes are one, inside single quotes
        else:
            break
    else:
        raise ValueError(f'"{key}" has a value with no closing {quote}')
    text, rest = value[1:end], value[end + 1 :]
    if quote == "'":
        return text.replace("''", "'"), rest
    try:
        return json.loads(f'"{text}"', strict=False), rest
    except ValueError:
        raise ValueError(f'"{key}" has an escape in double quotes that this script does not read') from None


def scalar(key, value):
    """One YAML value the way a YAML parser reads it: text, or a list for [a, b].

    Raises ValueError where a parser would stop, or would read something other than the text
    as written.
    """
    value = value.strip()
    if not value or value[0] == "#":
        return ""
    if value[0] in "\"'":
        text, rest = quoted(key, value)
        # only a comment may follow the closing quote
        if rest.strip() and not (rest[0].isspace() and rest.lstrip()[0] == "#"):
            raise ValueError(f'"{key}" has text after its closing {value[0]}')
        return text
    if value[0] == "[" and value[-1] == "]":
        return [value[1:-1]]  # what is inside is left as written
    if " #" in value or "\t#" in value:
        raise ValueError(
            f'"{key}" has " #" in an unquoted value, which YAML reads as the start of a comment.'
            " Put the value in quotes"
        )
    if ": " in value or value[-1] == ":":
        raise ValueError(
            f'"{key}" has ": " in an unquoted value, which YAML reads as a nested key.'
            " Reword it, or put the value in quotes"
        )
    if value[0] in RESERVED_START or value[:2] in ("- ", "? ") or value in ("-", "?"):
        raise ValueError(f'"{key}" has an unquoted value that starts with {value[0]}, put it in quotes')
    return value


def collection(key, lines):
    """The lines under a key that has no value of its own: a mapping or a list of one-line values."""
    lines = [line for line in lines if not line.lstrip().startswith("#")]
    if len({len(line) - len(line.lstrip()) for line in lines}) > 1:
        raise ValueError(f'nests more than one level under "{key}"')
    lines = [line.strip() for line in lines]
    items = [LIST_ITEM.match(line) for line in lines]
    if lines and all(items):
        return [scalar(key, item.group(1) or "") for item in items]
    child = {}
    for line in lines:
        entry = KEY_LINE.match(line)
        if not entry:
            raise ValueError(f'has an unreadable line under "{key}"')
        name = f"{key}.{entry.group(1)}"
        if entry.group(1) in child:
            raise ValueError(f'has "{name}" twice')
        child[entry.group(1)] = scalar(name, entry.group(2) or "")
    return child


def frontmatter(text):
    """The header of a SKILL.md as a dict.

    Reads the subset of YAML the skills use: one-line values with an optional comment, block
    scalars, lists, and one level of nesting. Raises ValueError on anything else, and on a
    header a YAML parser would reject or read differently.
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
        entry = KEY_LINE.match(line)
        if not entry:
            raise ValueError(f"has an unreadable line {i + 1}")
        key, value = entry.group(1), (entry.group(2) or "").strip()
        if key in data:
            raise ValueError(f'has "{key}" twice')
        if value.startswith("#"):
            value = ""  # a comment after the key
        # the lines that belong to this key: indented ones, and list items written flush left
        nested = []
        while i < len(body) and (
            not body[i].strip() or body[i][0] in " \t" or (not value and LIST_ITEM.match(body[i]))
        ):
            if body[i].strip():
                nested.append(body[i].rstrip())
            i += 1
        if value in BLOCK_SCALARS:
            data[key] = BLOCK_SCALARS[value].join(line.strip() for line in nested)
        elif value:
            data[key] = scalar(key, " ".join([value, *(line.strip() for line in nested)]))
        else:
            data[key] = collection(key, nested)
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


def version_numbers(version):
    """A version as three integers, or None when it is not written that way."""
    found = VERSION.fullmatch(version) if isinstance(version, str) else None
    return tuple(int(part) for part in found.groups()) if found else None


def check_skill(name, entry):
    where = f"{MANIFEST} ({name})"
    if not isinstance(entry, dict):
        fail(where, "is not an object")
        return
    for field in MANIFEST_FIELDS:
        if not entry.get(field):
            fail(where, f'has no "{field}"')
    if entry.get("version") and version_numbers(entry.get("version")) is None:
        fail(where, f'version "{entry.get("version")}" is not three integers, as in 1.2.3')
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
    """The wording policy for one file. The word rules apply to skill text only."""
    text = read_text(path)
    if text is None:
        return
    for number, line in enumerate(text.splitlines(), 1):
        where = f"{path}:{number}"
        if EM_DASH in line:
            fail(where, "has an em dash")
        if not words:
            continue
        for pattern, instead in BANNED_WORDS:
            found = pattern.search(line)
            if found:
                fail(where, f'has the word "{found.group(0)}", {instead}')


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def repository_files():
    """Every file git tracks or would add, as repository paths."""
    listed = git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    if listed.returncode != 0:
        fail("git ls-files", "could not list the files in this checkout")
        return []
    return sorted(set(filter(None, listed.stdout.split("\0"))))


def check_secrets(path):
    """No file in the repository holds a key, whatever kind of file it is."""
    file = ROOT / path
    # nothing to read for a file deleted from the working tree, and a link is not followed
    if file.is_symlink() or not file.is_file():
        return
    try:
        text = file.read_bytes().decode("utf-8", "replace")
    except OSError:
        fail(path, "is unreadable")
        return
    for number, line in enumerate(text.splitlines(), 1):
        where = f"{path}:{number}"
        # never echo the match: a real key would land in a public log
        if LIVE_KEY.search(line):
            fail(where, "has what looks like a live key, write the placeholder as vamo_sk_...")
        if PEM_KEY.search(line):
            fail(where, "has a private key header")


def check_base(ref, skills):
    """A skill that changed since ref has a higher version, and the changelog changed with it."""
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
        new = version_numbers(now.get("version"))
        old = version_numbers(before.get("version"))
        # check_skill reports a version that does not read as numbers, and one like that at the
        # base leaves nothing to compare with
        if new is None or old is None:
            continue
        if new <= old:
            fail(
                f"{SKILLS_DIR}/{name}",
                f'changed since {ref}, so its version in {MANIFEST} has to be higher than'
                f' "{before.get("version")}" (it is "{now.get("version")}")',
            )
    if changed_skills and CHANGELOG not in changed:
        fail(CHANGELOG, f"did not change, but these skills changed since {ref}: {', '.join(changed_skills)}")


def main():
    parser = argparse.ArgumentParser(description="Validate this repository's skills.")
    parser.add_argument(
        "--base",
        metavar="REF",
        help="also require a higher version and a changelog change for every skill that differs from REF",
    )
    args = parser.parse_args()

    manifest = load_json(MANIFEST)
    skills = check_manifest(manifest)
    check_plugin(manifest)
    for path in (README, CHANGELOG):
        check_policy(path, words=False)
    for path in (MANIFEST, *skill_files()):
        check_policy(path, words=True)
    files = repository_files()
    for path in files:
        check_secrets(path)
    if args.base:
        check_base(args.base, skills)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        print(f"\n{len(failures)} failed", file=sys.stderr)
        return 1
    print(f"ok: {len(skills)} skills, {len(files)} files checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
