---
name: vamo-search
description: Use when searching for software engineers, sourcing candidates for a role, or enriching developer profiles through the Vamo API. Covers endpoint selection, the search lever model, how to read a result without misranking it, and cost control. Triggers "find engineers who", "source for this role", "who built X", "enrich these developers", "get emails for".
---

# Vamo Search

How an agent should use and search Vamo without misreading a result or burning credits.

Vamo is a developer talent search engine over GitHub proof-of-work. You describe who you
want in natural language; it returns real people with the repos that prove the claim.

Base URL `https://api.vamotalent.ai` (staging `https://api-staging.vamotalent.ai`).
Machine-readable spec: `https://api.vamotalent.ai/openapi.json` — every operation carries an
`x-vamo` block with its access level, credit price, rate limit, and quota. **When this skill and
the spec disagree, the spec wins.**

The published spec documents the four `GET /v1/developers/*` routes. The `POST /v1/searches/*`
and `POST /v1/search/jobs` lanes below are real and shipped, but are not in `openapi.json` —
confirm them against the API before building an external integration on them.

---

## Auth

```
Authorization: Bearer vamo_sk_...
```

A session token (member) or an API key prefixed `vamo_sk_` (agent). All search routes need
the `search:read` entitlement. Rate limit is **30 requests/minute per account** — not per key.
Parallel agents on one account share that budget, so a fanout of 30 queries needs throttling.

---

## Pick the right door

The single most common mistake is calling the wrong endpoint and concluding Vamo can't do
something it does.

| You want | Call | Notes |
|---|---|---|
| One page, simple filters | `GET /v1/developers/search` | The easy door. Billed per developer returned. |
| To see the query before spending | `POST /v1/searches/plan` → `POST /v1/searches/run` | **Planning is free.** Read/edit the plan, then run it. |
| Alternative angles on a query | `POST /v1/searches/angles` | Returns suggested alternate search configs. A cached read spends nothing. Server-side fanout. |
| Full control, one call | `POST /v1/searches/execute` | Takes the whole search config. Use when the GET params can't express it. |
| More than a few pages | `POST /v1/search/jobs` | Fills toward a target across rounds. Poll `GET /v1/search/jobs/{id}`, extend with `POST .../more`. Note the path is `search`, singular. |
| Deepen rows you already hold | `GET /v1/developers/enrich` | Same shape as search. Don't re-run the search to get more depth. |
| More people like this one | `GET /v1/developers/similar` | Walks co-contribution, co-star, follow, and repo-similarity edges from one seed. |
| Email addresses | `GET /v1/developers/emails` | Separate purchase, 100 credits per developer. |
| Depth on a shortlist you already have | `POST /v1/deep-research/jobs` | Research, **not** search. It finds nobody new. |

**Plan before you run when you're spending someone else's money.** `plan` is free and returns
a readable object. Iterating on a plan costs nothing; iterating on a bad `run` costs credits.

---

## The search lever model

`q` carries the intent. Every other parameter narrows it.

```
GET /v1/developers/search
  q            free text — who you're looking for, matched semantically
  lang         languages the person has DEMONSTRATED (go,rust)
  skills       abilities matched semantically against what they built
  country      united states,canada
  company      where they work NOW
  repos        seed repos as owner/name — finds people who build comparable things
  minFollowers integer
  hasEmail     true|false — FILTERS ONLY, never returns an address
  exclude      developer ids to leave out, comma separated
  depth        core | enriched | deep
  limit        1-100, default 25
  cursor       opaque, from the previous response
```

Rules that are not obvious:

- **`lang` filters on evidence, not absence.** A developer with no language data held is
  excluded, not included-by-default. Use `lang` only when something is genuinely mandatory;
  otherwise put it in `skills` and let it rank instead of gate.
- **`hasEmail=true` filters, it does not reveal.** Addresses are a separate 100-credit
  purchase per developer. Rows dropped by `hasEmail` are never billed.
- **`exclude` is how "show me 50 more" works.** Pass the ids you already hold when paging.
  Exclusion happens *before* billing, so you're not charged for a repeat you'd discard.
- **`cursor` is lane-scoped.** Never construct one, parse one, or reuse one across queries.
- **`repos` is the strongest lever most agents forget.** "People who build things like
  `huggingface/lerobot`" beats any adjective you can put in `q`.

### Levers are declared, never silently dropped

Every lever you set comes back in exactly one of two arrays:

- `appliedLevers` — bound on this page
- `unsupported` — this lane could not apply it as a hard filter

**Check `unsupported` on every call.** If your mandatory filter is listed there, you are
looking at unfiltered results and must not present them as filtered.

