---
name: vamo-search
description: Use when searching for software developers with Vamo, from a technology, a company, a repository, a place, one great person or a whole job description. Covers turning intake notes into a search spec (lanes, gates, rank signals), covering a broad topic with many queries without missing the famous items, running the search, and reading results correctly. Also use when a filter seems ignored, a page comes back short, the same people repeat, strong developers are missing, or results are celebrity maintainers, thin profiles or keyword noise. Triggers "find engineers who", "who built X", "find more like this person", "here is the job description", "turn these intake notes into a search", "what should we search for this req", "find the best N", "make sure we don't miss anyone", "source for this role".
metadata:
  version: "3.1.0"
  updated: "2026-10-14"
---

# Vamo Search

How an agent uses the Vamo developer search API (v2) and reads its results correctly.

Vamo is a developer talent search engine over GitHub proof-of-work joined to professional
history. You send one JSON body: facts as filters, the work as a short phrase. It returns real
people with the repos and roles that prove the claim.

Base URL `https://api.vamotalent.ai`. Machine-readable spec:
`https://api.vamotalent.ai/openapi.json`. The fields a search may use, with their operators,
are listed live at `GET /v2/developers/fields`. **When this skill and the API disagree, the API
wins.**

Everything below is enough to search with one request and no other reading. `vamo-setup`
gets a person connected and covers direct access over HTTP. `vamo-troubleshooting` covers errors
and a connection that stops working. Five reference files go deeper:

- `references/discovery-recipes.md`: twelve starting points and the request for each. **Start
  here when someone asks to find people.**
- `references/sourcing-guide.md`: the full method for a whole role. Sizing the funnel, the eight
  qualification questions, ranking and diversifying, reading a developer's signals, playbooks,
  and worked reasoning traces.
- `references/domain-library.md`: phrasings of the work for fifty domains.
- `references/role-decomposition.md`: turning a job description and intake notes into a search
  spec (lanes, gates, rank signals, exclusions) before any search runs. A worked example is in
  `references/role-decomposition-example.md`.
- `references/fanout.md`: covering a broad topic with many queries plus the famous items keyword
  search misses, then ranking the union.

**With the Vamo MCP tools.** If your tool list has the Vamo tools, use them to make the calls.
They hold the credential, so skip **Auth** below, and they take the same bodies as the API:

| MCP tool | Same as |
| --- | --- |
| `search` | `POST /v2/developers/search` (and `/aggregate` with `group_by`) |
| `similar` | `POST /v2/developers/similar` |
| `enrich` | `POST /v2/developers` (logins, LinkedIn profiles or ids, at a depth) |
| `deep_research` | `/v2/deep-research` (start a job, check it, read a report) |

Email addresses and summaries are API calls only. Everything else in this skill applies
unchanged.

---

## Auth

```
Authorization: Bearer vamo_sk_...
Content-Type: application/json
```

Search routes allow 10 requests per second per key. Parallel agents on one key share it.

---

## Pick the right door

| You want | Call |
| --- | --- |
| People matching facts and a description of work | `POST /v2/developers/search` |
| More people like one person | `POST /v2/developers/similar` |
| Counts by a field (sizing a market, where talent is) | `POST /v2/developers/aggregate` |
| More depth on people you already hold | `GET /v2/developers/enrich?logins=a,b&depth=enriched` (or `ids=`, 25 per call) |
| Look up by LinkedIn profile, login or id | `POST /v2/developers` with `{"linkedin": [...], "logins": [...], "ids": [...], "depth": "enriched"}` |
| Email addresses | `GET /v2/developers/emails?logins=a,b` |

| A short written summary per person | `GET /v2/developers/summaries?logins=a,b` |
| People ranked against a role text | `POST /v1/fit-rank` (logins you hold, 50 per call). It has no v2 path yet |
| A full report on a person or a repository | `POST /v2/deep-research/jobs` with `{"subject": "developers", "logins": [...]}` or `{"subject": "repos", "repos": ["owner/name"]}`, then `GET /v2/deep-research/jobs/{id}` and read each item's `reportPath` |
| The fields and their operators | `GET /v2/developers/fields` |

