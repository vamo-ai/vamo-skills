# Worked example: intake notes to search spec

Worked example for `role-decomposition.md`, in the `vamo-search` skill. The company, the people and the notes are invented.
The spec below is what Steps 1 to 7 produce from the notes before any call is made, so values
that depend on calibration or probing are marked `TBD(calibration)` or `TBD(probe)`, and guesses
are marked `ASSUMED` and repeated under `open_questions`. Company, school, person and repository names are placeholders.

## The intake notes

```
ExampleCo. Series A, 14 people, NYC. Building a collaborative data notebook: think spreadsheet
plus SQL plus charts, multiplayer, works offline. Core engine is Rust compiled to WASM, UI is
TypeScript/React. They wrote their own sync layer (CRDT based) and an incremental query engine that
recomputes cells when upstream data changes.

Roles: 1 senior developer for the engine team, and they'd take 1 or 2 new grads if they're exceptional.

What the CTO said, roughly in order:

- "I want people who build things for fun. Side projects that are actually finished."
- Engine person needs real systems chops. Rust strongly preferred, would take C++ or Zig if the work is good.
- Loves people who've built a database, a spreadsheet engine, a query planner, a reactive/incremental
  computation library, a CRDT library, a text editor, anything like that.
- "Not a manager. I don't want someone who hasn't written code in two years."
- Top schools are a plus for the new grads (School A, School B, School C, School D were named) but "I'd take a
  dropout with a great GitHub over a 4.0".
- New grads: graduated 2025 or graduating 2026/2027.
- Ex Company A, Company B, Company C, Company Y, Company D, Company X people would be amazing.
- Do NOT contact anyone currently at Company X or Company Y (friendly with founders). Also nobody from their
  investor's portfolio company Company Z.
- Hybrid, 3 days in office. NYC or willing to move. No visa sponsorship right now, so US based only.
- Comp for senior: 190 to 240 base plus equity.
- "High agency, low ego. Good writers."
- "More people like one developer on our team" (GitHub: <benchmark-login>) and "that guy who wrote the incremental
  computation library everyone uses, but he's probably too famous to get".
- They've already emailed about 40 people themselves; list to follow.
- Wants 40 senior candidates and 20 new grads to start.
```

## The spec: sort of the notes

