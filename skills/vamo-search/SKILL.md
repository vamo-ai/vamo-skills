---
name: vamo-search
description: Use when searching for software engineers, sourcing candidates for a role, or enriching developer profiles through the Vamo API, and the question is which endpoint or filter to use or how to read what came back. Also use when a filter seems ignored, a page comes back short, the same people repeat across pages, or strong engineers are missing from results. Triggers "find engineers who", "source for this role", "who built X", "enrich these developers", "get emails for".
metadata:
  version: "1.1.1"
  updated: "2026-10-09"
---

# Vamo Search

How an agent uses the Vamo developer search API and reads its results correctly.

Vamo is a developer talent search engine over GitHub proof-of-work. You describe who you want in
plain language. It returns real people with the repos that prove the claim.

Base URL `https://api.vamotalent.ai`. Machine-readable spec:
`https://api.vamotalent.ai/openapi.json`. Every operation carries an `x-vamo` block with its
access level and rate limit. **When this skill and the spec disagree, the spec wins.**

`vamo-api-access` covers setup, access and errors, with a curl walkthrough of every route. `role-decomposition` turns a role
into a search spec. `vamo-sourcing-agent` runs that spec into a shortlist.

---

## Auth

```
Authorization: Bearer vamo_sk_...
```

Search routes share one rate limit of **30 requests per minute per account**. Parallel agents on
one account share it, so a fan-out of thirty queries needs throttling.

---

## Pick the right door

| You want | Call |
| --- | --- |
| People matching a description of work | `GET /v1/developers/search` |
| More depth on rows you already hold | `GET /v1/developers/enrich` (ids or logins, 25 per call) |
| More people like one person | `GET /v1/developers/similar` |
| Email addresses | `GET /v1/developers/emails` |
| A short written summary per person | `GET /v1/developers/summaries` |
| People ranked against a role text | `POST /v1/fit-rank` (logins you hold, 50 per call) |
| A full report on a person or a repository | `POST /v1/deep-research/jobs`, then read the report |

Deep research and fit-rank work on people you already hold. They find nobody new. Use `enrich` to
deepen a row. Re-running the search for more depth returns a different page.

---

## The lever model

`q` carries the intent. Every other parameter narrows it. Either `q` or one narrowing parameter is
required.

Levers fall into two families, and the family decides how much of the population a filter can
see.

**GitHub-native levers reach everyone in the index:**
`lang`, `skills`, `repos`, `subjects`, `techs`, `orgs`, `employer`, `minCracked`, `maxCracked`,
`tier`, `minStars`, `maxStars`, `minFollowers`, `minRepos`, `maxRepos`, `pushedAfter`,
`pushedBefore`, `hideHighProfile`, `country`, `city`, `excludeCurrentCompanies`.

**Professional levers reach developers with a linked professional profile:**
`company`, `pastCompanies`, `schools`, `titles`, `industries`, `peerCompanies`, `companySize`,
`experienceTier`, `yoeMin`, `yoeMax`, `openToWork`, `state`.

Rules that are easy to miss:

- **A professional lever shrinks the page to linked profiles.** Strong builders with no linked
  profile drop out. Run these as their own pass and join on developer id.
- **`lang`, `country` and `city` filter on evidence.** A developer with no data on file for that
  field stays in. Add `requireLocation=true` when location is a hard requirement, then confirm
  `details.contact.location` at `depth=enriched`.
- **`subjects` and `techs` are hard filters on tags. `skills` and `q` are soft aims.** Put a
  must-have in the hard filter and a nice-to-have in `skills`.
- **`repos` is the lever most agents forget.** Seeding with the two or three projects that define a space finds a population no adjective in
  `q` describes.
- **`employer` and `company` are different signals.** `employer` is inferred from GitHub
  activity and reaches everyone. `company` reads the linked profile.
- **`requireEmail`, `requireLinkedin` and `requireLocation` only filter.** Each row already
  carries `hasEmail`, `hasLinkedin` and `hasLocation`. Addresses come from `/v1/developers/emails`.
- **`exclude` is how "fifty more" works.** Pass the ids you already hold on every call.
- **A `cursor` belongs to the query that produced it.** Pass it back unchanged.
- **`sortBy` binds when the query routes to the GitHub user index.** Check the order of the first
  page before relying on a sort.

---

## Reading a result

| Field | What it tells you |
| --- | --- |
| Row order | The ranking. Best match first. There is no per-row score to sort or threshold on. |
| `match.repos[]` | Why this person matched: `fullName`, `stars`, `language`, `role`. Your citation. |
| `match.repos[].role` | `owner` means the repo sits under their namespace. The lead author of an organization's repo reads as `contributor`. |
| `match.repos[].stars` | Count at retrieval time. `0` can also mean the source returned no count. |
| `match.status` | `unattributed` means this page carries no repo attribution. It makes no claim about match strength. |
| `id` | GitHub's numeric user id as a string. Stable across renames. Dedupe on it. |
| `countStatus` | `exact`, or `short` with `requested`, `returned` and `shortfallReason`. |
| `cursor` | Continuation token. `null` means no continuation for this query. |
| `cached` | The page came from a cached result set and may omit newer envelope fields. |
| `details.*` | Namespaces appear only when resolved. An absent namespace is unknown. |

### Short pages say why

| `shortfallReason` | Meaning | Next move |
| --- | --- | --- |
| `corpus` | Nobody else in the index matches | Stop paging this query. Widen it. |
| `filter_attrition` | Matches existed and your filters removed them from this page | Page on with the cursor |
| `coverage` | People matched and could not be returned | Page on |
| `capability` | A lane was unavailable to this credential | Retry with the cursor |
| `call_budget` | The request hit its own ceiling with more upstream | Retry with the cursor |
| `lane_window` | One lane ran out of window | Page on, or rephrase |

