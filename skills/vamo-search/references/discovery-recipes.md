# Discovery recipes

Reference for the `vamo-search` skill. Each recipe starts from what the person already has in
hand and gives the calls, what to read on the results, and what to hand back. Parameter names are
from the API's description at `https://api.vamotalent.ai/openapi.json`. Read the operation there
before relying on one, and the spec wins when this file disagrees.

Two rules hold in every recipe. Describe work in `q`, and put every other requirement in its own
filter. Confirm a hard requirement by reading the field on each person after `enrich`.

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

- Write three to five `q` phrasings that each describe an artifact in the niche, one idea each,
  and run each as its own search. `references/domain-library.md` has phrasing sets for fifty
  domains.
- Add `techs` or `subjects` only with tag values you have seen on a real row.
- For something trending, add `pushedAfter` set a few months back, so the people are building
  it now.
- Hand back: person, the matched repository, what it does in one sentence.

## 2. People who code under another title

*"Designers who ship code." "Product managers with real GitHub work." "Solutions engineers and
forward-deployed engineers."*

- Run `titles` with the titles you want, paired with a `q` that describes what such a person
  builds: a component library, internal tools, customer integrations, demo apps.
- `titles` reads linked professional profiles, so it reaches the people who have one. Run a
  second pass without `titles`, on `q` alone, and read the title after `enrich` at
  `depth=enriched`.
- Hand back: person, title and employer, the repository that shows they build.

## 3. The strongest people at one organization

*"Who are the strongest engineers in this GitHub organization?"*

- `orgs=<organization>` with `sortBy=crackedScore`. No `q` is needed.
- For a company with no single GitHub organization, use `employer=<company>` the same way.
- Read `details.score.cracked` and the top repositories. Check current employment on the
  profile, since an organization association can outlast a job.
- Hand back: a ranked list with band, what each person works on, and whether they still appear
  to be there.

## 4. People from named companies

*"Engineers at these competitors." "People who used to work at these companies."*

- Now: `company` (linked profiles) and `employer` (everyone, inferred from GitHub activity). Run
  both and join on `id`.
- Before: `pastCompanies`. It matches the full employment history, the current employer
  included, so confirm on `details.identity.experience` that the role has ended.
- Always send `excludeCurrentCompanies` with the hiring company and anyone off limits.
- Add a `q` for the area of work you want from those companies.

## 5. People from a school

*"Strong builders who went to these universities."*

- `schools=<school>` with a `q` or `lang` for the kind of work. Add `experienceTier=early` for
  recent graduates.
- It reads linked professional profiles, so it finds a subset. Many strong builders list no
  school. Treat school as a way to find some people and to rank others, and confirm the entry
  under `details.identity.education`, reading past any secondary school listed first.

## 6. People around a repository

*"People who build things like this project." "Who are the real contributors here?"*

- `repos=<owner/name>` finds people who build comparable things. Seed one repository at a time.
  Several seeds at once let one dominate.
- For the contributors themselves, start a deep-research job on the repository and read its
  report: contributors weighted toward recent work, and where its audience places.
- Run `/v1/developers/similar` on the two or three strongest people the report names.

## 7. People in a place

*"Rust engineers in Austin."*

- `city` or `country` with `requireLocation=true`. Without `requireLocation`, people with no
  location on file pass the filter.
- After `enrich` at `depth=enriched`, read `details.contact.location`: `city`, `country`, `raw`
  and `source`. The resolved country can be empty while the city or the raw text names the place.
- Hand back the location and where it came from beside each person.

## 8. People like your own team

*"This is our GitHub organization. Find everyone in it, then find people like them."*

1. `orgs=<your organization>` to list the team. Keep their ids.
2. `/v1/developers/similar` on each of the strongest four to six.
3. Add a `q` built from what the team's best repositories do, to catch people the graph misses.
4. Put the team's ids and your organization in `exclude` and `excludeCurrentCompanies`.

A person returned from several seeds is close to the center of what the team does. Rank on it.

## 9. More people like one person

*"Find more like this engineer."*

- `/v1/developers/similar?login=<login>`. Each result carries a `whySimilar` line.
- Read what the seed built, then write two `q` phrasings from it and run those as well. The
  similar set finds neighbors. The queries find people with the same craft and no connection.
- If the seed is very well known, results skew to other well-known people. Add a reputation
  ceiling with `maxCracked`, or `hideHighProfile=true`, when the goal is people who will answer.

## 10. A job description

*"Here is the role. Find fifty people who fit."*

- Use the `role-decomposition` skill first. It turns the description into lanes, gates and
  rank signals. Then run each lane here.
- Recall ten to fifteen times the number of people wanted, and cut on evidence you read.
- `POST /v1/fit-rank` scores the logins you hold against the role text, as a second opinion on
  your own ordering.

## 11. Where the talent is

*"Which cities have the most people building this?" "Where should we open the role?"*

- Fix one set of queries and one reputation band. Run the identical set once per place with
  `city` or `country` and `requireLocation=true`, with the same `limit` and page count each time.
- For each place record: how many people came back in the band, how many own a matched
  repository, and three example people.
- Report it as a comparison between the places you tested. It is a sample under one set of
  queries. Say which queries and which places, and do not present any count as a total.

## 12. A credibility bar

*"Only people with serious open-source work." "Only the top tier."*

- Reputation: `minCracked`, or `tier`. Add `maxCracked` when the role needs people who are
  reachable as well as strong.
- Popularity of their own work: `minStars` on the total across their repositories.
- Ownership: read `match.repos[].role` and the repository itself. A star count on a project
  they contributed one fix to says little about them.
- Activity: `pushedAfter` for recency, and the garden summary at `depth=deep` for rhythm.
