# Vamo Developer API: curl walkthrough

Reference for the `vamo-api-access` skill. Sixteen steps, in order, cover the whole API. These are worked
examples written against the spec on 2026-10-09. Check a parameter in the spec before relying on
it.

Values in angle brackets are yours to fill in: `<login>` is a GitHub username, `<owner/name>` a
repository, `<org>` a GitHub organization, `<company>` and `<school>` plain names in lowercase.

- Base URL `https://api.vamotalent.ai`
- Docs `https://api.vamotalent.ai/docs`
- Machine-readable spec `https://api.vamotalent.ai/openapi.json`. It is generated from the API, so
  it wins over this file when they disagree.

---

## 1. Load your key and set up two helpers

Getting access and storing it safely are covered in the `vamo-api-access` skill. With the key in
`VAMO_API_KEY`:

```bash
vamo()     { curl -s "https://api.vamotalent.ai$1" -H "Authorization: Bearer $VAMO_API_KEY"; }
vamoPost() { curl -s -X POST "https://api.vamotalent.ai$1" -H "Authorization: Bearer $VAMO_API_KEY" -H "content-type: application/json" -d "$2"; }
```

The helpers are shell shorthand. A plain `curl -s "..." -H "Authorization: Bearer $VAMO_API_KEY"`
works the same anywhere.

## 2. Run a first search

`q` is plain language. Describe the work.

```bash
vamo "/v1/developers/search?q=rust+systems+programmer&limit=3"
```

## 3. Read the response

```bash
vamo "/v1/developers/search?q=lsm-tree+storage+engine,+compaction&limit=5" \
  | jq '{count: .countStatus, next: .cursor, people: [.results[] | {id, login, name, hasEmail, why: [.match.repos[]?.fullName]}]}'
```

| Field | Meaning |
| --- | --- |
| `results[]` | Developers, best match first. The order is the ranking. |
| `id`, `login`, `name`, `hasEmail`, `hasLinkedin`, `hasLocation` | The identity spine on every row. `id` is GitHub's numeric user id as a string and survives renames. |
| `match.repos[]` | Why this person came back: `fullName`, `stars`, `language`, `role` (`owner` or `contributor`). |
| `match.status` | `attributed` or `unattributed`. Unattributed means this page carries no repo attribution. It says nothing about match strength. |
| `details` | Keyed by namespace: `githubProfile.core`, `githubProfile.repos`, `score.cracked`, `identity.linkedin`, `identity.experience`, `identity.education`, `contact.socials`, `contact.location`, `contact.emails`, `github.gardenSummary`, `ai.*`. A namespace appears only when resolved. |
| `countStatus` | `{"kind":"exact"}` or `{"kind":"short", requested, returned, shortfallReason}`. Only a `corpus` reason means the index is exhausted. For any other reason, ask again with the `cursor`. |
| `cursor` | Pass it back for the next page. `null` means no continuation. |

Errors carry a stable `code`, a `message` and often a `remedy`. Branch on `code`.

## 4. Narrow with filters

Filters sit on top of `q`, or work with no `q` at all.

```bash
# language and country
vamo "/v1/developers/search?q=platform+engineer&lang=go,rust&country=united+states&limit=3"
# city
vamo "/v1/developers/search?q=platform+engineer&city=san+francisco,new+york&limit=3"
# current company
vamo "/v1/developers/search?q=infrastructure+engineer&company=<company>&limit=3"
# a past employer
vamo "/v1/developers/search?q=backend+engineer&pastCompanies=<company>,<company>&limit=3"
# drop anyone currently at these companies
vamo "/v1/developers/search?q=platform+engineer&excludeCurrentCompanies=<company>,<company>&limit=3"
# a cracked score band
vamo "/v1/developers/search?q=distributed+systems&minCracked=60&maxCracked=85&limit=3"
# seed repositories: people who build comparable things
vamo "/v1/developers/search?q=training+infrastructure&repos=<owner/name>,<owner/name>&limit=3"
```

`lang`, `country` and `city` filter on evidence: a developer with no data on file for that field
is left in. Add `requireLocation=true` when you can only act on people you can place.

## 5. Filter on professional detail

These resolve from linked professional profiles, so they match the developers who have one and
return smaller pages.

```bash
vamo "/v1/developers/search?q=distributed+systems&titles=staff+engineer&companySize=51-200&yoeMin=8&limit=3"
vamo "/v1/developers/search?q=compiler+engineer&schools=<school>&experienceTier=early&depth=enriched&limit=3"
```

Others in this family: `industries`, `peerCompanies`, `yoeMax`, `openToWork`, `state`.

## 6. Check who is reachable

Every result carries `hasEmail` and `hasLinkedin`. Filter on them, then read the matched LinkedIn
facts under `details.identity`. Email addresses come from their own call.

```bash
# only developers with an email on file
vamo "/v1/developers/search?q=data+engineer&requireEmail=true&limit=3"
# only developers with a matched LinkedIn profile
vamo "/v1/developers/search?q=data+engineer&requireLinkedin=true&limit=3"
# every email address observed for a developer
vamo "/v1/developers/emails?logins=<login>"
```

