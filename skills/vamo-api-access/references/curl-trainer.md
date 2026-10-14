# Vamo Developer API: curl walkthrough

Reference for the `vamo-api-access` skill. Sixteen steps, in order, cover the whole API. These are worked
examples written against the v2 developers API on 2026-10-13. Check a field with
`GET /v2/developers/fields`, or a whole body with `POST /v2/developers/search/validate`, before
relying on it.

Values in angle brackets are yours to fill in: `<login>` is a GitHub username, `<owner/name>` a
repository, `<org>` a GitHub organization, `<Company>`, `<University>` and `<City>` plain names.

- Base URL `https://api.vamotalent.ai`
- Docs `https://api.vamotalent.ai/docs`
- Machine-readable spec `https://api.vamotalent.ai/openapi.json`. The fields a search may use are
  listed live at `GET /v2/developers/fields`. Both win over this file when they disagree.

**v1 fallback.** On the production host, `/v2/developers/*` can answer `404` or `503` until the
v2 engine is switched on there. Then use the v1 route of the same name (`GET /v1/developers/search`
with query parameters, `GET /v1/developers/enrich`, `GET /v1/developers/similar?login=`, and so on,
all listed in the spec) and tell the person in one line that the call ran on v1.

---

## 1. Load your key and set up two helpers

Getting access and storing it safely are covered in the `vamo-api-access` skill. With the key in
`VAMO_API_KEY`:

```bash
vamo()     { curl -s "https://api.vamotalent.ai$1" -H "Authorization: Bearer $VAMO_API_KEY"; }
vamoPost() { curl -s -X POST "https://api.vamotalent.ai$1" -H "Authorization: Bearer $VAMO_API_KEY" -H "content-type: application/json" -d "$2"; }
```

The helpers are shell shorthand. A plain `curl -s -X POST "..." -H "Authorization: Bearer $VAMO_API_KEY"`
with a JSON body works the same anywhere. On Windows, `platforms.md` has the same two helpers for PowerShell.

## 2. Run a first search

A search is one JSON body. The work goes in one short phrase, ranked by meaning.

```bash
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "rust systems programming"]], "limit": 3}'
```

`ask` is optional plain language for the re-rank to read. Facts never go in the phrase: they are
filters (step 4).

## 3. Read the response

```bash
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "lsm-tree storage engine with compaction"]], "limit": 5}' \
  | jq '{count: .countStatus, next: .cursor, people: [.results[] | {id, login, name, hasEmail, why: [.evidence.matches[]?.full_name]}]}'
```

| Field | Meaning |
| --- | --- |
| `results[]` | Developers, best match first. The order is the ranking. |
| `id`, `login`, `name`, `hasEmail`, `hasLinkedin`, `hasLocation` | The identity spine on every row. `id` is GitHub's numeric user id as a string and survives renames. |
| `evidence.matches[]` | Why this person came back: the repo (`full_name`, `stars`, `repo_role`, `similarity`), the role or the profile row that matched, and the `lane` it matched in. |
| `match.repos[]` | The matched repositories: `fullName`, `stars`, `language`, `role` (`owner` or `contributor`). |
| `index` | The card the search ran on: `profile`, `top_repos`, and at `enriched` or `deep` `recent_roles`. |
| `details` | Keyed by namespace: `githubProfile.core`, `githubProfile.repos`, `identity.linkedin`, `identity.experience`, `identity.education`, `contact.socials`, `contact.location`, `contact.emails`, `github.gardenSummary`, `ai.*`. A namespace appears only when resolved. |
| `countStatus` | `{"kind":"exact"}` or `{"kind":"short", requested, returned, shortfallReason}`. `corpus` means the index found nobody else. `coverage` means people matched and could not be returned, so page on. |
| `cursor` | Pass it back for the next page. `null` means no continuation. |
| `places_resolved`, `ids_resolved` | How each place and name in the filters was read. |

Errors you can fix carry `error` and a `hint` that says what to change. The v1 routes carry a
stable `code` and a `message`. Branch on those.

## 4. Narrow with filters

