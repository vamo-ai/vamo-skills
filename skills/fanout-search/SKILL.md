---
name: fanout-search
description: Use when a search request is a topic rather than a single lookup — sourcing candidates, literature reviews, competitive scans, "find me the best N repos/papers/tools for X", or any task where missing good results is worse than doing extra queries. Turns one human query into 25-40 machine queries plus a known-item arm, then ranks the union. Corpus-agnostic (GitHub, arXiv, web, vector index, internal DB). Triggers "find all", "best N", "comprehensive list", "research X thoroughly", "make sure we don't miss".
---

# Fanout Search

How to turn one human query into 25–40 machine queries, then back into one ranked list.

Works for any searchable corpus: GitHub, arXiv, web, a vector index, an internal DB. The corpus changes; the six steps don't.

---

## The one rule

**Never run the user's query verbatim as your only search.**

A human query is a _topic_. A search engine wants a _facet_. "Find strong repos on foundation models in robotics" is not a query, it's a description of a region. Your job is to cover that region with 25–40 overlapping probes, then rank what you caught.

One query returns one engine's opinion of one phrasing. Thirty queries return the region, and the overlap between them is a free centrality signal you get for nothing.

---

## Step 1 — Decompose into axes

Find the dimensions the field actually splits along, then take the cross product. Ask: _if I were writing a taxonomy of this region, what are the column headers?_

Generic axis kit — most domains use 4–6 of these:

| Axis            | Question               | Robotics example                                |
| --------------- | ---------------------- | ----------------------------------------------- |
| **Method**      | How is it done?        | VLA, diffusion policy, behavior cloning, RL     |
| **Subject**     | What is it done to/by? | arm, hand, humanoid, quadruped, drone, car      |
| **Task**        | What outcome?          | manipulation, grasping, navigation, locomotion  |
| **Artifact**    | What kind of thing?    | model, dataset, simulator, benchmark, framework |
| **Scale / era** | Which generation?      | pre-LLM, foundation-model, 2026 SOTA            |
| **Register**    | Whose words?           | academic, industry, tutorial, non-English       |

Write one query per meaningful cell. Skip cells that are nonsense (drone + tactile grasping). Target 25–40 queries. Under 15 means you under-decomposed; over 60 means you're permuting noise.

**Overlap is the point.** Do not deduplicate your _queries_ to be efficient. Two queries that both return item X are telling you X is central. Count those hits and use them when ranking.

---

## Step 2 — Lift the vocabulary

Weak agents search the user's words. Strong agents search the _field's_ words. For each axis value, add:

- **Acronym and expansion, both.** `VLA` and `vision-language-action`. They retrieve different documents. Everyone forgets this.
- **Insider term for the outsider term.** User says "robot AI brain"; field says "embodied foundation model", "generalist policy".
- **Named artifacts as bare nouns.** The model, simulator and benchmark names everyone in the field cites. Names retrieve ecosystems.
- **Org names.** The handful of labs and organizations that publish most of the field's code. Labs cluster.
- **Meta-terms.** `awesome <topic>`, `<topic> survey`, `<topic> paper list`. These are high-recall hubs — one hit yields fifty candidates.
- **Other languages** where the field is active. Chinese robotics/embodied-AI repos are a large, mostly-disjoint slice you miss entirely by searching only English.

If you don't know the field's vocabulary, that is itself step 0: run 2–3 broad probes, read the top 20 titles, harvest the recurring nouns, _then_ build the real query set.

---

## Step 3 — Add the known-item arm ← the step everyone skips

**Keyword search systematically under-retrieves the most famous items in a field.**

This is not a tuning problem, it's structural. When something is canonical, hundreds of other documents describe themselves in relation to it, and those descriptions outrank the thing itself. The famous item shows up everywhere as a _mention_ and nowhere as a _result_.

Measured on the robotics run: seven of the field's load-bearing repositories (two open policy models, a robot-learning library, a humanoid foundation model, a locomotion training suite, an imitation-learning framework and a control suite) appeared in 863 keyword hits **only inside other repos' descriptions**. Zero of them were returned as results.

