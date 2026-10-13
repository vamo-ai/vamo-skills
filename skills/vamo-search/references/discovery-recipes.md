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

```json
{"filters": ["And", [["title_function", "In", ["design"]], PEOPLE]],
 "rank_by": ["v", "ANN", ["Embed", "component library and design system in React"]],
 "limit": 50, "depth": "enriched"}
```

- `title_function` values include design, product, devrel, solutions, forward_deployed,
  customer_eng, founder. Pair the family with a phrase for what such a person builds.
- Title filters read linked professional profiles. Run a second pass on the phrase alone and read
  the title on the card.
- Hand back: person, title and employer, the repository that shows they build.

## 3. The strongest people at one organization

*"Who are the strongest engineers at this company?"*

```json
{"filters": ["And", [["current_company_ids", "ContainsAny", {"company": ["<Company>"]}], PEOPLE]],
 "sort": "devrank", "limit": 50, "depth": "enriched"}
```

- For the company's open-source people, add a second lane ranked the same way with
  `["contributed_repo_ids", "ContainsAny", {"repos_of": "<owner/name>"}]` on one of its main
  repositories, and fuse. Keep the employer filter on both lanes.
- Read `index.recent_roles` to check they are still there.
- Hand back: a ranked list with band, what each person works on, and whether they still appear
  to be there.

## 4. People from named companies

*"Engineers at these competitors." "People who used to work at these companies."*

- Worked there, now or before: `["former_company_ids", "ContainsAny", {"company": ["<A>", "<B>"]}]`.
- Now: `current_company_ids`. Left: `past_company_ids`.
- Exclude the hiring company and anyone off limits:
  `["Not", ["current_company_ids", "ContainsAny", {"company": ["<Hiring company>"]}]]`.
- Add a phrase for the area of work you want from those companies, and `"depth": "enriched"` so
  the card carries title and recent roles.

## 5. People from a school

*"Strong builders who went to these universities."*

```json
{"filters": ["And", [["school_ids", "ContainsAny", {"school": ["<University>"]}], ["graduation_year", "Gte", 2023], PEOPLE]],
 "rank_by": ["v", "ANN", ["Embed", "<the kind of work>"]], "limit": 50, "depth": "enriched"}
```

- School and graduation year read linked professional profiles, so they find a subset. Many
  strong builders list no school. Use school to find some people and to rank others, and confirm
  the entry under `details.identity.education`.

## 6. People around a repository

*"People who build things like this project." "Who are the real contributors here?"*

- Contributors: `"repos": {"names": ["<owner/name>"], "role": "contributor"}`.
- People who worked alongside them: `"repos": {"names": ["<owner/name>"], "hops": 2}`.
- People who build comparable things: `"rank_by": ["v", "ANN", {"like": ["<owner/name>"]}]`. The
  repo's own contributors rank first; read past them.
- For a full read of who builds it and who validates it, start a deep-research job on the
  repository (`{"subject": "repos", "repos": ["<owner/name>"]}`) and read its report.
- Run `/v2/developers/similar` on the two or three strongest people found.

## 7. People in a place

*"Rust engineers in Austin."*

```json
{"filters": ["And", [["location_ids", "ContainsAny", {"place": ["Austin"]}], ["person_languages", "ContainsAny", ["rust:strong", "rust:primary"]], PEOPLE]],
 "sort": "devrank", "limit": 50}
```

- A city means its metro area; `places_resolved` says how it was read. Add `"scope": "city"` for
  the city itself. A region or a country works the same way (`{"place": ["Bay Area"]}`).
- Hand back the location beside each person.

## 8. People like your own team

*"This is our company. Find everyone on the team, then find people like them."*

1. Recipe 3 with your own company, to list the team. Keep their ids.
2. `/v2/developers/similar` on each of the strongest four to six.
3. Add a phrase built from what the team's best repositories do, to catch people the graph misses.
4. Put the team's ids in `exclude` and your company in a `Not` filter.

A person returned from several seeds is close to the center of what the team does. Rank on it.

## 9. More people like one person

*"Find more like this engineer."*

```json
{"like_person": "<login>", "intent": "same", "limit": 25}
```

- `POST /v2/developers/similar`. `intent` is `same` (the same kind of work), `overall` or
  `network`. Add `filters` to keep it to a place or a company.
- Read what the seed built, then write two phrasings from it and run those as well. Similar finds
  neighbors. The phrasings find people with the same craft and no connection.
- If the seed is very well known, results skew to other well-known people. Add a reputation
  ceiling (recipe 12) when the goal is people who will answer.

## 10. A job description

*"Here is the role. Find fifty people who fit."*

- Use the `role-decomposition` skill first. It turns the description into lanes, gates and rank
  signals. Then run each lane here.
- Recall ten to fifteen times the number of people wanted, and cut on evidence you read.
- `POST /v1/fit-rank` scores the logins you hold against the role text, as a second opinion on
  your own ordering.

## 11. Where the talent is

*"Which cities have the most people building this?" "Where should we open the role?"*

```json
{"filters": ["And", [["title_function", "In", ["ml_eng", "ai_research"]], PEOPLE]],
 "aggregate_by": {"people": ["Count"]}, "group_by": ["title_level"], "limit": 20}
```

- `POST /v2/developers/aggregate` counts people by a field under any filters. Run the same
  filters once per place to compare places.
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