Report a target as met only when the rows you hold meet it.

### Unknown is its own answer

A missing `details` namespace, a null location, an empty education list: each means the data is
silent. Check the neighbours before settling on unknown: a location with an empty `country` often
has a `city` or a `raw` string that names the place. Carry it as unknown through your ranking. Drop on unknown only when the requirement is a
hard gate and the person asking has said so.

---

## Depth

| Depth | Adds |
| --- | --- |
| `core` | Profile, top repositories, the `match` block, cracked score |
| `enriched` | LinkedIn identity, experience, education, socials, resolved location |
| `deep` | The contribution garden, as `gardenSummary` by default or the full heatmap with `garden=full` |

Search wide at `core`, decide who matters, then `enrich` the survivors at the depth you need.
`facets` adds `ai.person_summary`, `ai.repo_summaries`, `ai.match_rationale` and `tags.repos` on
top of any depth. AI facets resolve in the background: the first read is `pending`, a second read
returns the value.

---

## Fan out: one query is a starting point

A role description is a topic. The `fanout-search` skill covers the general method. Applied here:

1. **Decompose the role into lanes**, each named by an artifact a strong person would have built.
   `role-decomposition` does this from intake notes.
2. **Write several `q` phrasings per lane**, one idea each, and run each as its own search.
3. **Vary the lever as well as the words.** A `repos`-seeded query, an `orgs` query and a `q`
   query for the same concept return substantially different people.
4. **Seed the known items.** Name the five to fifteen repositories that define the space and put
   them in `repos`. Keyword-style search under-retrieves canonical projects because everyone
   else's description of them outranks the thing itself.
5. **Walk the graph.** Call `/v1/developers/similar` on every strong hit.
6. **Page with `exclude`** carrying everything you hold.
7. **Dedupe on `id`.** People rename their logins.
8. **Cut on evidence you read**: the matched repos, the role, the band, the gates. Row order is
   relative to one query and does not compare across queries.

---

## Failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| A location or language filter seems ignored | Evidence-based filter left unknowns in | Add `requireLocation=true`, confirm on the row |
| Pages shrink to a handful | A professional lever restricted the pool to linked profiles | Run it as a separate pass, join on `id` |
| Same people on every page | `exclude` not sent | Pass every id you hold |
| Great engineers missing | One query, no seeds, no graph walk | Fan out, seed `repos`, walk `similar` |
| Thin page reported as complete | `countStatus` not read | Read `shortfallReason`, page on unless it is `corpus` |
| Tutorials and lists at the top | `q` names a topic | Describe an artifact and its mechanism |
| A sort did nothing | The query routed to a lane the sort does not bind on | Drop `q`, or sort the rows you hold yourself |
| `ai.*` value missing | Facet still `pending` | Read the same request again |
| Two people merged or split | Deduped on login | Dedupe on `id` |
| A long run returned nothing | Many sequential calls hit a time limit | Run queries in parallel groups of about eight |
| Unrelated projects on page one | A short or ambiguous term in `q` | Put the domain noun beside it |

---

## Reporting rules

When handing results to a person:

- **Cite the evidence.** Every claim about a developer traces to `match.repos` or a field you
  read. Say what they built and how it works.
- **Say what you filtered and what you confirmed.** A filter you sent and a field you verified
  are different claims. Name which one backs each requirement.
- **Carry unknowns visibly.** Mark an unverified location or seniority as unverified.
- **Declare what you left out**: pages you did not fetch, lanes that ran thin, people you cut and
  why.

---

## Drop-in prompt

```
You are sourcing engineers with the Vamo API (https://api.vamotalent.ai, bearer vamo_sk_ key,
30 search requests per minute per ACCOUNT). Spec: https://api.vamotalent.ai/openapi.json. The
spec wins over memory.

1. PICK THE DOOR. New people: GET /v1/developers/search. Depth on people you hold:
   /v1/developers/enrich. More like one person: /v1/developers/similar. Addresses:
   /v1/developers/emails. Rank logins against a role: POST /v1/fit-rank.

2. FAN OUT. The role description is a topic. Split it into lanes named by artifacts. Write
   several one-idea q phrasings per lane. Seed `repos` with the canonical projects of the space.
   Vary the lever as well as the wording. Call similar on every strong hit. Page with `exclude`.

3. KNOW THE TWO FAMILIES. GitHub-native levers (lang, skills, repos, subjects, techs, orgs,
   employer, minCracked/maxCracked, pushedAfter, hideHighProfile, country, city) reach everyone.
   Professional levers (company, pastCompanies, schools, titles, experienceTier, yoeMin/yoeMax,
   state) reach linked profiles only: run them as a separate pass and join on id.
   lang/country/city leave unknowns in: add requireLocation=true and confirm on the row.

4. READ RESULTS CORRECTLY. Row order is the ranking; there is no score field. match.repos is
   the evidence; role owner means the repo is under their namespace. match.status unattributed
   says nothing about strength. Read countStatus.shortfallReason before claiming a target:
   only `corpus` means exhausted. Dedupe on id. An absent details namespace is unknown.

5. GO DEEP LAST. Search at depth=core. Enrich only the survivors. Request ai.* facets twice:
   pending first, value second.

6. REPORT. Cite match.repos for every person. Separate what you filtered from what you
   confirmed. Mark unknowns. Declare pages not fetched, thin lanes and cuts.
```