---

## Reading a result without misranking it

This section is the reason this skill exists. The response fields are easy to misuse and the
failure is silent.

| Field | What it is | The trap |
|---|---|---|
| `score` | Page-local ordering key | **NOT match quality.** Never show it, never threshold on it. |
| `relevance` | The provider's query-match score | This is the one to gate on. |
| `relevanceOrder` | Direction for reading `relevance` | **Inverts by lane.** See below. |
| `evidence.matchedRepos` | Why this person matched | Your citation. Use it in outreach. |
| `evidence.matchStatus` | `unattributed` = lane can't attribute | Does **not** mean a weak match. |
| `countStatus.shortfallReason` | Why a page is short | Distinguishes exhausted corpus from platform gates. |
| `rankScope` | Population the ordering was computed over | `page` means rows were ranked only against each other. |
| `entity` | Index actually queried after auto-routing | `User` vs `Repo`. Don't branch on `provider`. |

### `relevanceOrder` will silently invert your ranking

- `higher_is_better` — the User lane (weighted BM25, no vector)
- `lower_is_better` — the two vector lanes (LinkedIn profile lane, repo→contributor fanout),
  which report **cosine distance**
- `null` — the page carries no relevance to order at all. A repo-seed gate has no query to be
  relevant to, and a filter-only search is ordered by recency, so every row carries the same
  relevance. **Null must not be read as "everything matched equally."**

Sorting by `relevance` without reading `relevanceOrder` will hand you the *worst* matches as
your top results on half the lanes, and nothing in the response will look wrong. Always read
the direction. Never hardcode it.

### Short pages are declared, never hidden

A live `cursor` means ask again. A short page with `countStatus.shortfallReason` set is telling
you why. Never pad a short page and never report a target as met when `countStatus` says it wasn't.

---

## Cost discipline

Every call is real money. Surface costs proactively.

**Depth ladder**, charged per developer *returned* (not per call, not per request):

| Depth | Credits | USD | What you get |
|---|---|---|---|
| `core` | 13 | $0.013 | profile, repos, measured signals, cracked score |
| `enriched` | 19 | $0.019 | + deeper enrichment |
| `deep` | 26 | $0.026 | + external reach |
| email reveal | 100 | $0.100 | **per developer**, every address observed for them |

Non-obvious economics:

- **`limit` is a price ceiling, not a price.** A page of zero results costs zero. There is no
  per-call floor.
- **Re-enrichment is nearly free.** A developer your account already enriched this month
  re-bills at **1 credit**, not the full tier. Re-paging a corpus you've already enriched is cheap.
- **A developer with no email costs 1 credit** and returns `emails: []`. An id the platform
  holds nothing for is omitted and costs nothing. Duplicates bill once.
- **Read the actual debit off the `x-cost` response header.** Do not estimate from the table.
- **On `POST /v1/searches/execute`, be explicit about `facets`.** Omitting it applies *your
  account's default* facets and charges for them, so the same request body costs different
  amounts on different accounts. Send `[]` to suppress enrichment, or send the exact list.
  If you're billing your own customers, never rely on the account default.

**Cheapest correct pattern:** search wide at `core`, decide who matters, then `enrich` or buy
emails only for the survivors. Never search at `deep` to "see what's there."

---

## Fan out — one query is not a search

A role description is a *topic*, not a query. Running the JD verbatim as one `q` and taking
page one is the single biggest quality loss. The `fanout-search` skill in this repo covers the
general method; applied to Vamo:

1. **Decompose the role into axes** — language, domain, artifact (library vs product vs
   infra), seniority signal, geography. Write 10–25 queries across the meaningful cells.
2. **Ask the API for angles.** `POST /v1/searches/angles` returns alternate search configs for
   your query. It is server-side query expansion, and a cached read spends nothing — cheaper
   than inventing all your facets yourself.
3. **Vary the lever, not just the words.** A `repos`-seeded query and a `skills` query for the
   same concept hit different lanes and return substantially different people. That is
   coverage, not redundancy.
4. **Known-item arm:** name the 5–15 repos that define this space and seed `repos` with them
   directly. Keyword search under-retrieves canonical projects because everyone else's
   description of them outranks the thing itself.
5. **Walk the graph.** For every strong hit, call `GET /v1/developers/similar`. Co-contribution
   and co-star edges surface people no text query would reach.
6. **Page with `exclude`,** passing everything you already hold, so a wide sweep never
   re-bills or repeats.
7. **Dedupe on `developer.developerId`** — GitHub's numeric user id, stringified. It is
   deterministic and rename-proof. Never dedupe on login; people rename.