A filter is `[field, Operator, value]`. Combine with `["And", [...]]`, `["Or", [...]]` and
`["Not", f]`. Names resolve for you: `{"place": [...]}`, `{"company": [...]}`, `{"school": [...]}`.
An unknown name is a 400 that lists the closest known ones.

```bash
# a place: a city means its metro area
vamoPost "/v2/developers/search" '{"filters": ["location_ids", "ContainsAny", {"place": ["<City>"]}], "rank_by": ["v", "ANN", ["Embed", "platform infrastructure"]], "limit": 3}'
# the city alone
vamoPost "/v2/developers/search" '{"filters": ["location_ids", "ContainsAny", {"place": ["<City>"], "scope": "city"}], "rank_by": ["v", "ANN", ["Embed", "platform infrastructure"]], "limit": 3}'
# writes a language well
vamoPost "/v2/developers/search" '{"filters": ["person_languages", "ContainsAny", ["go:strong", "go:primary", "rust:strong", "rust:primary"]], "rank_by": ["v", "ANN", ["Embed", "platform infrastructure"]], "limit": 3}'
# a reputation band
vamoPost "/v2/developers/search" '{"filters": ["And", [["devrank", "Gte", 60], ["devrank", "Lte", 85]]], "rank_by": ["v", "ANN", ["Embed", "distributed systems"]], "limit": 3}'
# people only: no bots, no organization accounts
vamoPost "/v2/developers/search" '{"filters": ["And", [["is_bot", "Eq", false], ["is_org_account", "Eq", false]]], "rank_by": ["v", "ANN", ["Embed", "training infrastructure"]], "limit": 3}'
```

Put `["is_bot", "Eq", false]` and `["is_org_account", "Eq", false]` in every search for people.
`Lt`, `Lte` and `Not` keep people with no value. Add `["devrank", "NotEq", null]` when the band is a
hard requirement.

## 5. Filter on professional detail

These resolve from linked professional profiles, so they match the developers who have one and
return smaller pages.

```bash
# worked at a company, now or before
vamoPost "/v2/developers/search" '{"filters": ["former_company_ids", "ContainsAny", {"company": ["<Company>"]}], "rank_by": ["v", "ANN", ["Embed", "backend services"]], "limit": 3, "depth": "enriched"}'
# works there now; past_company_ids for people who have left
vamoPost "/v2/developers/search" '{"filters": ["current_company_ids", "ContainsAny", {"company": ["<Company>"]}], "sort": "devrank", "limit": 3, "depth": "enriched"}'
# drop anyone currently at a company
vamoPost "/v2/developers/search" '{"filters": ["Not", ["current_company_ids", "ContainsAny", {"company": ["<Company>"]}]], "rank_by": ["v", "ANN", ["Embed", "platform infrastructure"]], "limit": 3}'
# school and graduation year
vamoPost "/v2/developers/search" '{"filters": ["And", [["school_ids", "ContainsAny", {"school": ["<University>"]}], ["graduation_year", "Gte", 2024]]], "rank_by": ["v", "ANN", ["Embed", "compiler"]], "limit": 3, "depth": "enriched"}'
# role family, level and title words
vamoPost "/v2/developers/search" '{"filters": ["And", [["title_function", "In", ["software_eng", "infra"]], ["title_level", "In", ["staff", "principal"]], ["current_title", "ContainsAnyToken", "founding"]]], "rank_by": ["v", "ANN", ["Embed", "distributed systems"]], "limit": 3, "depth": "enriched"}'
```

`GET /v2/developers/fields` lists every field with its operators, its status and its coverage. A
field below `live` runs on partial data and is named in the response's `not_live`.

## 6. Check who is reachable

Every result carries `hasEmail` and `hasLinkedin`. Filter on them, then read the matched LinkedIn
facts under `details.identity`. Email addresses come from their own call.

```bash
# only developers with an email on file
vamoPost "/v2/developers/search" '{"filters": ["has_email", "Eq", true], "rank_by": ["v", "ANN", ["Embed", "data pipelines"]], "limit": 3}'
# only developers with a matched LinkedIn profile
vamoPost "/v2/developers/search" '{"filters": ["has_linkedin", "Eq", true], "rank_by": ["v", "ANN", ["Embed", "data pipelines"]], "limit": 3}'
# every email address observed for a developer
vamo "/v2/developers/emails?logins=<login>"
```