| # | Statement in the notes | Bin | Becomes |
| --- | --- | --- | --- |
| 1 | "collaborative data notebook: think spreadsheet plus SQL plus charts, multiplayer, works offline" | Lane | Product context; lanes `spreadsheet-engine`, `offline-first-data-app` |
| 2 | "Core engine is Rust compiled to WASM, UI is TypeScript/React" | Lane | Lane `rust-wasm-data-engine`; a language filter on engine lanes |
| 3 | "They wrote their own sync layer (CRDT based)" | Lane | Lane `crdt-sync` |
| 4 | "an incremental query engine that recomputes cells when upstream data changes" | Lane | Lanes `incremental-computation`, `query-engine` |
| 5 | "1 senior developer for the engine team, and they'd take 1 or 2 new grads if they're exceptional" | Lists | Two lists |
| 6 | "I want people who build things for fun. Side projects that are actually finished." | Screen (with proxy) + care-axis lane | Proxy: owned repos with releases and a real README. Lane `built-for-fun-systems` |
| 7 | "Engine person needs real systems chops." | Lane | Covered by every engine lane; no separate filter |
| 8 | "Rust strongly preferred, would take C++ or Zig if the work is good." | Rank | `SYSTEMS_LANGS` (Rust, C++, Zig) on engine lanes; Rust is the bonus |
| 9 | "built a database, a spreadsheet engine, a query planner, a reactive/incremental computation library, a CRDT library, a text editor, anything like that" | Lane | Six artifacts, mapped to lanes below |
| 10 | "Not a manager." | Gate (senior list) | Confirm current `experience[].title`. Unknown stays in |
| 11 | "I don't want someone who hasn't written code in two years." | Gate | No recall filter (activity data is partial, and a filter would drop the silent). Confirm on garden summary |
| 12 | "Top schools are a plus for the new grads (School A, School B, School C, School D were named)" + "I'd take a dropout with a great GitHub over a 4.0" | Rank (new-grad list) | Profile funnel with `school_ids`, bonus only |
| 13 | "New grads: graduated 2025 or graduating 2026/2027." | Gate (new-grad list) | `graduation_year` 2025 to 2027 in the profile funnel only (partial data). Read `education[].endDate`. Unknown goes to the unverified list |
| 14 | "Ex Company A, Company B, Company C, Company Y, Company D, Company X people would be amazing." | Rank | Profile funnel with `former_company_ids` |
| 15 | "Do NOT contact anyone currently at Company X or Company Y (friendly with founders)." | Exclude | `["Not", ["current_company_ids", ...]]`, confirmed on every survivor |
| 16 | "Also nobody from their investor's portfolio company Company Z." | Exclude | `["Not", ["current_company_ids", ...]]` (current). Past employees: open question |
| 17 | "Hybrid, 3 days in office." | Screen | Question for the first call |
| 18 | "NYC or willing to move." | Rank | NYC evidence is a bonus. Relocation is a first-call question |
| 19 | "No visa sponsorship right now, so US based only." | Gate | `["location_ids", "ContainsAny", {"place": ["United States"]}]`, confirm after enrich. Work authorization itself is a Screen item |
| 20 | "Comp for senior: 190 to 240 base plus equity." | Screen | Human screen. Informs the band ceiling |
| 21 | "High agency, low ego." | Screen | No proxy. Question for the first call |
| 22 | "Good writers." | Screen | Proxy: READMEs and design notes that explain the hard part |
| 23 | "More people like one developer on our team (GitHub: <benchmark-login>)" | Calibrate | Look up, set the band, seed `/v2/developers/similar`, exclude that id |
| 24 | "that guy who wrote the incremental computation library everyone uses, but he's probably too famous to get" | Calibrate | Seed with his project, ceiling below him. He is unnamed: open question |
| 25 | "They've already emailed about 40 people themselves; list to follow." | Exclude | Ids into `exclude` on every call. Blocked until the list arrives |
| 26 | "Wants 40 senior candidates and 20 new grads to start." | Lists | `target_n` 40 and 20 |
| 27 | "Series A, 14 people, NYC" | Context | Role block. Not a filter |

## The spec: lists, lanes, exclusions

