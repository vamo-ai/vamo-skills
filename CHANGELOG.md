# Changelog

Each skill carries its own version in its `SKILL.md` header and in `skills.json`. A change that
alters what an agent should do raises the minor version. A wording or formatting fix raises the
patch version. A change that makes earlier behavior wrong raises the major version.

## 2026-10-14

Eight skills become six, one per job: connect (`vamo-setup`), fix (`vamo-troubleshooting`), find
(`vamo-search`), look up (`vamo-enrich`), reach out (`vamo-outreach`) and work with other tools
(`vamo-workflows`). Several skills claimed the same requests ("set up Vamo", "connect", "setup
code"), so an agent had to guess between them. Each request now belongs to one skill, and the
material the others held moved into reference files.

- **vamo-setup 1.0.0** (new). Guided setup in the AI tool a person already uses. The agent works
  out which tool it is in (Claude Code, Claude on the web or desktop, Cursor, Codex, ChatGPT,
  Gemini or another agent) and what it can reach by checking, then picks the route that keeps
  working: the Vamo MCP server with browser sign-in by default, the MCP server with a one-time
  setup code where sign-in is not offered, and direct API access only for people writing their own
  code. It adds the skills, verifies with one search, and runs the first search as a short
  tutorial pitched at the person's depth. **Replaces `vamo-api-access`**, now
  `references/direct-api.md` (with `setup-code.md`, `platforms.md` and `curl-trainer.md`).
- **vamo-outreach 1.0.0** (new). Personalized technical outreach grounded in what each engineer
  built and linked to the problem the team is hiring for: two openings per person, subject lines,
  two follow-ups, a quality check, merge fields with a variant tag for a sending tool. A person
  approves every message. Takes over the message recipe from `vamo-enrich` and the "enrichment in
  front of a message" pattern from `vamo-workflows`.
- **vamo-search 3.1.0**. **Replaces `role-decomposition` and `fanout-search`**, now
  `references/role-decomposition.md` (with `role-decomposition-example.md`) and
  `references/fanout.md`. With the Vamo MCP tools connected, the agent makes its calls through
  them and keeps the method.
- **vamo-enrich 1.2.0**. Starts from people wherever they came from: an applicant tracking system
  such as Ashby, LinkedIn profiles, applicants, a spreadsheet. Never guesses a GitHub username.
- **vamo-workflows 1.2.0**. Reframed around the other tools an agent reaches through connectors:
  who owns what, new matches posted to Slack, applicants screened and written back to the
  tracking system, drafts left in Gmail for approval, a weekly search, your own sourcing agent.
- **vamo-troubleshooting 1.2.0**. Points at `vamo-setup` for connecting again.
- **Removed names.** `/vamo:vamo-api-access`, `/vamo:role-decomposition` and
  `/vamo:fanout-search` no longer exist. Use `/vamo:vamo-setup` or `/vamo:vamo-search`, or ask in
  plain words.

## 2026-10-13

- **vamo-api-access 1.4.0, vamo-enrich 1.1.0, vamo-workflows 1.1.0, vamo-troubleshooting 1.1.0,
  role-decomposition 1.4.0**. Search and lookup move to the v2 developers API: a search is one
  JSON body to `POST /v2/developers/search` (facts as filters with name resolution, the work as
  one phrase, `repos`, `sort`, `cursor`, `exclude`), lookups go to `POST /v2/developers` (logins,
  LinkedIn profiles or ids), and similar, enrich, emails, summaries and deep research use their
  `/v2` routes. `GET /v2/developers/fields`, `POST /v2/developers/search/validate` and
  `POST /v2/developers/resolve` replace reading parameters from the spec. When a `/v2/developers`
  route answers `404` or `503` on the production host, each skill falls back to the v1 route of
  the same name and says so in one line.
  - `vamo-api-access`: verification runs one v2 search, with the v1 form as the fallback. The curl
    walkthrough is rewritten for v2 bodies.
  - `vamo-enrich`: a row with only a LinkedIn URL can now be looked up.
  - `vamo-workflows`: stored searches are validated before each run; the record carries devRank.
  - `vamo-troubleshooting`: the v2 `400` body (`error`, `hint`) and the `404` / `503` fallback.
  - `role-decomposition`: every binding, band and planned call is written as v2 filters
    (`devrank`, `location_ids`, `former_company_ids`, `past_company_ids`, `school_ids`,
    `graduation_year`, `title_level`), with the worked example to match.
- **vamo-search 3.0.0**. Searches with one request to the v2 developers API
  (`POST /v2/developers/search`, `/similar`, `/aggregate`): facts are filters, the work is one
  short phrase in a vector lane, repositories and look-alike seeds are part of the same body.
  The request shape, the filters and the response fields are in the skill itself, so an agent
  needs no other reading to search. Enrich, emails, summaries, lookup and deep research move to
  their `/v2` paths. The discovery recipes and the sourcing guide are rewritten for the new
  request; the domain library maps its short notes to it.
  A `404` or `503` on a `/v2` route falls back to the v1 route of the same name, `repos_of`
  takes an org or person login (a single repository is the `repos` clause), and the prose says
  developers.
- **vamo-api-access 1.3.0**. On your own machine, access now arrives as a setup code: one line from
  **Connect a tool** in the app, which the agent trades for a key and stores by itself. Nobody
  copies a key, and an agent never asks for one. `references/setup-code.md` has the exchange for
  macOS, Linux and Windows. Windows is covered throughout: the file lives at
  `%USERPROFILE%\.config\vamo\env`, limited to your account, and PowerShell loads it without
  showing it. The lookup order starts with a setup code and is the same on every system. Saving a
  key you created yourself moved to `references/platforms.md`. A project's instructions are no
  longer listed as a place to keep a key, because they hand the key to the model in every
  conversation. The `description` in the header is reworded so that every YAML parser reads it.
  The steps for a key a person creates follow the app: API keys sit under Developer in Settings, a
  key is taken away with **Remove**, and Search: Write is reading saved deep-research reports.
  The error table stays in `vamo-troubleshooting`; the access skill keeps one line for an expired
  or used setup code.

## 2026-10-12

- **vamo-troubleshooting 1.0.0** (new). An agent diagnoses its own Vamo connection: which route
  it is on (the MCP tools, or the API over HTTP), three checks in order, every API error with
  what to tell the person, the MCP cases (not connected, the fixed account sentence, an expired
  page), what to pass on to Vamo, and the rules. It never prints a key, and it asks before it
  installs or changes anything.
- **vamo-api-access 1.2.0**. The error table moved to `vamo-troubleshooting`. **Read the error**
  is now one line that points there. Setup, storage, the network path and verification are
  unchanged.
- **vamo-search 2.1.3, vamo-enrich 1.0.2, role-decomposition 1.3.1**. Cross-references point at
  `vamo-troubleshooting` for errors.

## 2026-10-09 (automation)

- Pull requests are validated by `scripts/validate.py`: the manifest against the folders, each
  skill header, the plugin manifests, the contents policy, and a higher version plus a changelog
  line for every skill that changed.
- A merge to `main` that changes a skill publishes a release with one zip per skill.
- **vamo-api-access 1.1.3, vamo-search 2.1.2, vamo-enrich 1.0.1, vamo-workflows 1.0.1**. Each
  `description` is reworded so the header reads the same in every YAML parser. What an agent
  should do is unchanged.

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
