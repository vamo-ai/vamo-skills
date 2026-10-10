# Changelog

Each skill carries its own version in its `SKILL.md` header and in `skills.json`. A change that
alters what an agent should do raises the minor version. A wording or formatting fix raises the
patch version. A change that makes earlier behavior wrong raises the major version.

## 2026-10-09 (sixth release)

- **vamo-api-access 1.2.0**. On your own machine, access now arrives as a setup code: one line from
  **Connect a tool** in the app, which the agent trades for a key and stores by itself. Nobody
  copies a key, and an agent never asks for one. `references/setup-code.md` has the exchange for
  macOS, Linux and Windows. Windows is covered throughout: the file lives at
  `%USERPROFILE%\.config\vamo\env`, limited to your account, and PowerShell loads it without
  showing it. The lookup order starts with a setup code and is the same on every system. Saving a
  key you created yourself moved to `references/platforms.md`. A project's instructions are no
  longer listed as a place to keep a key, because they hand the key to the model in every
  conversation. The `description` in the header is reworded so that every YAML parser reads it.

## 2026-10-09 (fifth release)

- **role-decomposition 1.3.0**. Top tier is a different thing from famous: no score ceiling still
  keeps the reach screen on, and very large followings are set aside in a separate file.
- **vamo-search 2.1.1**. The sourcing guide says the same for expert benches.

## 2026-10-09 (fourth release)

- **vamo-enrich 1.0.0** (new). Starting from people you already have: an interview check, a
  candidate one-pager, contact details, a personalized opening line, enriching a list from
  another tool, screening a pipeline, deep research on a set.
- **vamo-workflows 1.0.0** (new). Making it repeatable: rules for anything that runs twice, one
  record shape, and patterns for an agent loop, a weekly search, enrichment in front of a
  message, and hand-offs to other tools.
- **vamo-search 2.1.0**. Adds `references/discovery-recipes.md`: twelve starting points and the
  calls for each.
- **vamo-api-access 1.1.2**. Lists the new skills.

## 2026-10-09 (third release)

- **vamo-search 2.0.0**. Absorbs `vamo-sourcing-agent`, which is removed. The field guide is now
  `references/sourcing-guide.md` and the query library `references/domain-library.md`. With the
  plugin installed, `/vamo:vamo-sourcing-agent` becomes `/vamo:vamo-search`.
- **vamo-api-access 1.1.1, role-decomposition 1.2.2**. Cross-references updated. Platform notes
  add OpenAI Codex and ChatGPT.
- `skills.json` drops `category`. The set is one flat list.

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