Deep research and fit-rank work on people you already hold. They find nobody new. Use `enrich`
to deepen a row. Re-running the search for more depth returns a different page.

---

## The request

```json
{"filters": [...], "rank_by": [...], "repos": {...}, "sort": "devrank", "limit": 20, "depth": "core"}
```

At least one of `filters`, `rank_by` or `repos` is required. `limit` is people, 1 to 100.

- **Facts are filters.** Place, employer, school, title, seniority, languages, graduation year,
  reputation. A filter is `[field, Operator, value]`; combine with `["And", [...]]`,
  `["Or", [...]]`, exclude with `["Not", f]`.
- **The work is one short phrase** in a vector lane:
  `"rank_by": ["v", "ANN", ["Embed", "low-latency audio streaming"]]`. Never put a place, an
  employer or a seniority word in it.
- **Jargon the phrase may not carry** (a protocol name, an acronym): a keyword lane
  `["all_repo_text", "BM25", "gto"]`, fused with the phrase lane (below).
- **No work to match, and you want the strongest people:** `"sort": "devrank"` (also
  `followers`, `stars`, `recent`).
- **People only:** always add `["is_bot", "Eq", false]` and `["is_org_account", "Eq", false]`.

Filters. Names resolve to ids for you; an unknown name is a 400 that lists the closest known
names.

| Want | Filter |
| --- | --- |
| A place. A city means its metro area | `["location_ids", "ContainsAny", {"place": ["Denver"]}]`; the city itself: `{"place": ["Denver"], "scope": "city"}` |
| Worked at a company, now or before | `["former_company_ids", "ContainsAny", {"company": ["<Company>"]}]` |
| Works there now | `["current_company_ids", "ContainsAny", {"company": ["<Company>"]}]` |
| Left it | `["past_company_ids", "ContainsAny", {"company": ["<Company>"]}]` |
| School | `["school_ids", "ContainsAny", {"school": ["<University>"]}]` |
| Graduation year | `["graduation_year", "Gte", 2023]` |
| Role family | `["title_function", "In", ["software_eng", "infra", "ml_eng"]]` |
| Title level | `["title_level", "In", ["senior", "staff", "principal"]]` |
| Title words | `["current_title", "ContainsAnyToken", "founding"]` |
| Writes a language | `["person_languages", "ContainsAny", ["rust:strong", "rust:primary"]]` (levels `some`, `strong`, `primary`) |
| Reputation band | `["devrank", "Gte", 70]` and `["devrank", "Lte", 88]` |
| Popularity of their own work | `["owned_stars_max", "Gte", 100]` (their best repo) |
| Contributed to the repos an org or person owns | `["contributed_repo_ids", "ContainsAny", {"repos_of": "<owner login>"}]` (one repository: the `repos` clause) |

`title_function` values: software_eng, product_eng, infra, eng_mgmt, ml_eng, ai_research,
research, data_eng, data_sci, data_analyst, security, qa, devrel, forward_deployed, solutions,
customer_eng, it_ops, hardware, product, design, program_mgmt, founder, exec, mgmt_other,
academia, student, nontech. `title_level` values: intern, junior, mid, senior, staff, principal,
distinguished, exec. Any other field: `GET /v2/developers/fields`.

Repositories:

| Want | Body |
| --- | --- |
| Contributed to, or owns, a repo | `"repos": {"names": ["<owner/name>"], "role": "contributor"}` (`owner`, `either`) |
| Worked alongside the people on a repo | `"repos": {"names": ["<owner/name>"], "hops": 2}` |
| Built things like a repo | `"rank_by": ["v", "ANN", {"like": ["<owner/name>"]}]` |