```yaml
role:
  company: ExampleCo. Series A, 14 people, NYC. Collaborative data notebook
    (spreadsheet + SQL + charts), multiplayer, offline. Rust engine compiled to WASM,
    TypeScript/React UI.
  center: Build the Rust engine that recomputes notebook cells incrementally and syncs them
    across collaborators with CRDTs.
  sources: [kickoff notes (undated)]          # no job description supplied

lists:
  - name: senior-engine
    target_n: 40
    recall_n: 500                              # about 12 times the target
    band: [["devrank", "Gte", 70], ["devrank", "Lte", 88], ["devrank", "NotEq", null],
           ["followers", "Lte", <ceiling>]]
      # starting band for a senior IC. Replace with a bracket around <benchmark-login>'s
      # devRank after calibration: TBD(calibration)
    gates:
      - criterion: US based
        note: '"No visa sponsorship right now, so US based only."'
        filter: ["location_ids", "ContainsAny", {"place": ["United States"]}]
        confirm: details.contact.location.country (read `raw` when source is github)
        on_unknown: drop
      - criterion: has written code in the last two years
        note: '"I don''t want someone who hasn''t written code in two years."'
        filter: none at recall. last_active_at is partial data and a filter would drop the silent
        confirm: details.github.gardenSummary (lastActiveDay, activeWeeks, last90Days) at depth=deep;
          details.githubProfile.repos[].commits > 0 on at least one repo
        on_unknown: keep_flagged
      - criterion: not a manager
        note: '"Not a manager."'
        filter: none
        confirm: current details.identity.experience[] row (current=true) title has no
          manager/director/VP/head-of wording
        on_unknown: keep_flagged
    rank:
      - criterion: Rust evidence
        note: '"Rust strongly preferred, would take C++ or Zig if the work is good."'
        signal: match.repos[].language is Rust (C++ and Zig score lower, still in)
      - criterion: owns the proving repo
        note: '"Side projects that are actually finished."'
        signal: evidence.matches[].repo_role is owner, or details.githubProfile.repos[].owned with commits
      - criterion: worked at a peer product company
        note: '"Ex Company A, Company B, Company C, Company Y, Company D, Company X people would be amazing."'
        signal: found by the profile funnel with former_company_ids; confirm the employer in
          details.identity.experience[] with current=false
      - criterion: in NYC already
        note: '"NYC or willing to move."'
        signal: details.contact.location.city is New York (or state New York). Unknown scores zero
      - criterion: senior scope
        note: '"1 senior developer for the engine team"'
        signal: profile funnel with title_level senior, staff or principal; experience[].title and startDate.
          Unknown scores zero and stays in
    lanes: [incremental-computation, crdt-sync, query-engine, embedded-database,
            spreadsheet-engine, text-editor, rust-wasm-data-engine, built-for-fun-systems]

  - name: new-grad
    target_n: 20
    recall_n: 300                              # the graduation gate confirms on few rows
    band: [["devrank", "Gte", 40], ["devrank", "Lte", 80]]   # ASSUMED. No new-grad benchmark was named
    gates:
      - criterion: US based
        note: '"No visa sponsorship right now, so US based only."'
        filter: ["location_ids", "ContainsAny", {"place": ["United States"]}]
        confirm: details.contact.location.country (read `raw` when source is github)
        on_unknown: drop
      - criterion: graduated 2025, or graduating 2026 or 2027
        note: '"New grads: graduated 2025 or graduating 2026/2027."'
        filter: profile funnel only, [["graduation_year", "Gte", 2025], ["graduation_year", "Lte", 2027]]
          (partial data: the code funnel carries no graduation filter)
        confirm: latest details.identity.education[].endDate, year parsed permissively, in 2025..2027
        on_unknown: second_list            # new-grad-unverified
    rank:
      - criterion: named school
        note: '"Top schools are a plus for the new grads (School A, School B, School C, School D were named)"
          but "I''d take a dropout with a great GitHub over a 4.0"'
        signal: found by the profile funnel with school_ids; confirm in details.identity.education[].school
      - criterion: Rust evidence
        note: '"Rust strongly preferred, would take C++ or Zig if the work is good."'
        signal: match.repos[].language is Rust
      - criterion: finished, owned project
        note: '"if they''re exceptional"; "Side projects that are actually finished."'
        signal: evidence.matches[].repo_role is owner; repo has a README that explains the design
      - criterion: in NYC already
        note: '"NYC or willing to move."'
        signal: details.contact.location.city is New York
    lanes: [built-for-fun-systems, incremental-computation, crdt-sync, query-engine,
            embedded-database, spreadsheet-engine, text-editor]

  - name: new-grad-unverified
    target_n: as found
    note: Passed every new-grad check except graduation year, which the data is silent on.
      Labeled "graduation year unverified" for the client to judge.

lanes:
  - lane: incremental-computation
    maps_to: '"an incremental query engine that recomputes cells when upstream data changes"'
    artifact: a library that tracks dependencies between computations and recomputes only what changed
    queries:
      - incremental computation library with dependency tracking and memoized recomputation
      - self-adjusting computation framework with a dependency graph and change propagation
      - reactive signals runtime with glitch-free propagation, written from scratch
      - differential dataflow engine that updates query results from input deltas
      - build system that reruns only the steps whose inputs changed, with early cutoff
      - demand-driven query system with red-green invalidation for a compiler
    seed_repos: [<owner/name of the canonical projects for this lane>]
    seed_orgs: []
    seed_people: [<benchmark-login>]                 # plus the unnamed author once identified
    filters: [SYSTEMS_LANGS plus ocaml]        # ASSUMED ocaml: much of this craft lives there
    priority: 1
    grade: TBD(probe)

  - lane: crdt-sync
    maps_to: '"They wrote their own sync layer (CRDT based)"; "multiplayer, works offline"'
    artifact: a CRDT library or sync engine that merges concurrent offline edits without a central lock
    queries:
      - CRDT library for collaborative text and JSON documents with a compact binary encoding
      - sequence CRDT implementation with a run-length encoded operation log
      - local-first sync engine that merges offline edits and replays them over websockets
      - operational transformation server for a collaborative editor
      - rollback netcode for a multiplayer game with deterministic state resync
      - SQLite extension that replicates tables as conflict-free replicated relations
    seed_repos: [<owner/name of the canonical projects for this lane>]
    seed_orgs: [<orgs behind those projects>]
    seed_people: []
    filters: [SYSTEMS_LANGS plus typescript]
    priority: 1
    grade: TBD(probe)

  - lane: query-engine
    maps_to: '"a query planner"; "spreadsheet plus SQL"'
    artifact: a SQL query planner and execution engine with a cost-based or rule-based optimizer
    queries:
      - SQL query planner with a cost-based optimizer and join reordering
      - vectorized columnar query execution engine over Arrow arrays
      - SQL parser and logical plan builder written from scratch
      - incremental view maintenance engine for SQL queries
      - cascades-style query optimizer framework with a memo table
      - datalog engine with semi-naive evaluation
    seed_repos: [<owner/name of the canonical projects for this lane>]
    seed_orgs: []
    seed_people: []
    filters: [SYSTEMS_LANGS]
    priority: 1
    grade: TBD(probe)

  - lane: embedded-database
    maps_to: '"built a database"'
    artifact: a storage engine or embedded database written from scratch
    queries:
      - embedded key-value store with a B-tree pager and write-ahead log
      - LSM-tree storage engine with compaction and bloom filters
      - SQLite-compatible database rewritten in Rust
      - MVCC transaction layer with snapshot isolation for an embedded store
      - distributed SQL database built for learning, with Raft and a query executor
    seed_repos: [<owner/name of the canonical projects for this lane>]
    seed_orgs: []
    seed_people: []
    filters: [SYSTEMS_LANGS]
    priority: 2
    grade: TBD(probe)

  - lane: spreadsheet-engine
    maps_to: '"a spreadsheet engine"; the notebook recalculates cells'
    artifact: a spreadsheet formula engine with a parser, dependency graph and recalculation order
    queries:
      - spreadsheet formula engine with a dependency graph and recalculation order
      - spreadsheet formula parser and evaluator with range references and array formulas
      - spreadsheet application with an infinite canvas and a Rust calculation core compiled to WebAssembly
      - terminal spreadsheet with formulas and cell dependency tracking
      - reactive notebook runtime that reruns cells in topological order when inputs change
    seed_repos: [<owner/name of the canonical projects for this lane>]
    seed_orgs: []
    seed_people: []
    filters: []                                 # no language filter: strong engines exist in TypeScript
    priority: 1
    grade: TBD(probe)

  - lane: text-editor
    maps_to: '"a text editor"'
    artifact: a text editor core, with its own buffer structure and incremental rendering or parsing
    queries:
      - modal text editor written from scratch with a rope buffer
      - rope data structure library for editing very large text files
      - piece table text buffer with undo history
      - incremental parsing library that reuses syntax trees after an edit
      - GPU-rendered code editor with its own text layout engine
    seed_repos: [<owner/name of the canonical projects for this lane>]
    seed_orgs: []
    seed_people: []
    filters: [SYSTEMS_LANGS]
    priority: 2
    grade: TBD(probe)

  - lane: rust-wasm-data-engine
    maps_to: '"Core engine is Rust compiled to WASM"; adjacent craft: heavy engines shipped into a browser'
    artifact: a compute-heavy Rust or C++ core compiled to WebAssembly and driven from a TypeScript UI
    queries:
      - analytical database compiled to WebAssembly that runs SQL in the browser
      - dataframe library with WebAssembly bindings for in-browser analytics
      - Rust core compiled to WebAssembly with a zero-copy bridge to a TypeScript frontend
      - browser design tool with a C++ or Rust rendering engine compiled to WebAssembly
      - offline-first web app that stores its data in SQLite on OPFS
    seed_repos: [<owner/name of the canonical projects for this lane>]
    seed_orgs: []
    seed_people: []
    filters: [SYSTEMS_LANGS]
    priority: 2
    grade: TBD(probe)

  - lane: built-for-fun-systems
    maps_to: '"I want people who build things for fun. Side projects that are actually finished."' (care axis)
    artifact: a finished, owned, from-scratch systems project nobody was paid to write
    queries:
      - toy relational database written from scratch with a B-tree and a SQL parser
      - programming language with its own bytecode virtual machine and garbage collector
      - hobby operating system kernel with a scheduler and a filesystem
      - ray tracer or software rasterizer written from scratch, with a writeup of the design
      - emulator for a game console with cycle-accurate CPU timing
      - regex engine built from scratch with a lazy DFA
    seed_repos: []
    seed_orgs: []
    seed_people: [<benchmark-login>]
    filters: [SYSTEMS_LANGS]                   # count finished owned repos after enrich
    priority: 1 for new-grad, 2 for senior-engine
    grade: TBD(probe)

  # Benchmark lanes: after calibration, read what <benchmark-login> built. Each distinct artifact not
  # covered above becomes a lane card here. TBD(calibration)

exclude:
  current_companies: [<company x>, <company y>, <company z>]      # ["Not", ["current_company_ids", ...]], every call
  developer_ids:
    - <id of <benchmark-login>>                             # TBD(calibration)
    - <ids of the ~40 people ExampleCo already emailed> # BLOCKED: "list to follow"
    - <ids already returned, when paging>
  confirm_on_every_survivor:
    - details.githubProfile.core.organization and currentRole are not Company X, Company Y or Company Z
    - no details.identity.experience[] row with current=true at Company X, Company Y or Company Z
  note: former_company_ids matches the FULL employment history, so a profile-funnel hit on
    <company x> or <company y> may be a current employee. The confirm above is mandatory there.

screen:
  - trait: builds for fun, finishes things
    note: '"I want people who build things for fun. Side projects that are actually finished."'
    proxy: owned repos (role owner / owned true) with releases, a README that explains the hard
      part, and steady gardenSummary.activeWeeks
  - trait: good writer
    note: '"Good writers."'
    proxy: READMEs, design notes or a blog linked in details.contact.socials that explain the hard part
  - trait: high agency, low ego
    note: '"High agency, low ego."'
    proxy: none. Question for the first call
  - trait: hybrid, 3 days in the office
    note: '"Hybrid, 3 days in office. NYC or willing to move."'
    proxy: none. Question for the first call (relocation and office days)
  - trait: US work authorization without sponsorship
    note: '"No visa sponsorship right now"'
    proxy: none. US location is not authorization. Question for the first call
  - trait: comp fit, 190 to 240 base plus equity
    note: '"Comp for senior: 190 to 240 base plus equity."'
    proxy: none. Question for the first call. Used only to keep the band ceiling realistic

open_questions:
  - School A is in another country. '"School A ... were named"' sits beside '"No visa sponsorship right
    now, so US based only."' Does the US gate apply to new grads who are currently in that country? Until answered, the US gate holds and School A matches outside the US are dropped.
  - Who is "that guy who wrote the incremental computation library everyone uses"? Need the
    name or login. He sets the ceiling (devRank below him) and seeds a /v2/developers/similar call.
  - '"nobody from ... Company Z"': current employees only, or anyone who ever worked there?
    Assumed current only. Ever-worked-there needs a read of experience[] on every survivor.
  - Company X and Company Y are both off limits (current) and wanted (ex). Confirm that someone who
    left either company is fair game.
  - Is NYC a Gate or a preference? '"NYC or willing to move"' was binned as Rank. Should people
    outside commuting range be kept only if they have signalled willingness to move?
  - Is "not a manager" a hard pass for a tech lead who still ships code every week?
  - Seniority floor and ceiling for the senior hire, described as scope of work. The notes give
    only "senior" and the comp band.
  - What makes a new grad "exceptional" for this CTO? No new-grad benchmark was named, so the
    40-80 band is my assumption.
  - The already-emailed list: please send GitHub logins or LinkedIn profile URLs. Names or emails
    alone cannot be turned into ids by this API.
  - Other benchmark people. One is thin for setting a band. Two more GitHub links, ideally.
  - ExampleCo's own GitHub org and public repos, for seeds and for excluding the current team.
  - Are C++ or Zig candidates with no Rust at all acceptable for the new-grad list too?
  - No job description was supplied. Needed as the role text for fit-rank.
  - Assumed and unconfirmed: the new-grad band, the ocaml and typescript language filters,
    the seed repositories (to be named with the client), the language value spellings, and
    the school and company names (checked with POST /v2/developers/resolve before the probe).

output_columns: [login, id, list, lane, proving repo, stars, role, language, devrank,
  location (city, country, source, raw), current employer, current title, graduation year,
  rank notes, found by (code / profile / both), flags]
```