## 7. Use hard filters across the whole index

These apply to the whole population before ranking. They compose with each other and with `q`.

```bash
# minimum total stars across their repos
vamo "/v1/developers/search?q=rust+systems+programmer&minStars=10000&limit=3"
# technologies tagged on their work
vamo "/v1/developers/search?q=backend+engineer&techs=rust,go&limit=3"
# subject tags
vamo "/v1/developers/search?q=database+internals&subjects=distributed-systems&limit=3"
# cracked tier: developing, intermediate, advanced, expert, elite
vamo "/v1/developers/search?q=machine+learning&tier=elite&limit=3"
# pushed code on or after this date
vamo "/v1/developers/search?q=frontend+engineer&pushedAfter=2026-01-01&limit=3"
# associated with this GitHub org, no query needed
vamo "/v1/developers/search?orgs=<org>&limit=3"
# employer inferred from GitHub activity
vamo "/v1/developers/search?q=payments+infrastructure&employer=<company>&limit=3"
# leave very high-profile accounts out
vamo "/v1/developers/search?q=react+state+management&hideHighProfile=true&limit=3"
```

## 8. Sort results

`sortBy` orders by one numeric fact, strongest first: `crackedScore`, `followers`, `following`,
`total_stars`, `repo_count`, `contributions_last_year`, `last_pushed_at`. It works with no query.

```bash
vamo "/v1/developers/search?sortBy=crackedScore&maxCracked=88&limit=10"
vamo "/v1/developers/search?tier=elite&sortBy=followers&limit=10"
```

## 9. Page through results

```bash
# run the search, read .cursor off the response
vamo "/v1/developers/search?q=rust+engineer&limit=10"
# pass the cursor back for the next page
vamo "/v1/developers/search?q=rust+engineer&limit=10&cursor=$CURSOR"
# already hold some ids? leave them out
vamo "/v1/developers/search?q=rust+engineer&exclude=12345,67890&limit=10"
```

A cursor belongs to the query that produced it. `limit` goes from 1 to 250, default 25.

## 10. Choose a depth

Same query, three tiers. Each tier adds data to every row.

```bash
vamo "/v1/developers/search?q=react+performance&depth=core&limit=3"       # profile, top repos, match, cracked score
vamo "/v1/developers/search?q=react+performance&depth=enriched&limit=3"   # adds LinkedIn identity, socials, location
vamo "/v1/developers/search?q=react+performance&depth=deep&limit=3"       # adds the contribution garden
```

At `deep` the garden arrives as a compact `gardenSummary` (`activeWeeks`, `last90Days`,
`lastActiveDay`). Send `garden=full` for the day-by-day heatmap. `repoLimit` (1 to 12, default 4)
sets how many top repositories come back per developer.

## 11. Add AI facets

`facets` requests optional add-ons, up to five per call. They land under `details.ai`. They
resolve in the background, so call the same query twice: the first read is `pending`, the second
is `ok` with a `value`.

```bash
# a short bio plus a summary of their top repos
vamo "/v1/developers/search?q=typescript+build+tooling&facets=ai.person_summary,ai.repo_summaries&limit=3"
# why this person matches the query
vamo "/v1/developers/search?q=staff+engineer+for+a+high+throughput+payments+platform+in+go&facets=ai.match_rationale&limit=3"
# subject and technology tags on each repo
vamo "/v1/developers/search?q=query+engine&facets=tags.repos&limit=3"
```

`ai.match_rationale` returns `{ matched, reasons }`. Check `matched` before reading `reasons`.

## 12. Look up developers you already know

Enrich by login or id, up to 25 per call. There is no query, so there is no `match` block.

```bash
vamo "/v1/developers/enrich?logins=<login>,<login>&depth=enriched"
```

## 13. Find similar developers

Give it one seed and get back people who build like them, each with a `whySimilar` line.

```bash
vamo "/v1/developers/similar?login=<login>&limit=5&depth=core"
```

## 14. Get a quick summary

```bash
vamo "/v1/developers/summaries?logins=<login>,<login>"
```

## 15. Research a developer or a repository in depth

A job that saves a full report to the account. Start it, poll it, then read the report whenever
you need it.

```bash
# a developer
vamoPost "/v1/deep-research/jobs" '{"subject":"developers","logins":["<login>"]}'
vamo "/v1/deep-research/jobs/$JOB_ID"
vamo "/v1/deep-research/reports/developers/<login>"

# a repository: who builds it and who its audience is
vamoPost "/v1/deep-research/jobs" '{"subject":"repos","repos":["<owner/name>"]}'
vamo "/v1/deep-research/reports/repos/<owner>/<name>"
```

Up to 25 subjects per job. Polling the job also advances it, so keep polling until it finishes.

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
| `401` | No credential, or an invalid one |
| `403` | The key lacks the entitlement this route needs |
| `402` | The plan does not include this capability |
| `429` | A rate limit or quota is exhausted. Each route's limit is in its `x-vamo.rateLimit` block in the spec |