8. **Gate on `relevance`** (in the direction `relevanceOrder` gives you), then rank on your own
   composite. Never gate on `score`.

Budget the sweep before you run it: 20 queries x 25 results x 13 credits ≈ 6,500 credits
($6.50) at `core`. Say that number out loud before spending it.

---

## Recipes

**Cheap wide sweep, one facet of a role**

```bash
curl -s -H "Authorization: Bearer $VAMO_API_KEY" \
  "https://api.vamotalent.ai/v1/developers/search?q=engineers+who+build+inference+servers+for+LLMs&lang=python,rust&depth=core&limit=50" \
  | jq '{n: (.results|length), order: .relevanceOrder, unsupported, shortfall: .countStatus}'
```

Always inspect `unsupported` and `relevanceOrder` on the first call of any new query shape.

**Seed from repos instead of adjectives**

```
/v1/developers/search?q=distributed+training+infrastructure&repos=pytorch/pytorch,ray-project/ray&depth=core&limit=25
```

**Deepen only the survivors**

```
/v1/developers/enrich?ids=583231,1024025&depth=deep      # max 25 ids
```

**Buy contact for a shortlist**

```
/v1/developers/emails?logins=torvalds,gvanrossum         # 100 credits each
```

`ids` and `logins` are freely mixable on `enrich` and `emails`, 25 max.

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Top results are obviously the worst | Sorted by `relevance` ignoring `relevanceOrder` | Read the direction; it inverts by lane |
| "Vamo can't filter on X" | Wrong door — GET params are the simple surface | Use `POST /v1/searches/execute` |
| Filter appears ignored | Lever landed in `unsupported` | Check the array; don't present results as filtered |
| Bill higher than expected | `facets` omitted on `execute`, so account defaults applied | Send an explicit list or `[]` |
| Same people every page | Not passing `exclude` | Pass every id you hold |
| Great engineers missing | Single query, no fanout, no `repos` seeds | Fan out; seed canonical repos; walk `similar` |
| Results thin, reported as complete | Ignored `countStatus.shortfallReason` | Report the shortfall and its reason |
| Ranking looks arbitrary | Read `score` as quality | `score` is a page-local ordering key only |

---

## Reporting rules

When handing results to a human:

- **Cite the evidence.** Every claim about a person traces to `evidence.matchedRepos`. Say
  "built B, relevant because C" — describe the work, don't sell the person.
- **Never state corpus or population size.** No "out of N developers", no percentile framing
  derived from a count. Placement claims are bounded by the source, not the population.
- **State the cost.** What you spent, at what depth, and what remains unpurchased.
- **Declare what you dropped** — filters that landed in `unsupported`, pages not fetched,
  shortfalls. Silent truncation reads as full coverage.

---

## Drop-in prompt

```
You are sourcing engineers with the Vamo API (https://api.vamotalent.ai, bearer vamo_sk_ key,
30 req/min per ACCOUNT). Spec: https://api.vamotalent.ai/openapi.json — it wins over memory.

1. PICK THE DOOR. Simple page -> GET /v1/developers/search. Need to inspect the query first ->
   POST /v1/searches/plan (FREE) then /run. Can't express it in GET params ->
   POST /v1/searches/execute. Need many pages -> POST /v1/search/jobs (singular 'search' — the guides say
   /v1/searches/jobs and that path is wrong).

2. FAN OUT. The role description is a topic, not a query. Decompose into 10-25 queries across
   language / domain / artifact / seniority / geography. Seed `repos` with the 5-15 canonical
   projects of the space. Vary the LEVER, not just the wording. Call
   GET /v1/developers/similar on every strong hit. Page with `exclude`.

3. SPEND CAREFULLY. Search wide at depth=core. Only enrich or buy emails for survivors.
   `limit` is a ceiling, not a price. Re-enriching this month's developers costs 1 credit.
   Emails are 100 credits/developer and hasEmail only FILTERS. Read `x-cost` for the real
   debit. State your budget before the sweep.

4. READ RESULTS CORRECTLY. Gate on `relevance`, in the direction `relevanceOrder` says —
   it INVERTS by lane and null does not mean "all equal". NEVER gate or display `score`.
   Check `unsupported` for filters that did not bind. Check `countStatus.shortfallReason`
   before claiming you hit a target. Dedupe on `developer.developerId`, never on login.

5. REPORT. Cite evidence.matchedRepos for every person. State total cost. Declare dropped
   filters, unfetched pages, and shortfalls. Never state corpus size or population counts.
```