## Filter bindings

| Criterion | Bin | Filter at recall | Reach | Confirm by reading |
| --- | --- | --- | --- | --- |
| Kind of work | Lane | the phrase per lane query, `repos`, `{"like": [...]}`, `{"repos_of": "<org>"}`, the lane's language filter. `person_tech` only with values seen in calibration | everyone | `evidence.matches[]` (`full_name`, `stars`, `language`) |
| Owns the work | Rank | none | | `evidence.matches[].repo_role`, `details.githubProfile.repos[].owned`, `.commits` |
| Reputation band | per list | `devrank` `Gte` / `Lte` with `NotEq null`, `followers` `Lte` | everyone with a score | devRank on the row |
| Written code in two years | Gate | none (partial data) | | `details.github.gardenSummary` at `depth=deep` |
| US based | Gate | `["location_ids", "ContainsAny", {"place": ["United States"]}]` | people with a resolved location | `details.contact.location.country`, `source`, `raw` |
| NYC | Rank | none on the code funnel. Probe variant: `{"place": ["New York"]}` (the metro) | people with a resolved location | `details.contact.location.city`, `state` |
| Not a manager | Gate | none | | `details.identity.experience[]` where `current` is true: `title` |
| Off-limits employer | Exclude | `["Not", ["current_company_ids", "ContainsAny", {"company": ["<Company X>", "<Company Y>", "<Company Z>"]}]]` | linked profiles; unknowns stay in | `details.githubProfile.core.organization`, `details.identity.experience[]` |
| Benchmarks, already contacted | Exclude | `"exclude": [<ids>]` | everyone | id not in the exclude set |
| Ex Company A, Company B, Company C, Company Y, Company D, Company X | Rank | `former_company_ids` with those six names (profile funnel) | linked profiles | `details.identity.experience[]`, `current` false |
| Named school | Rank, new-grad | `school_ids` with `{"school": [<the four schools>]}` (profile funnel) | linked profiles | `details.identity.education[].school` |
| Graduation year 2025 to 2027 | Gate, new-grad | `graduation_year` `Gte 2025`, `Lte 2027` in the profile funnel | linked profiles, partial | `details.identity.education[].endDate` |
| Senior scope | Rank, senior | `["title_level", "In", ["senior", "staff", "principal"]]` (profile funnel) | linked profiles | `experience[].title`, `startDate` |
| Reachable | not a criterion in the notes | none. Read the flags on every row | everyone | `hasEmail`, `hasLinkedin` |
| Fit to the role text | final ordering | `POST /v1/fit-rank` (`logins` up to 50, `role`, `company: ExampleCo`) | logins you hold | `fit`, `gettable`, `bridgeable`, `bridge` |