So: **before searching, write down every canonical item you already know.** Fetch those directly by ID/name/URL. 40–70 of them. Merge with the keyword results.

If you know nothing about the field, get the list from meta-terms first (step 2: `awesome <topic>`), read one or two hub documents, extract the names everyone cites, then fetch those by name.

Cost is trivial — direct lookups are cheap and don't touch the search rate limit.

---

## Step 4 — Fan out

Run every query. Mechanical, parallelizable, no model needed.

- Respect rate limits (GitHub search: 30/min authed → sleep ~2.2s between calls).
- 2 pages per query is usually enough; page 3+ is tail noise.
- Apply a quality floor at the API level when supported (`stars:>50`) — it costs nothing and halves your junk.
- Store raw results append-only as JSONL. Never filter during collection; you'll want to re-filter with different thresholds later and re-fetching is the expensive part.
- Record which query produced each hit, or at minimum a per-item hit count.

---

## Step 5 — Gate

Broad queries drag in garbage. A robotics sweep pulled in a web scraper, a UI library, and a list of CS video lectures.

A cheap two-term AND gate kills most of it:

```
keep IF  (matches DOMAIN vocabulary)  AND  (matches QUALIFIER vocabulary)
         AND NOT (matches BAN list)
         AND NOT archived/dead
```

For robotics: DOMAIN = `robot|embodied|manipulat|humanoid|drone|navigation|driving`, QUALIFIER = `model|learning|policy|transformer|diffusion|dataset|benchmark|foundation`, BAN = `web crawler|no-code|chatbot maker|video lectures|resume|cheatsheet`.

Build the BAN list _from what you actually saw_, not from imagination. Look at the raw results, spot the junk clusters, ban those. Two minutes of looking beats an hour of guessing.

Gate the keyword arm only. **Known-items bypass the gate** — you already vouched for them, and canonical repos often have terse descriptions that fail keyword gates. The field's best-known physics simulator describes itself as a general purpose physics simulator. The word "robot" never appears.

---

## Step 6 — Rank and cut

Composite beats any single signal:

```
score = log10(popularity + 1) * 2      # log, so 30k stars doesn't erase everything else
      + hit_count * 0.35               # cross-query centrality
      + recency_bonus                  # 1.2 if <6mo, 0.4 if <18mo, else 0
```

Give known-items a modest hit-count (≈4), not a maximum. They're a nudge onto the list, not a guarantee of the top. Overweighting them buries legitimately huge finds — a seed bonus of 9 pushed a 2.5k-star repo above a 7.9k-star one until it was dialed back.

Tune weights by looking at the top 20 and asking "is this the order an expert would give?" If the answer is no, the weights are wrong — not the list.

Then sort, cut to N, export with enough columns to re-filter without re-running: `rank, id, popularity, type, category, language, last_updated, url, description`.

Add a `type` column separating primary artifacts from meta artifacts (code vs. paper-list, product vs. review). Users almost always want one or the other, and it's one regex to compute.

---

## Coverage check — do this before you report

Name 5–10 things you are confident _should_ be in the result. Check whether they are. Every miss is a query you didn't write. Add it, re-run, repeat.

Stop when a full round produces nothing new. Two consecutive dry rounds means done.

Also report what you dropped: the floor, the cut, the ban list, the pages you didn't fetch. Silent truncation reads as "covered everything" when it wasn't.

---

## Drop-in prompt

Give this to an agent along with the user's query.