## 7. Search by repository, keyword and activity

```bash
# contributors to a repository (role: owner, contributor or either)
vamoPost "/v2/developers/search" '{"repos": {"names": ["<owner/name>"], "role": "contributor"}, "sort": "devrank", "limit": 3}'
# people who worked alongside that repository's people
vamoPost "/v2/developers/search" '{"repos": {"names": ["<owner/name>"], "hops": 2}, "limit": 3}'
# people who build things like a repository
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", {"like": ["<owner/name>"]}], "limit": 3}'
# contributed to any repository of a GitHub organization
vamoPost "/v2/developers/search" '{"filters": ["contributed_repo_ids", "ContainsAny", {"repos_of": "<org>"}], "sort": "devrank", "limit": 3}'
# a term the phrase may not carry, fused with the phrase
vamoPost "/v2/developers/search" '{"queries": [{"rank_by": ["v", "ANN", ["Embed", "game theory solver"]]}, {"rank_by": ["all_repo_text", "BM25", "cfr"]}], "fuse": ["RRF", {"weights": [1, 1]}], "limit": 3}'
# popularity of their own work, and recent activity
vamoPost "/v2/developers/search" '{"filters": ["And", [["owned_stars_max", "Gte", 1000], ["last_active_at", "Gte", "2026-01-01T00:00:00Z"]]], "rank_by": ["v", "ANN", ["Embed", "frontend build tooling"]], "limit": 3}'
```

Up to three lanes go under `queries`, each with its own `filters` and `rank_by`.

## 8. Sort results

`sort` orders the people a search found, strongest first: `relevance` (default), `devrank`,
`stars`, `followers`, `recent`. With no phrase and no `rank_by` it orders the whole filtered pool.

```bash
vamoPost "/v2/developers/search" '{"filters": ["And", [["devrank", "Lte", 88], ["devrank", "NotEq", null], ["is_bot", "Eq", false]]], "sort": "devrank", "limit": 10}'
vamoPost "/v2/developers/search" '{"filters": ["location_ids", "ContainsAny", {"place": ["<City>"]}], "sort": "followers", "limit": 10}'
```

## 9. Page through results

```bash
# run the search, read .cursor off the response
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "rust"]], "limit": 10}'
# send the same body with the cursor for the next page
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "rust"]], "limit": 10, "cursor": "'"$CURSOR"'"}'
# already hold some ids? leave them out (up to 1000)
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "rust"]], "limit": 10, "exclude": ["12345", "67890"]}'
```

A cursor belongs to the query that produced it: the same body with another cursor is a 400.
`limit` goes from 1 to 100.

## 10. Choose a depth

Same query, three tiers. Each tier adds data to every row.

```bash
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "react performance"]], "limit": 3, "depth": "core"}'      # profile, top repos, match, evidence
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "react performance"]], "limit": 3, "depth": "enriched"}'  # adds title, company, school, recent roles, socials, location
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "react performance"]], "limit": 3, "depth": "deep"}'      # adds the contribution garden
```

At `deep` the garden arrives as a compact `gardenSummary` (`activeWeeks`, `last90Days`,
`lastActiveDay`). Send `"garden": "full"` for the day-by-day heatmap. `repoLimit` (1 to 12,
default 4) sets how many top repositories come back per developer.

## 11. Add AI facets

`facets` requests optional add-ons, up to five per call. They land under `details.ai`. They
resolve in the background, so send the same body twice: the first read is `pending`, the second
is `ok` with a `value`.

```bash
# a short bio plus a summary of their top repos
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "typescript build tooling"]], "facets": ["ai.person_summary", "ai.repo_summaries"], "limit": 3}'
# why this person matches the ask
vamoPost "/v2/developers/search" '{"ask": "staff developer for a high-throughput payments platform in go", "rank_by": ["v", "ANN", ["Embed", "payments platform in go"]], "facets": ["ai.match_rationale"], "limit": 3}'
# subject and technology tags on each repo
vamoPost "/v2/developers/search" '{"rank_by": ["v", "ANN", ["Embed", "query engine"]], "facets": ["tags.repos"], "limit": 3}'
```