## Planned calls

Every search goes to `POST /v2/developers/search`. Shared pieces, written once and pasted into
each body's `filters` (an `And` list) and top level:

```
PEOPLE        = ["is_bot", "Eq", false], ["is_org_account", "Eq", false]
SYSTEMS_LANGS = ["person_languages", "ContainsAny", ["rust:strong", "rust:primary", "c++:strong",
                 "c++:primary", "zig:strong", "zig:primary"]]     # spellings ASSUMED: check GET /v2/developers/fields
US            = ["location_ids", "ContainsAny", {"place": ["United States"]}]
OFF_LIMITS    = ["Not", ["current_company_ids", "ContainsAny", {"company": ["<Company X>", "<Company Y>", "<Company Z>"]}]]
SENIOR_BAND   = ["devrank", "Gte", 70], ["devrank", "Lte", 88], ["devrank", "NotEq", null], ["followers", "Lte", <ceiling>]
GRAD_BAND     = ["devrank", "Gte", 40], ["devrank", "Lte", 80]
SENIOR_CODE   = filters ["And", [PEOPLE, US, OFF_LIMITS, SENIOR_BAND]], "exclude": [<ids>]
GRAD_CODE     = filters ["And", [PEOPLE, US, OFF_LIMITS, GRAD_BAND]], "exclude": [<ids>]
```