Two or three angles in one request: `"queries": [{lane}, {lane}]` with
`"fuse": ["RRF", {"weights": [1, 1]}]`. Each lane carries its own `filters` and `rank_by`. At most
three lanes.

More like one person: `POST /v2/developers/similar` with
`{"like_person": "<login>", "intent": "same", "limit": 20}`; `intent` is `same` (the same kind of
work), `overall` or `network`. Add `filters` to keep it to a place or a company.

---

## The rules that are easy to miss

- **`Lt` and `Lte` keep people with no value.** `["devrank", "Lte", 88]` also returns people with
  no devRank. Add `["devrank", "NotEq", null]` when the field is a hard requirement. `Not` keeps
  unknowns too.
- **Professional facts reach people with a linked professional profile.** Employer, title,
  school and graduation filters drop strong builders with no linked profile. Run a second pass
  on the work alone and join on `id`.
- **A city is its metro.** "Denver" includes Boulder. `places_resolved` in the response says how
  each place was read. Add `"scope": "city"` only when the ask means the city itself.
- **"Ex-X" means worked there, now or before.** `former_company_ids` covers both. Use
  `past_company_ids` only for people who have left.
- **`exclude` is how "fifty more" works**, and `cursor` is how the next page works. Pass the ids
  you hold in `exclude`, or the previous page's `cursor` with the same body.
- **A `cursor` belongs to the query that produced it.** Another body with that cursor is a 400.

---

## Reading a result

| Field | What it tells you |
| --- | --- |
| Row order | The ranking. Best match first. |
| `evidence.matches[]` | Why this person matched: the repo (`full_name`), the role (`company`, `title`, years) or the profile, with `similarity` for a phrase lane. Your citation. |
| `match.repos[]` | The matched repositories: `fullName`, `stars`, `language`, `role`. |
| `index.profile` | The card the search ran on: login, name, location, devrank, followers, languages; at `enriched` also title, company, school, graduation year, LinkedIn. |
| `index.recent_roles` | Newest first (at `enriched` or `deep`). Trust these over a headline. |
| `index.top_repos` | Their strongest repositories. |
| `id` | GitHub's numeric user id as a string. Stable across renames. Dedupe on it. |
| `countStatus` | `exact`, or `short` with `requested`, `returned` and `shortfallReason`. |
| `cursor` | The next page. `null` means no more for this query. |
| `places_resolved`, `ids_resolved` | How each place and name was read. |
| `details.*` | The developer namespaces at the depth asked. An absent namespace is unknown. |

| `shortfallReason` | Meaning | Next move |
| --- | --- | --- |
| `corpus` | Nobody else matches | Stop paging this query. Widen it. |
| `coverage` | People matched and could not be returned | Page on |

Report a target as met only when the rows you hold meet it.

A missing value, a null location, an empty education list: each means the data is silent. Carry
it as unknown through your ranking. Drop on unknown only when the requirement is a hard gate and
the person asking has said so.

---

## Depth

| Depth | Adds |
| --- | --- |
| `core` | Profile, top repositories, the match and evidence, reputation |
| `enriched` | Title, company, school and recent roles on the card, LinkedIn identity, experience, education, socials, resolved location |
| `deep` | The contribution garden, as `gardenSummary` by default or the full heatmap with `garden=full` |

Search wide at `core`, decide who matters, then `enrich` the survivors at the depth you need. Ask
for `enriched` on the search itself when the answer is about employer, title or school.
`facets` adds `ai.person_summary`, `ai.repo_summaries`, `ai.match_rationale` and `tags.repos` on
top of any depth. AI facets resolve in the background: the first read is `pending`, a second read
returns the value.

---

## Fan out: one query is a starting point

A role description is a topic. `references/fanout.md` covers the general method. Applied here:

1. **Decompose the role into lanes**, each named by an artifact a strong person would have built.
   `references/role-decomposition.md` does this from intake notes.
2. **Write several phrasings of the work per lane**, one idea each, and run each as its own
   search, or two or three as fused lanes in one request.