`ai.match_rationale` returns `{ matched, reasons }`. Check `matched` before reading `reasons`.

## 12. Look up developers you already know

By login, LinkedIn profile or id, up to 25 inputs per call. There is no query, so there is no
`match` block. Results come back in the order you sent.

```bash
vamoPost "/v2/developers" '{"logins": ["<login>", "<login>"], "depth": "enriched"}'
vamoPost "/v2/developers" '{"linkedin": ["https://www.linkedin.com/in/<slug>"], "depth": "enriched"}'
# the same by query string
vamo "/v2/developers/enrich?logins=<login>,<login>&depth=enriched"
```

To turn names into ids before a search, `POST /v2/developers/resolve` with
`{"place": [...], "company": [...], "school": [...]}`.

## 13. Find similar developers

Give it one seed and get back people who build like them. `intent` is `same` (the same kind of
work), `overall` or `network` (shared employers and repositories). `evidence.matches[].lane` says
which part of the seed's work each person matched.

```bash
vamoPost "/v2/developers/similar" '{"like_person": "<login>", "intent": "same", "limit": 5, "depth": "core"}'
# the same with the seed in the path, kept to one place
vamoPost "/v2/developers/<login>/similar" '{"intent": "same", "filters": ["location_ids", "ContainsAny", {"place": ["<City>"]}], "limit": 5}'
```

## 14. Get a quick summary

```bash
vamo "/v2/developers/summaries?logins=<login>,<login>"
```

## 15. Research a developer or a repository in depth

A job that saves a full report to the account. Start it, poll it, then read the report whenever
you need it.

```bash
# a developer
vamoPost "/v2/deep-research/jobs" '{"subject":"developers","logins":["<login>"]}'
vamo "/v2/deep-research/jobs/$JOB_ID"
vamo "/v2/deep-research/reports/developers/<login>"

# a repository: who builds it and who its audience is
vamoPost "/v2/deep-research/jobs" '{"subject":"repos","repos":["<owner/name>"]}'
vamo "/v2/deep-research/reports/repos/<owner>/<name>"
```

Up to 25 subjects per job. Polling the job also advances it, so keep polling until it finishes.

If the start answers `409` with `reason: GITHUB_CONNECTION_REQUIRED`, the member this key acts for
has no GitHub connected. Read the link out of the body and give it to the person:

```bash
vamoPost "/v2/deep-research/jobs" '{"subject":"developers","logins":["<login>"]}' | jq -r '.connectUrl // .message'
```

They open it in any browser and approve on GitHub. No Vamo sign-in is needed, and the link works
for 15 minutes. When they say it is done, run the same start again.

## 16. Score people against a role

Send up to 50 logins and the role text. Results come back best fit first with `fit` (0 to 2),
`gettable`, `bridgeable`, `confidence` and a short `bridge` reason.

```bash
vamoPost "/v1/fit-rank" '{"logins":["<login>","<login>"],"role":"<the role, in a few sentences or the full job description>","company":"<hiring company>"}'
```

---

## Wire it into an agent

MCP server at `https://mcp.vamotalent.ai/mcp/search` (Streamable HTTP, same key). Fastest setup:
paste one line into your agent.

```
Fetch https://vamotalent.ai/agent-setup/search/prompt.md and follow the instructions
```

## Status codes

| Code | Meaning |
| --- | --- |
| `400` | The body is wrong. `hint` says what to change. `POST /v2/developers/search/validate` checks a body without running it |
| `401` | No credential, or an invalid one |
| `403` | The key lacks the entitlement this route needs |
| `402` | The plan does not include this capability |
| `404` | No such route or record. On a `/v2/developers` route on production, the v2 engine is not on yet: use v1 |
| `429` | A rate limit or quota is exhausted. Search allows 10 requests per second per key. Wait for `Retry-After` |
| `503` | On a `/v2/developers` route, the v2 engine is not available on this host. Use the v1 route and say so |