Before the probe, check every place, company and school name once with
`POST /v2/developers/resolve` (`{"company": [...], "school": [...]}`), and each body with
`POST /v2/developers/search/validate`.

**A. Calibration (Step 5)**

```
POST /v2/developers
{"logins": ["<benchmark-login>"], "depth": "deep", "facets": ["tags.repos"]}
```

Record: devRank (`details.score.cracked.crackedScore`), `details.githubProfile.core.followers`
and `totalStars`, stars on their best two or three `githubProfile.repos[]` with `owned` true,
`gardenSummary.activeWeeks`, `last90Days`, `lastActiveDay`, and the `subjects` / `technologies`
tags on their repos. Then: set the senior band to bracket their score, set an activity floor if their
garden is steady, copy real tag values into lane `person_tech` filters, add benchmark lanes for
anything they built that the lanes do not cover, put their `id` in `exclude`.

**B. Seed expansion**

```
POST /v2/developers/similar
{"like_person": "<benchmark-login>", "intent": "same", "filters": ["And", [PEOPLE, US, OFF_LIMITS]], "limit": 50, "depth": "core", "exclude": [<ids>]}
# after the client names the unnamed author: the same with "like_person": "<his login>"
```

Similar takes `filters`, so the location and the exclusions apply at recall. Read the band on the
rows.

