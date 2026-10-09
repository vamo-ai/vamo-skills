# Changelog

Each skill carries its own version in its `SKILL.md` header and in `skills.json`. A change that
alters what an agent should do raises the minor version. A wording or formatting fix raises the
patch version. A change that makes earlier behavior wrong raises the major version.

## Hosted catalog

- The skills are served at `https://vamotalent.ai/skills`, as a catalog and as raw markdown, read
  live from this repository. README and **vamo-api-access 1.1.1** point update checks at
  `https://vamotalent.ai/skills/index.json`.

## 2026-10-09 (second release)

- **vamo-api-access 1.1.0**. Renamed from `vamo-api`. Platform-agnostic: storage is described by
  kind of environment (your own machine, or a sandbox that starts empty) and network access by
  who administers it. Product-specific menu paths moved to `references/platforms.md`. The private
  access skill is named `vamo-access`.
- **vamo-search 1.1.1, role-decomposition 1.2.1, vamo-sourcing-agent 1.1.1**. Cross-references
  updated to the new name.

## 2026-10-09

- **vamo-api 1.0.0** (new). Direct API usage: getting a key, which permissions to grant, storing
  the key so it persists between sessions, opening network access, verifying the connection,
  reading errors, troubleshooting by symptom. Replaces `vamo-api-quickstart`, whose walkthrough is
  now `references/curl-trainer.md`. The key variable is `VAMO_API_KEY`.
- **role-decomposition 1.2.0**. Engagement type sets the band. A client's stated bar overrides it.
  Regional tiers are a segment. Queries carry a domain anchor. Lanes declare an evidence kind.
  People found in several lanes rank higher. Probes run in parallel groups.
- **vamo-sourcing-agent 1.1.0**. Identity check, rank and diversify, hand-over format, playbooks
  for early-career lists, deep contributors, outreach tiers and part-time expert benches.
- **vamo-search 1.1.0**. Rewritten against the published spec: row order is the ranking, two
  filter families, short-page reasons.
- **fanout-search 1.0.1**. Examples describe projects generically. Punctuation.
- Versioning introduced: `metadata.version` in each skill, `skills.json`, this file.
