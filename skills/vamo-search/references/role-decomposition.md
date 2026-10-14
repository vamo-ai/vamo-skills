# Role Decomposition

Reference for the `vamo-search` skill: turning a job description and intake notes into a search spec before running any search.

Intake notes mix several kinds of statement, and a search engine treats each kind differently.
Sort every statement into its kind, turn the kind-of-work statements into **lanes**, and bind
everything else to an exact filter and an exact field you will read. The output is one spec that a
person can redline and an agent can run.

Written against the Vamo v2 developers API (`https://api.vamotalent.ai`, `POST /v2/developers/search`
with one JSON body; the fields and their operators are listed live at `GET /v2/developers/fields`,
which wins over this file when they disagree). The sorting and lane method holds for any search
that ranks people by what they built.

On the production host, `/v2/developers/*` can answer `404` or `503` until the v2 engine is
switched on there. Then probe on the v1 route of the same name (`GET /v1/developers/search` and
its query parameters, in the spec at `/openapi.json`), and say in one line that the probes ran on
v1. The spec you write stays the same: its filters name what to bind, whichever route runs it.

This skill stops at the spec and its lane grades. `vamo-search` runs the spec through the
funnel, qualifies people and writes the outreach angle. `vamo-search` covers how to read results.
The `vamo-setup` skill covers setup and access, with a curl for every call named here in its direct API reference.
Its troubleshooting reference covers errors.

---

## The traps

Each of these produces a list that looks fine and is wrong.

1. **The whole brief in one phrase.** The phrase in `rank_by` (`["v", "ANN", ["Embed", "..."]]`) is
   matched against what people built. A school, an employer, a city, a years-of-experience number
   or an adjective inside it filters nothing and pulls the ranking toward repos that happen to
   contain the word. Every non-work criterion leaves the phrase and becomes its own filter.
2. **Describing the person.** "Senior compiler developer" matches no README. "A TypeScript type
   checker written in Rust" matches the people who wrote one. Queries describe artifacts.
3. **A preference promoted to a gate.** Most developers have no school or employer on file. Gating
   on a field removes everyone the data is silent about, including the strongest builders. Silence
   is unknown.
4. **A gate left as prose.** A hard constraint stated in plain language to a search or a model is a
   request. A gate needs a filter that binds and a field you read on every survivor.
5. **Benchmark people returned as candidates.** People the client named are calibration data. Their
   ids go in `exclude`.
6. **One lane.** A role can be filled by several kinds of builder. One query family finds one kind.

---

## Step 1. Gather the inputs

| Input | Why you need it |
| --- | --- |
| Job description and raw intake notes | The statements you will sort. Keep the client's wording. |
| The company's product and public repos | Subsystems become lanes. Their repos become seeds. |
| Benchmark people, as GitHub logins | They set the reputation band and suggest lanes. |
| Example repos the client admires, with their comments | Each comment names a signal you can measure. |
| Off-limits companies and people | Push-down exclusions. |
| People already contacted | Ids for `exclude`. |
| Target count per list | Sizes the recall. |

Questions worth asking when the notes leave them open:

- Which requirements would make you pass on the best builder you have seen?
- Which three people, on your team or outside it, would you clone? GitHub links please.
- Which projects do you respect, and what about each one?
- Who is off limits: companies, portfolio, named people, people you know personally?
- Where must the person be, and are relocation and sponsorship possible?
- What is the seniority floor and ceiling, described as scope of work?
- Which parts of the product are hardest to hire for?

When nobody is available to answer, write the spec anyway. Mark each assumption as assumed and put
the question under `open_questions`.

A contacted list needs resolving to developer ids before it can go in `exclude`.
`POST /v2/developers` with `{"logins": [...], "linkedin": [...]}` returns the `id` for GitHub
usernames and LinkedIn URLs, 25 per call. Rows with only a name or an email, and rows you cannot
resolve, stay on a manual scrub list that is checked before any outreach.

---

## Step 2. Sort every statement

Go through the notes line by line. Quote each statement and give it a bin. The sort table goes at
the top of the spec, because it is the part a client can check fastest.