**C. Probe (Step 8): one page per query, 44 queries across 8 lanes, both lists share them**

```
{"rank_by": ["v", "ANN", ["Embed", "<lane query>"]], <lane filters> + SENIOR_CODE, "depth": "core", "limit": 25}
{"repos": {"names": [<lane seed_repos>]}, SENIOR_CODE, "depth": "core", "limit": 25}      # one per lane with seeds
POST /v2/developers {"ids": [<the 25 ids>], "depth": "enriched"}                         # to confirm the gates
```

Per lane record: people returned (and `countStatus.shortfallReason` when short), owner matches
(`evidence.matches[].repo_role == owner`; skip rows with no repo in `evidence.matches`), people
inside the band, people who pass the gates after enrich. Grade Rich / Mixed / Weak on the lane
card. Search allows 10 requests per second per key, so the probe runs in batches.

**D. Profile funnel, per list**

```
# senior-engine: peer-company preference
{"filters": ["And", [["former_company_ids", "ContainsAny", {"company": ["<Company A>", "<Company B>", "<Company C>", "<Company Y>", "<Company D>", "<Company X>"]}],
                     SYSTEMS_LANGS, PEOPLE, US, OFF_LIMITS]],
 "rank_by": ["v", "ANN", ["Embed", "<short lane phrase>"]], "depth": "enriched", "limit": 25, "exclude": [<ids>]}

# senior-engine: seniority preference
{"filters": ["And", [["title_level", "In", ["senior", "staff", "principal"]], SYSTEMS_LANGS, PEOPLE, US, OFF_LIMITS, SENIOR_BAND]],
 "rank_by": ["v", "ANN", ["Embed", "<short lane phrase>"]], "depth": "enriched", "limit": 25, "exclude": [<ids>]}

# new-grad: school preference and graduation-year narrowing
{"filters": ["And", [["school_ids", "ContainsAny", {"school": ["<School A>", "<School B>", "<School C>", "<School D>"]}],
                     ["graduation_year", "Gte", 2025], ["graduation_year", "Lte", 2027], SYSTEMS_LANGS, PEOPLE, US, OFF_LIMITS, GRAD_BAND]],
 "depth": "enriched", "limit": 25, "exclude": [<ids>]}
{"filters": ["And", [["graduation_year", "Gte", 2025], ["graduation_year", "Lte", 2027], SYSTEMS_LANGS, PEOPLE, US, OFF_LIMITS, GRAD_BAND]],
 "rank_by": ["v", "ANN", ["Embed", "<short lane phrase>"]], "depth": "enriched", "limit": 25, "exclude": [<ids>]}
```

Join both funnels on the developer `id`. Found by both: Rank bonus. Code funnel only: stays in,
that Rank item marked unknown.

**E. Full run, after redline:** page Rich lanes with `cursor` and `exclude` until `recall_n`,
look up survivors at `depth=enriched` in batches of 25, apply the gate confirms, then
`POST /v1/fit-rank` in batches of 50 logins with the job description as `role`.

If a `/v2/developers` route answers `404` or `503` on the production host, the v2 engine is not on
there yet. Run the same plan on the v1 routes (`GET /v1/developers/search` with the spec's query
parameters) and note in the run report that it ran on v1.

## Ready when

- The client has redlined the sort table and the spec and answered the open questions that block a run:
  the unnamed author, the already-emailed list, the School A/US conflict.
- Calibration has replaced the default band.
- Each priority-1 lane grades Rich or Mixed, and every Gate has confirmed on real rows.