```
You are running a FANOUT SEARCH. The user gave you a topic, not a query.
Do NOT search their words directly and stop. Follow all six steps.

TOPIC: {{user_query}}
CORPUS: {{github | arxiv | web | vector index | ...}}
TARGET: {{N}} results

1. AXES. Decompose the topic into 4-6 axes (method / subject / task / artifact /
   scale / register). List the values under each. Take the cross product and write
   25-40 concrete queries, one per meaningful cell. Skip nonsense cells.

2. VOCABULARY. For each query, use the FIELD's words, not the user's. Include both
   acronym and expansion. Add named artifacts, lab/org names, and meta-terms
   ("awesome X", "X survey"). Add non-English terms if the field is active there.
   If you don't know the vocabulary: run 3 broad probes, read the top 20 titles,
   harvest recurring nouns, then write the real query set.

3. KNOWN ITEMS. List 40-70 canonical items in this field that you already know by
   name. Fetch them DIRECTLY by id/name/url — do not rely on search to surface them.
   Keyword search structurally under-retrieves famous items, because everyone else's
   description of them outranks the thing itself. If you know none, extract names
   from the meta-term hits in step 2 first.

4. FETCH. Run every query. 2 pages each. Apply a quality floor if the API supports
   one. Store raw results append-only; do not filter during collection. Record a
   per-item hit count across queries.

5. GATE. Keep an item only if it matches BOTH a domain term AND a qualifier term,
   and matches no ban term, and isn't archived. Build the ban list from junk you
   actually observed in the raw results. Known-items from step 3 BYPASS the gate.

6. RANK. score = log10(popularity+1)*2 + hits*0.35 + recency_bonus. Sort, cut to N,
   export as CSV with: rank, id, popularity, type, category, language, last_updated,
   url, description. Add a type column separating primary artifacts from meta
   artifacts (code vs paper-list).

COVERAGE CHECK before reporting: name 5-10 items you're confident belong in the
result. Any that are missing = a query you failed to write. Add it and re-run.
Repeat until a round yields nothing new.

REPORT: the file path, the composition breakdown, and explicitly what you dropped
(floor, cut, ban list, unfetched pages). Never imply coverage you didn't achieve.
```

### Expansion-step output schema

If you split this across agents, have the expansion agent emit exactly this. Everything downstream is deterministic code and needs no model.

```json
{
  "axes": { "method": ["..."], "subject": ["..."], "task": ["..."], "artifact": ["..."] },
  "queries": ["vision-language-action model robot", "diffusion policy manipulation", "..."],
  "known_items": ["<owner/name>", "<owner/name>", "..."],
  "gate": {
    "domain": ["robot", "embodied", "manipulat"],
    "qualifier": ["model", "policy", "dataset"],
    "ban": ["web crawler", "no-code", "video lectures"]
  },
  "expected": ["items you'd bet money are in the final list — used for the coverage check"]
}
```

---

## Worked example

**Query:** "200 strong repos on foundation models in robotics AI"

29 facet queries + 8 topic queries → 863 raw hits → 712 unique → gate → 274. 64 known-items fetched by name, 59 resolved, 7 of which the keyword sweep had missed entirely. Merged pool 308 → ranked → top 200.

Result: 172 code / 28 paper-lists, median 1,140 stars, 64 VLA-and-foundation-model, 52 simulator/benchmark/dataset. Dropped: `stars<50`, archived repos, 24 hand-banned off-topic items, pages 3+.

Elapsed: ~4 minutes, dominated by search rate-limit sleeps.

---

## Failure modes

| Symptom                        | Cause                                                  | Fix                                         |
| ------------------------------ | ------------------------------------------------------ | ------------------------------------------- |
| Famous items missing           | No known-item arm                                      | Step 3                                      |
| Results all say the same thing | Axes too narrow; you permuted synonyms                 | Add an orthogonal axis                      |
| Junk at the top                | No gate, or popularity-only ranking                    | Step 5, and add hit-count to score          |
| Everything from one lab/org    | Single vocabulary register                             | Add insider + outsider + non-English terms  |
| Great list, wrong field        | Never checked the user's intent                        | Coverage check against _their_ expectations |
| Can't hit N                    | Floor too high, or region genuinely smaller than asked | Lower the floor, say so; don't pad          |

---

## Notes

- Only step 1–3 need a model. Steps 4–6 are deterministic code. Don't spend a model call on what a regex does.
- Cache raw results. Re-filtering is free; re-fetching costs rate limit and time.
- When ranking by popularity, know your metric's health. GitHub stars, for instance, stopped flowing through the public firehose around May 2026 — the repo API is still accurate, but any star data sourced from event streams trails badly.
- `vamo-search` in this repo applies this method to one specific API, including the levers and
  cost model that change how aggressively you should fan out.