| Bin | What it is | Where it goes |
| --- | --- | --- |
| **Lane** | A kind of work the person has done | Queries and seeds (Step 4) |
| **Gate** | Binary. The client rejects anyone who fails it | A binding filter plus a field you confirm (Step 6) |
| **Rank** | A preference | An ordering signal. Unknown counts as zero and the person stays |
| **Exclude** | People and companies that must stay out | `["Not", ["current_company_ids", ...]]`, `exclude`, a confirm on every survivor |
| **Screen** | A trait no search can read | A proxy you can observe, or a named item for a person to assess |

Two more kinds of statement set up the run and sit beside the bins:

- **Calibrate.** A benchmark person or an admired repo. It feeds Step 5.
- **Lists.** A count or a second population ("and one or two new grads"). It feeds Step 3.

A statement gets one bin. The one exception: a line can name a Lane and carry a second bin, as
"people who build things for fun" is both a Screen item and the seed of a lane.

**Gate or Rank?** Ask whether the client would pass on the best builder they have ever seen for
failing this. Their own words usually answer it. "I'd take a dropout with a great GitHub over a
4.0" makes school a Rank. "No visa sponsorship" makes country a Gate. When the notes do not settle
it, bin it as Rank and add an open question.

**Screen items need a proxy or an owner.**

| Trait in the notes | Observable proxy |
| --- | --- |
| "Builds for fun", "passion projects" | Owned, finished side projects with steady activity |
| "You can feel the love in it" | A README that explains the hard part, real users, sustained upkeep |
| "Good writer" | Design notes, READMEs and issue replies that explain decisions |
| "Still hands-on" | `details.githubProfile.repos[].commits` in the trailing year, recent `lastActiveDay` |
| "Real contributor", "no contribution farming" | Contributions to one project over many months, substantive in kind |
| "High agency", "low ego", interview questions | None. Question for the first call |

Things that look like one criterion and are two:

- **Location and work authorization.** A country filter confirms where someone is. Authorization
  is a Screen item for the first call.
- **A duration.** "Hasn't written code in two years" becomes
  `["last_active_at", "Gte", "<date>T00:00:00Z"]` at recall and a garden confirm afterward.
  Activity is partial data: the filter drops people with none on file, so run it as a Rank (`"sort":
  "recent"`) unless the client made it a Gate.
- **A list of admired employers.** The list is a Rank. The reason the client gave for the list
  ("developer-led, grew fast") is worth more: it lets you extend the list with peer companies
  yourself and recognise a company the client did not think to name.

**Statements that contradict each other go to `open_questions`.** A named school outside the
country Gate, a seniority ask the comp band cannot reach, a remote-friendly line beside an office
requirement: record both quotes and ask. Resolving it yourself hides a decision that belongs to
the client.

### Read the engagement type first

The same person is a good target for one kind of role and a wasted message for another. Decide
which kind this is before sorting anything else, because it changes the band and several bins.

| Engagement | Band | What changes |
| --- | --- | --- |
| Full-time hire | Floor and ceiling. The gettable middle | Titles far above the seat are cut. Location and relocation matter |
| Contract or freelance | Floor, a loose ceiling | Availability is a Screen item. Location matters only for hours and pay |
| Part-time expert, advisor, reviewer | Floor only | Depth is the point, so principal and staff titles are targets. Location becomes a segment |

**The client's stated bar overrides the table.** When the client says they want the very best and
are glad to see principals, directors and staff developers, set a high devRank floor
(`["devrank", "Gte", 85]`) and no score ceiling, whatever the engagement. Record their words
beside the band.

**Top tier is a different thing from famous.** A principal developer with a few hundred followers
and a household name in the field can carry the same score. The second gets a steady stream of
inbound whatever the role. Keep a reach ceiling on (`["followers", "Lte", <ceiling>]`, set from
the benchmarks), and after enrich set aside anyone with a very large public following
(`details.githubProfile.core.followers`). Write those names to a separate file with the reason,
so the client can see who was left off and overrule it.

For part-time and contract work add two Screen items for the first call: whether the person's
employer permits outside work, and whether their employer is close enough to the client's business
to be a conflict.

