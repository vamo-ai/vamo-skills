# Discovery recipes

Reference for the `vamo-search` skill. Each recipe starts from what the person already has in
hand and gives the request, what to read on the results, and what to hand back. Bodies go to
`POST /v2/developers/search` unless another route is named. Field names are from
`GET /v2/developers/fields`, and the API wins when this file disagrees.

Two rules hold in every recipe. Describe the work in one short phrase, and put every other
requirement in its own filter. Confirm a hard requirement by reading the field on each person.
`PEOPLE` below stands for `["is_bot", "Eq", false], ["is_org_account", "Eq", false]`, which
every `And` list carries.

## What do you have?

| You have | Recipe |
| --- | --- |
| A technology, a niche, or something trending | [1](#1-a-technology-or-a-niche) |
| A kind of person whose title is not "engineer" | [2](#2-people-who-code-under-another-title) |
| A company or a GitHub organization | [3](#3-the-strongest-people-at-one-organization), [4](#4-people-from-named-companies) |
| A school | [5](#5-people-from-a-school) |
| A repository you admire | [6](#6-people-around-a-repository) |
| A place | [7](#7-people-in-a-place) |
| Your own team | [8](#8-people-like-your-own-team) |
| One great person | [9](#9-more-people-like-one-person) |
| A job description | [10](#10-a-job-description) |
| A question about where talent is | [11](#11-where-the-talent-is) |
| A bar for credibility | [12](#12-a-credibility-bar) |

## 1. A technology or a niche

*"Find developers building real-time voice agents." "Who is working on robot learning?"*

```json
{"rank_by": ["v", "ANN", ["Embed", "real-time voice agents, turn-taking and barge-in"]],
 "filters": ["And", [PEOPLE]], "limit": 50}
```

- Write three to five phrasings that each describe an artifact in the niche, one idea each, and
  run each as its own search. `domain-library.md` has phrasing sets for fifty domains.
- A term the phrase may not carry (a protocol, an acronym): add a keyword lane and fuse,
  `"queries": [{"filters": [...], "rank_by": ["v", "ANN", ["Embed", "..."]]}, {"filters": [...], "rank_by": ["all_repo_text", "BM25", "<term>"]}], "fuse": ["RRF", {"weights": [1, 1]}]`.
- For something trending, add `["last_active_at", "Gte", "<date a few months back>T00:00:00Z"]`.
- Hand back: person, the matched repository, what it does in one sentence.

## 2. People who code under another title

*"Designers who ship code." "Product managers with real GitHub work." "Forward-deployed
engineers."*

- Fix one search body: the same work phrase, the same filters, the same reputation band. Run it
  once per place, adding only the place filter, with the same `limit` and the same number of pages.
- For each place record how many strong people came back on those pages, how many own a matched
  repository, and three example people.
- Report it as a comparison between the places you tested, under one set of filters. Say which
  filters and which places, and do not present any count as a total.

## 12. A credibility bar

*"Only people with serious open-source work." "Only the top tier."*

- Reputation band: `["devrank", "Gte", 70], ["devrank", "Lte", 88], ["devrank", "NotEq", null]`.
  The ceiling sets aside people famous enough that they rarely answer; drop it for top tier.
- Popularity of their own work: `["owned_stars_max", "Gte", 100]`. Work they contributed to:
  `["contributed_stars_max", "Gte", 1000]`.
- Ownership: read the matched repo's `role`. A star count on a project they contributed one fix
  to says little about them.
- Activity: `["last_active_at", "Gte", "<date>T00:00:00Z"]`, and the garden summary at
  `depth=deep` for rhythm.