3. **Vary the lever as well as the words.** A `repos` search, a `like` lane and a phrase lane for
   the same concept return substantially different people.
4. **Seed the known items.** Name the repositories that define the space and search on them with
   `repos` or `like`. Phrase search under-retrieves canonical projects because everyone else's
   description of them outranks the thing itself.
5. **Walk the graph.** Call `/v2/developers/similar` on every strong hit.
6. **Page with `cursor`, or `exclude`** carrying everything you hold.
7. **Dedupe on `id`.** People rename their logins.
8. **Cut on evidence you read**: the matched repos and roles, the band, the gates. Row order is
   relative to one query and does not compare across queries.

---

## Failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| A 400 naming a field | The field is unknown or disabled, or the operator does not apply | Use the closest name in the hint, or check `GET /v2/developers/fields` |
| A 400 naming a place or company | The name did not resolve | Use the closest name in the hint |
| Pages shrink to a handful | A professional filter restricted the pool to linked profiles | Run it as a separate pass, join on `id` |
| Same people on every page | Neither `cursor` nor `exclude` sent | Send one of them |
| Great developers missing | One query, no seeds, no graph walk | Fan out, seed `repos`, walk `similar` |
| Tutorials and lists at the top | The phrase names a topic | Describe an artifact and its mechanism |
| Place or employer words in the phrase | The vector drifts | Move them into `filters` |
| Celebrity maintainers on top | No ceiling on reputation | Add `["devrank", "Lte", 88]` with `["devrank", "NotEq", null]` |
| `ai.*` value missing | Facet still `pending` | Read the same request again |
| A 504 | A cold start | Send the same request once more |

---

## Reporting rules

When handing results to a person:

- **Cite the evidence.** Every claim about a developer traces to `evidence.matches`, `match.repos`
  or a field you read. Say what they built and how it works.
- **Say what you filtered and what you confirmed.** A filter you sent and a field you verified
  are different claims. Name which one backs each requirement.
- **Carry unknowns visibly.** Mark an unverified location or seniority as unverified.
- **Declare what you left out**: pages you did not fetch, lanes that ran thin, people you cut and
  why.

---

## Drop-in prompt

```
You are sourcing developers with the Vamo API (https://api.vamotalent.ai, bearer vamo_sk_ key,
10 search requests per second per key). Fields: GET /v2/developers/fields. The API wins over
memory.

1. PICK THE DOOR. New people: POST /v2/developers/search. More like one person:
   POST /v2/developers/similar. Counts: POST /v2/developers/aggregate. Depth on people you
   hold: GET /v2/developers/enrich. Addresses: GET /v2/developers/emails. With the Vamo MCP
   tools, the same bodies go to the search, similar, enrich and deep_research tools.

2. WRITE ONE BODY. Facts are filters ([field, Op, value], And/Or/Not; names resolve:
   {"place": [...]}, {"company": [...]}, {"school": [...]}). The work is one short phrase:
   rank_by [v, ANN, [Embed, "..."]]. No work to match: sort devrank. Repos: "repos" or
   {"like": [...]}. Always is_bot false and is_org_account false.

3. FAN OUT. Split the role into lanes named by artifacts. Several phrasings per lane. Seed the
   canonical repos of the space. Call similar on every strong hit. Page with cursor or exclude.

4. READ RESULTS CORRECTLY. Row order is the ranking. evidence.matches says why each person
   matched. Read countStatus before claiming a target: only `corpus` means exhausted. Dedupe on
   id. An absent value is unknown. Lt/Lte and Not keep unknowns.

5. GO DEEP LAST. Search at depth core, or enriched when the ask is about employer, title or
   school. Enrich only the survivors. Request ai.* facets twice: pending first, value second.

6. REPORT. Cite the evidence for every person. Separate what you filtered from what you
   confirmed. Mark unknowns. Declare pages not fetched, thin lanes and cuts.
```