A job description for expert work usually lists areas ("expertise in one or more of the
following"). Each bullet is a lane. Covering several of them is a Rank signal.

The duties section names habits you can see in public work:

| Duty in the description | Observable proxy |
| --- | --- |
| "Measurable speedups, and can explain where they came from" | A README that reports numbers against a baseline and explains the cause |
| "Strong testing", "checks edge cases" | A test suite or correctness harness beside the fast path |
| "Builds benchmarks or evaluators" | An owned benchmark or evaluation harness |
| "Clear technical writing", "reviews others' work" | Teaching implementations, design notes, substantive review comments |

---

## Step 3. Split into lists

Two populations with different gates are two lists. A senior hire and a new-grad hire can share
lanes, with different lane priorities, and share nothing else: each list gets its own band, gates,
target count and output file.

**A pay or eligibility tier by region is a segment.** When the role is open across regions with
different terms, keep one list and add a `segment` column computed from the confirmed location.
People whose location is silent stay in with the segment marked unknown.

A Gate that reads a field most people leave empty creates a third kind of list. When graduation
year is a Gate, the people whose education is silent go to an **unverified** list, labeled as
such, so the client can still judge strong builders with thin profiles.

Size the recall from the target: plan to recall about ten to fifteen times the number of finished
candidates each list needs. Step 8 turns that into a query count.

---

## Step 4. Define the lanes

A lane is one kind of builder who could do the job, named by the thing they would have built.
Draw lanes from six sources:

1. **Product subsystems.** One lane per hard subsystem the company builds.
2. **Artifacts named in the notes.** "A database, a query planner, a text editor" is three lanes
   handed to you.
3. **Projects the client respects.** People with deep, long-running contributions to those
   projects are a lane of their own, seeded with `repos` and `{"repos_of": "<org>"}`.
4. **Adjacent crafts.** The same hard problem inside a different product. A sync-engine role
   reaches collaborative editors, multiplayer netcode and offline-first mobile apps.
5. **The care axis.** What someone who loves this problem builds unpaid. This lane finds people a
   stack filter never will.
6. **Benchmark people.** Read what each one built. Every distinct artifact is a candidate lane.

Aim for four to nine lanes. Fewer means the role was read too literally. More means lanes are
synonyms of each other.

Each lane is a card:

```yaml
- lane: incremental-computation
  maps_to: '"an incremental query engine that recomputes cells when upstream data changes"'
  artifact: a library that tracks dependencies between computations and recomputes only what changed
  queries:
    - incremental computation library with dependency tracking and memoized recomputation
    - spreadsheet formula engine with a dependency graph and recalculation order
    - reactive signals runtime with glitch-free propagation, written from scratch
    - differential dataflow engine that updates query results from input deltas
    - build system that reruns only the steps whose inputs changed, with early cutoff
  seed_repos: [<owner/name>]            # canonical projects, for "repos" and {"like": [...]}
  seed_orgs: []                         # for ["contributed_repo_ids", "ContainsAny", {"repos_of": "<org>"}]
  seed_people: []                       # logins for POST /v2/developers/similar
  filters: [["person_languages", "ContainsAny", ["rust:strong", "rust:primary"]]]   # only what is specific to this lane
  evidence: owner                       # owner, contributor, research or teaching (see below)
  pitch: the engine team's recalculation core
  priority: 1                           # 1 center of the role, 2 adjacent, 3 long shot
  grade: untested                       # set in Step 8
```

`evidence` says what kind of proof the lane produces, which decides how you grade it:

| Evidence | The work lives in | Confirm with |
| --- | --- | --- |
| `owner` | Tools people publish under their own name | `evidence.matches[].repo_role`, stars, the README |
| `contributor` | A few canonical projects owned by organizations | `repos[].commits`, months of contribution, a repo deep-research report |
| `research` | Paper repositories | Authorship and what the person implemented. Stars follow the paper |
| `teaching` | From-scratch or annotated implementations | Working code, measured results, clear explanation |

A lane is often mostly one kind. Inference engines and compilers live in organization repos, so
their best people read as contributors. Grading that lane on owner matches would call it weak.

`pitch` names the part of the company's work to lead with for people from this lane. Recording it
now means the outreach for a compiler person and for a sync person starts from different
sentences.

Five to eight queries per lane. Each query is one phrase, sent as
`"rank_by": ["v", "ANN", ["Embed", "<query>"]]`. Query rules:

- **Describe an artifact.** Name the thing and what makes it hard.
- **One idea per query.** Five narrow queries beat one wide one.
- **Name the mechanism.** "Tree shaking", "leader leases", "plural rules", "rollback netcode".
- **Anchor every query in the domain.** A short term or acronym means different things in
  different fields: a cache term pulls storage projects, "streaming" pulls media, "benchmark"
  pulls every language shoot-out. Put the domain noun beside it ("for language model inference",
  "of GPU kernels"). Read the first page for leaks and add the anchor where one shows.
- **Swap the artifact noun to widen.** Parser, then linter, formatter, minifier, bundler, language
  server.
- **For a care-axis lane, name the personal use.** "A habit tracker I built for myself" finds
  different people from "a habit tracking app".
- **Page before rewording.** When a query shows good owners, pull the next page with its `cursor`.
- **Work words only.** If a word describes the person's résumé, it belongs in Step 6.

Seed repos you name from memory are unchecked until a probe returns people for them. Mark them so.

The `vamo-search` domain library (`references/domain-library.md`) holds phrasing sets for fifty domains. Start a lane's
queries there when the domain is listed.

---

## Step 5. Calibrate from benchmarks and examples

Benchmarks and admired repos tell you what "strong" means for this client, in numbers.

**People.** Pull them once:

```
POST /v2/developers
{"logins": ["<benchmark logins>"], "depth": "deep", "facets": ["tags.repos"]}
```

Record for each:

| Reading | Field |
| --- | --- |
| Reputation | devRank: `details.score.cracked.crackedScore` on a looked-up row, `index.profile.devrank` on a search row (the same score) |
| Reach | `details.githubProfile.core.followers`, `core.totalStars` |
| Their best work | `details.githubProfile.repos[]`: `stars`, `owned`, `commits` |
| Rhythm | `details.github.gardenSummary`: `activeWeeks`, `last90Days`, `lastActiveDay` |
| Vocabulary | `repos[].subjects`, `repos[].technologies` |

That is the signature. From it set:

- **The band.** `["devrank", "Gte", <floor>]` and `["devrank", "Lte", <ceiling>]` bracketing the
  benchmarks, with `["devrank", "NotEq", null]` because `Lte` keeps people with no score. With no
  benchmarks, a senior individual-contributor search starts at 70 to 88. For any other level, run
  the first probe with no band, read the scores of the rows you would keep, and bracket those.
- **A ceiling for reach.** When the client names someone "too famous to get", seed with their
  project (`repos`) and their login (`POST /v2/developers/similar`), set the devRank ceiling below
  them and add a followers ceiling. When the person is described and unnamed, ask who it is and
  seed the lane with the canonical repos of the thing described.
- **An activity floor**, when the client wants people building now.
- **Tag vocabulary.** `person_tech` filters on technology tags. Use values you have seen on a real
  row or in `GET /v2/developers/fields`, and leave it out of the first probe until you have.
- **Name spellings.** Places, companies and schools resolve by name. `POST /v2/developers/resolve`
  with `{"place": [...], "company": [...], "school": [...]}` shows how each name reads, and an
  unknown name is a 400 that lists the closest known ones. Check every name once before building a
  funnel on it. Short or ambiguous company names need this most.

**Repos.** Each comment the client attached to an example repo names a signal. Translate it into
something you can read on a candidate:

| The client's comment | Reading on a candidate |
| --- | --- |
| "Contributions every week for two months" | `gardenSummary.activeWeeks`, `last90Days` |
| "Older, with many contributors" | A repo deep-research report: contributor count and spread |
| "Started as a side project, became a product" | Owned repo with growing stars and a company or site attached |
| "A thoughtful README" | Screen item with the README as proxy |

Add every benchmark id to `exclude`, along with current employees of the client. If two benchmarks
have very different signatures, the client is describing two lists: return to Step 3.

---

## Step 6. Bind every criterion

Every Gate, Rank and Exclude gets a row: the filter you send, how far it reaches, and the field
you read to confirm.

| Criterion | Filter at recall | Reach | Confirm by reading |
| --- | --- | --- | --- |
| Kind of work | the phrase (`rank_by` Embed), a keyword lane (`all_repo_text` BM25), `repos`, `{"like": [...]}`, `contributed_repo_ids` with `{"repos_of": "<org>"}`, `person_tech` | everyone | `evidence.matches[]`: `full_name`, `stars`, `similarity` |
| Language | `["person_languages", "ContainsAny", ["rust:strong", "rust:primary"]]` | people with language data | `match.repos[].language`, `core.languages` |
| Owns the work | `"repos": {..., "role": "owner"}` for a seeded project, otherwise none | | `evidence.matches[].repo_role`, `repos[].owned`, `repos[].commits` |
| Reputation band | `devrank` `Gte` and `Lte` with `NotEq null`, `followers` `Lte`, `owned_stars_max` | everyone with a score | devRank on the row |
| Building now | `last_active_at` `Gte`, or `"sort": "recent"` | partial: people with activity on file | `gardenSummary` at `depth=deep` |
| Country, state or city | `["location_ids", "ContainsAny", {"place": [...]}]` (a city means its metro; `"scope": "city"` for the city alone) | people with a resolved location | `details.contact.location`: `country`, `city`, `raw`, `source`; `places_resolved` |
| Works at X now | `current_company_ids` with `{"company": [...]}` | linked profiles | `index.recent_roles`, `details.identity.experience[]` where `current` |
| Worked at X, now or before | `former_company_ids` | linked profiles | `experience[]` entry for X |
| Left X | `past_company_ids` | linked profiles | `experience[]` entry for X with `current` false |
| Off-limits employer | `["Not", ["current_company_ids", ...]]` | linked profiles; unknowns stay in | `core.organization` and current `experience[]` on every survivor |
| School | `school_ids` with `{"school": [...]}` | linked profiles | `details.identity.education[].school` |
| Graduation year | `graduation_year` | linked profiles, partial | `education[].startDate`, `endDate` |
| Role family and level | `title_function`, `title_level`, `current_title` `ContainsAnyToken` | linked profiles | `index.recent_roles`, `experience[].title`, `current`, `startDate` |
| Employer type | `company_size_tier` (partial) | linked profiles | `experience[]` |
| Reachable | `["has_email", "Eq", true]`, `["has_linkedin", "Eq", true]` | everyone | `hasEmail`, `hasLinkedin` on the row |

`details.identity.*`, `details.contact.location` and `index.recent_roles` arrive at `depth=enriched`.
`GET /v2/developers/fields` gives each field's operators and status. A field below `live` runs on
partial data and is named in the response's `not_live`.

Behaviors that decide whether a gate holds:

- **`ContainsAny`, `Eq` and `Gte` drop unknowns; `Lt`, `Lte` and `Not` keep them.** A place or
  language filter returns only people with that value on file, so it binds a Gate and loses
  the silent. An off-limits filter (`Not`) and a ceiling (`Lte`) let the silent through, so
  confirm those on every survivor. A location `source` of `github` is geocoded from a free-text
  string, so read `raw` beside it. The resolved `country` can be empty while `city` or `raw`
  plainly names the place: read all three before calling a location unknown. For a language
  Gate, confirm on the matched repos.
- **Education lists can lead with a secondary school.** Read the university entries when
  confirming a school or a graduation year.
- **A narrower surface changes where the binding runs.** A wrapper or tool that exposes fewer
  filters than the API still returns the fields. Apply the band, the location check and the
  exclusions by reading each row, and keep the same confirm column.
- **`former_company_ids` matches the full employment history**, the current employer included.
  When a company is wanted as a past employer and off limits as a current one, use
  `past_company_ids`, and still confirm `current` is false.
- **"Linked profiles" filters reach a subset.** They match only developers with a linked
  professional profile. Applied to the code funnel, they shrink it to that subset.
- **Dates are free text.** `startDate` and `endDate` come as the source rendered them. Parse the
  year permissively and treat an unparseable date as unknown.
- **`role` is conservative.** `owner` means the repo sits under their namespace. The lead author
  of an organization's repo reads as `contributor`. `repos[].owned` and `repos[].commits` settle
  it.
- **`exclude` holds up to 1000 ids.** Keep benchmarks, client staff and the contacted list in it.
  Advance through a query's own pages with `cursor`, sending the same body.

### Every gate names what happens to unknowns

| `on_unknown` | Meaning | Use when |
| --- | --- | --- |
| `drop` | The person leaves the list | The client rejects anyone unconfirmed (location for an on-site role) |
| `keep_flagged` | The person stays with the gap in `flags` | A fail is disqualifying, silence is acceptable ("not a manager") |
| `second_list` | The person moves to a labeled unverified list | The field is empty for most strong builders (graduation year) |

### Two funnels, joined

Run the lanes as two funnels and join them on the developer `id`.

- **Code funnel.** Lane queries with the everyone-reach filters. This is where the builders are.
- **Profile funnel.** The linked-profile filters (`school_ids`, `former_company_ids`,
  `title_level`) paired with a lane's language filter or a short phrase. This finds the people a
  preference names. Its rows can come back with no matched repos in `evidence.matches`: that is
  the funnel's nature and says nothing about the person.

A person found by both carries the Rank signal as confirmed. A person found only by the code
funnel stays in with that signal unknown.

### Exclusions beyond employers

- **People the client knows.** Maintainers of directly competing projects are usually off limits
  for relationship reasons. Name those projects and exclude their primary maintainers.
- **Repo kinds that are not evidence.** A match on a link list, a course-notes repo or a docs
  repo proves reading, and a typo fix on a famous repo proves less. Keep a person on the strength
  of a tool they own or a long contribution record. One exception follows from the role: when the
  work is explaining, reviewing or writing tasks for others, an owned teaching implementation with
  working code and measured results is strong evidence.
- **Drive-by contributors with high scores.** A contributor match from someone whose own
  repositories and languages sit outside the lane is usually a small fix. Check that their own
  work is in the domain before the score carries them up the list.
- **Activity that is automation.** A garden active nearly every day of the year across a very
  large number of repos reads as scripted. Flag it for a look before it ranks high.
- **Quiet public activity.** Experienced people often do their current work in private. For a
  senior or expert list, recent activity is a Rank signal. Make it a Gate only when the client
  asked for people building in public now.

---

## Step 7. Write the spec

One markdown file. The sort table from Step 2 on top, then the YAML. The client reads the table
and the gates. The agent runs the rest.

```yaml
role:
  company: <name, stage, size, what they ship>
  center: <one sentence: the work at the middle of this role>
  engagement: <full-time | contract | part-time expert>
  segments: <none, or the rule that assigns each person a segment from their location>
  sources: [job description, kickoff notes <date>]

lists:
  - name: senior-engine
    target_n: 40
    recall_n: 500                       # about 10 to 15 times target_n
    band: [["devrank", "Gte", 70], ["devrank", "Lte", 88], ["devrank", "NotEq", null], ["followers", "Lte", <ceiling>]]
    gates:
      - criterion: US based
        note: '"No visa sponsorship right now, so US based only"'
        filter: ["location_ids", "ContainsAny", {"place": ["United States"]}]
        confirm: details.contact.location.country, with raw and source
        on_unknown: drop
      - criterion: individual contributor
        note: '"Not a manager"'
        filter: none
        confirm: current details.identity.experience[].title
        on_unknown: keep_flagged
    rank:
      - criterion: Rust evidence
        note: '"Rust strongly preferred, would take C++ or Zig if the work is good"'
        signal: match.repos[].language is Rust
      - criterion: worked at a peer product company
        note: '"People from <company A> or <company B> would be amazing"'
        signal: profile funnel with past_company_ids, current false
    lanes:                              # lane name: priority for this list
      incremental-computation: 1
      crdt-sync: 1
      query-engine: 1
      spreadsheet-engine: 2
      text-editor: 2
    tiers:
      hand_written: band top third plus a priority-1 lane and an owned tool with real users
      standard: everyone else who passes

lanes:
  - <lane cards from Step 4>

exclude:
  current_companies: [<off-limits employers>]      # ["Not", ["current_company_ids", ...]], confirmed per survivor
  developer_ids: [<benchmarks>, <client staff>, <already contacted>]
  maintainers_of: [<competing projects>]
  manual_scrub: [<contacted rows with no login>]

screen:
  - trait: builds for fun
    note: '"Side projects that are actually finished"'
    proxy: owned repos with releases and a README that explains the hard part
  - trait: work authorization
    proxy: none. Question for the first call.

open_questions:
  - Is the office city a Gate, or is "willing to move" enough to keep a strong person elsewhere in the country?

role_text: >
  <three to six sentences describing the work: the "ask" on each search, and the role for POST /v1/fit-rank at qualification time>

merge:
  order: gates, then confirmed rank signals (count), then lanes hit, then lane priority, then recent activity
  caps: no more than a quarter of a list from one lane, three people per employer, two per repo

output_columns:
  [id, login, list, lane, proving repo, stars, role, devrank, location, location source,
   employer, title, rank signals confirmed, flags, found by]
```

Rules for the file:

- Every Gate has `filter`, `confirm` and `on_unknown`.
- Every line that came from the notes carries the quote.
- Every Screen item has a proxy or the words "question for the first call".
- Anything you assumed is marked assumed. Anything you could not bind goes under
  `open_questions`. Nothing is dropped silently.
- `flags` in the output holds every unknown and every assumption that touched that person.
- `found by` records the lane and funnel, so yield per lane can be read off the final list.

A person returned by several lanes is central to the role. Count the lanes each person was found
in and use it in the order.

`merge` exists because search order compares rows inside one query only. Across lanes, the spec
decides: Gates first, then how many Rank signals are confirmed, then lane priority, then activity,
under caps that keep one team or one lane from filling the list.

---

## Step 8. Probe, grade, tune

Before the full run, test the lanes.

1. Check each body once with `POST /v2/developers/search/validate`. A 400 names the field, place
   or company to fix before anything runs.
2. One page per query: `"depth": "core"`, `limit` 10 to 25, with the list's band and Gate filters.
3. Read `countStatus`. A short page with `shortfallReason: coverage` has more behind its `cursor`,
   so page before judging the lane. Only `corpus` means the index found nobody else.
4. Look up the rows you would keep at `depth=enriched` (`POST /v2/developers` with their `ids`, 25
   per call), and confirm the Gates.
5. Pace the calls: search allows 10 requests per second per key. Run the queries in parallel
   groups of about eight. One long sequential run can exceed a time limit and lose every result.
6. Record which lanes returned each person as you go.

For each lane record four numbers: people returned, rows with real evidence of the lane's kind
(an owned tool, or for a `contributor` lane a canonical project they demonstrably built), rows
inside the band, rows that pass the Gates after enrich. Grade it:

| Grade | Reading | Next move |
| --- | --- | --- |
| Rich | Most rows own or built a real tool, inside the band | Page deeper |
| Mixed | Good people among tutorials, lists and forks | Tighten the artifact wording, add a mechanism |
| Weak | Few builders, or off-topic | Rewrite as a concrete artifact, anchor the domain, or seed with `repos` |

A page with no matched repos in `evidence.matches` cannot be graded on repos. Grade it on the
profiles after enrich.

**Plan the run from the yield.** Keepers per query is the number that matters. If twenty probe
queries produce ten people who pass every Gate, a list of forty needs about eighty more
query-pages of the same quality. Put the pages into Rich lanes first.

Record the grade on the lane card and show weak lanes to the client. A lane that stays weak after
a rewrite is a finding about where this work lives in public: move it to the profile funnel.

The spec is ready when each priority-1 lane grades Rich or Mixed and every Gate has confirmed on
real rows. Send it for redline, then hand it to `vamo-search`.

`role-decomposition-example.md` shows fictional intake notes and the spec they become.

---

## Common mistakes

| Symptom | Cause | Fix |
| --- | --- | --- |
| Results match the stack and nobody is right | One query built from the job title | Lanes from artifacts (Step 4) |
| School or employer words in the phrase | Résumé criteria left in the query | Move them to Step 6 filters |
| Strong builders missing from the list | A preference run as a filter on the code funnel | Two funnels, joined |
| People outside the country on an in-country list | The location was not confirmed after enrich | Read `country`, `city` and `raw` on every survivor |
| Managers and directors on an IC list | No seniority confirm | Read the current `experience[].title` |
| Current employees of an off-limits company in a "worked there before" pull | `former_company_ids` matches current too | Use `past_company_ids` and confirm `current` is false |
| The client's own team in the results | Benchmarks and staff not excluded | Their ids in `exclude` |
| Tutorials and link lists at the top | Query names a topic | Name the artifact and the mechanism |
| A lane graded Weak on a short page | `countStatus` not read | Page with the cursor first |
| A lane of strong contributors graded Weak | Graded on owner matches | Set the lane's `evidence` kind and grade on that |
| Off-field projects on the first page | An ambiguous term with no domain anchor | Add the domain noun to the query |
| Principal developers cut from an expert bench | Full-time gettability rules applied to part-time work | Set `engagement` and drop the ceiling |
| Household names on a top-tier list | No score ceiling was read as no reach screen | Keep a followers ceiling on and set aside very large followings |
| People with a city on file marked location unknown | Only `country` was read | Read `city` and `raw` as well |
| One lane fills the whole list | No merge rule | `merge.caps` in the spec |
| The client says "this is not what I meant" | Spec never shown before the run | Send the Step 7 file for redline first |

---

## Drop-in prompt

```
You are decomposing a role into a search spec for the Vamo v2 developers API
(https://api.vamotalent.ai, POST /v2/developers/search, fields at GET /v2/developers/fields). Write
the spec before any full run. If a /v2/developers route answers 404 or 503, probe on the v1 route
of the same name and say so in one line.

INPUTS: job description, intake notes, benchmark people (GitHub logins), admired repos with the
client's comments, off-limits companies and people, already-contacted list, target count.

0. ENGAGEMENT. Full-time hire, contract, or part-time expert work? Full-time gets a floor and a
   ceiling. Expert work gets a floor only, senior titles are targets, and outside-work permission
   and conflict of interest become first-call questions. Regional pay tiers are a segment column.

1. SORT. Go through the notes line by line. Quote each statement and bin it: LANE (a kind of
   work), GATE (binary, the client rejects on failure), RANK (preference, unknown stays in),
   EXCLUDE (off limits), SCREEN (no search reads it: give an observable proxy or mark it a
   question for the first call). Also mark CALIBRATE (benchmark people, admired repos) and LISTS
   (counts, second populations). Unsure between GATE and RANK: RANK plus an open question.
   Statements that contradict each other: quote both as an open question. Location and work
   authorization are separate items. Put the sort table at the top of the spec.

2. LISTS. Populations with different gates are separate lists, each with a band, gates, target
   and a recall of 10-15 times the target. A gate on a field most people leave empty gets an
   unverified second list.

3. LANES. Four to nine, each named by an artifact. Sources: product subsystems, artifacts named
   in the notes, projects the client respects, adjacent crafts, what a person who loves this
   problem builds unpaid, what each benchmark built. Each lane: what it maps to, the artifact in
   one sentence, 5-8 queries, seed repos, seed orgs, seed people, lane filters, the pitch area,
   priority 1-3, evidence kind (owner, contributor, research, teaching). Queries describe an
   ARTIFACT and its mechanism, one idea each, with the domain noun beside any ambiguous term. Each
   query is one phrase in rank_by [v, ANN, [Embed, "..."]]. Schools, employers, cities, years and
   adjectives never go in the phrase.

4. CALIBRATE. Look up benchmark logins (POST /v2/developers, depth deep, facets [tags.repos]).
   Read devRank (details.score.cracked.crackedScore), core.followers, repos[] (stars, owned,
   commits), gardenSummary, repo tags. Bracket the benchmarks with devrank Gte/Lte plus devrank
   NotEq null. No benchmarks: 70-88 for a senior IC, otherwise set the band from the first probe.
   Turn each comment on an admired repo into a field you can read. Check every place, company and
   school name with POST /v2/developers/resolve. Benchmarks and client staff go in exclude.

5. BIND. For every GATE, RANK and EXCLUDE write the filter, its reach, and the field you read to
   confirm. ContainsAny/Eq/Gte drop unknowns; Lt/Lte/Not keep them, so confirm ceilings and
   exclusions on every survivor. current_company_ids, former_company_ids, past_company_ids,
   school_ids, graduation_year, title_function, title_level and current_title reach linked
   profiles only: run them as a second funnel and join on id. former_company_ids includes the
   current employer: use past_company_ids for "left", and confirm current is false. Each gate
   states on_unknown: drop, keep_flagged or second_list.

6. WRITE one markdown file: sort table, then YAML with role, lists (target, recall, band, gates,
   rank, lanes with priority, tiers), lane cards, exclude, screen, open_questions, role_text,
   merge (order and caps), output_columns. Quote the note behind every line. Mark assumptions.

7. PROBE. Validate each body (POST /v2/developers/search/validate), then one page per query at
   depth core, limit 10-25, in parallel groups of about eight. Read countStatus and page with the
   cursor before judging a short page. Look up keepers at depth enriched, 25 per call. Per lane record:
   returned, real evidence of the lane's kind, in band, pass gates. Track which lanes found each
   person. Grade Rich / Mixed / Weak. Plan the full
   run from keepers per query. Rewrite weak lanes as concrete artifacts and show them in the spec.

Stop after the spec and the lane grades. Ask the client to redline it before the full run.
```
