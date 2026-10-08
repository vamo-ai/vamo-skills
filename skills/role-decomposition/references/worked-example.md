# Worked example: intake notes to search spec

Reference for the `role-decomposition` skill. The company, the people and the notes are invented.
The spec below is what Steps 1 to 7 produce from the notes before any call is made, so values
that depend on calibration or probing are marked `TBD(calibration)` or `TBD(probe)`, and guesses
are marked `ASSUMED` and repeated under `open_questions`. Seed repositories were written from
memory and are unchecked until a probe returns people for them.

## The intake notes

```
Tessera. Series A, 14 people, NYC (Flatiron). Building a collaborative data notebook: think spreadsheet
plus SQL plus charts, multiplayer, works offline. Core engine is Rust compiled to WASM, UI is
TypeScript/React. They wrote their own sync layer (CRDT based) and an incremental query engine that
recomputes cells when upstream data changes.

Roles: 1 senior engineer for the engine team, and they'd take 1 or 2 new grads if they're exceptional.

What the CTO said, roughly in order:

- "I want people who build things for fun. Side projects that are actually finished."
- Engine person needs real systems chops. Rust strongly preferred, would take C++ or Zig if the work is good.
- Loves people who've built a database, a spreadsheet engine, a query planner, a reactive/incremental
  computation library, a CRDT library, a text editor, anything like that.
- "Not a manager. I don't want someone who hasn't written code in two years."
- Top schools are a plus for the new grads (Waterloo, CMU, MIT, Berkeley were named) but "I'd take a
  dropout with a great GitHub over a 4.0".
- New grads: graduated 2025 or graduating 2026/2027.
- Ex Figma, Notion, Linear, Observable, Retool, Hex people would be amazing.
- Do NOT contact anyone currently at Hex or Observable (friendly with founders). Also nobody from their
  investor's portfolio company Rowboat.
- Hybrid, 3 days in office. NYC or willing to move. No visa sponsorship right now, so US based only.
- Comp for senior: 190 to 240 base plus equity.
- "High agency, low ego. Good writers."
- "More people like Mara on our team" (GitHub: mara-example) and "that guy who wrote the incremental
  computation library everyone uses, but he's probably too famous to get".
- They've already emailed about 40 people themselves; list to follow.
- Wants 40 senior candidates and 20 new grads to start.
```

## The spec: sort of the notes

| # | Statement in the notes | Bin | Becomes |
| --- | --- | --- | --- |
| 1 | "collaborative data notebook: think spreadsheet plus SQL plus charts, multiplayer, works offline" | Lane | Product context; lanes `spreadsheet-engine`, `offline-first-data-app` |
| 2 | "Core engine is Rust compiled to WASM, UI is TypeScript/React" | Lane | Lane `rust-wasm-data-engine`; `lang` lever on engine lanes |
| 3 | "They wrote their own sync layer (CRDT based)" | Lane | Lane `crdt-sync` |
| 4 | "an incremental query engine that recomputes cells when upstream data changes" | Lane | Lanes `incremental-computation`, `query-engine` |
| 5 | "1 senior engineer for the engine team, and they'd take 1 or 2 new grads if they're exceptional" | Lists | Two lists |
| 6 | "I want people who build things for fun. Side projects that are actually finished." | Screen (with proxy) + care-axis lane | Proxy: owned repos with releases and a real README. Lane `built-for-fun-systems` |
| 7 | "Engine person needs real systems chops." | Lane | Covered by every engine lane; no separate filter |
| 8 | "Rust strongly preferred, would take C++ or Zig if the work is good." | Rank | `lang=rust,cpp,zig` on engine lanes; Rust is the bonus |
| 9 | "built a database, a spreadsheet engine, a query planner, a reactive/incremental computation library, a CRDT library, a text editor, anything like that" | Lane | Six artifacts, mapped to lanes below |
| 10 | "Not a manager." | Gate (senior list) | Confirm current `experience[].title`. Unknown stays in |
| 11 | "I don't want someone who hasn't written code in two years." | Gate | `pushedAfter=2024-10-08`, confirm on garden summary |
| 12 | "Top schools are a plus for the new grads (Waterloo, CMU, MIT, Berkeley were named)" + "I'd take a dropout with a great GitHub over a 4.0" | Rank (new-grad list) | Profile funnel with `schools`, bonus only |
| 13 | "New grads: graduated 2025 or graduating 2026/2027." | Gate (new-grad list) | No filter. Read `education[].endDate`. Unknown goes to the unverified list |
| 14 | "Ex Figma, Notion, Linear, Observable, Retool, Hex people would be amazing." | Rank | Profile funnel with `pastCompanies` |
| 15 | "Do NOT contact anyone currently at Hex or Observable (friendly with founders)." | Exclude | `excludeCurrentCompanies`, confirmed on every survivor |
| 16 | "Also nobody from their investor's portfolio company Rowboat." | Exclude | `excludeCurrentCompanies` (current). Past employees: open question |
| 17 | "Hybrid, 3 days in office." | Screen | Question for the first call |
| 18 | "NYC or willing to move." | Rank | NYC evidence is a bonus. Relocation is a first-call question |
| 19 | "No visa sponsorship right now, so US based only." | Gate | `country=united states&requireLocation=true`, confirm after enrich. Work authorization itself is a Screen item |
| 20 | "Comp for senior: 190 to 240 base plus equity." | Screen | Human screen. Informs the band ceiling |
| 21 | "High agency, low ego." | Screen | No proxy. Question for the first call |
| 22 | "Good writers." | Screen | Proxy: READMEs and design notes that explain the hard part |
| 23 | "More people like Mara on our team (GitHub: mara-example)" | Calibrate | Enrich, set the band, seed `/similar`, exclude her id |
| 24 | "that guy who wrote the incremental computation library everyone uses, but he's probably too famous to get" | Calibrate | Seed with his project, ceiling below him. He is unnamed: open question |
| 25 | "They've already emailed about 40 people themselves; list to follow." | Exclude | Ids into `exclude` on every call. Blocked until the list arrives |
| 26 | "Wants 40 senior candidates and 20 new grads to start." | Lists | `target_n` 40 and 20 |
| 27 | "Series A, 14 people, NYC (Flatiron)" | Context | Role block. Not a filter |

## The spec: lists, lanes, exclusions

```yaml
role:
  company: Tessera. Series A, 14 people, NYC (Flatiron). Collaborative data notebook
    (spreadsheet + SQL + charts), multiplayer, offline. Rust engine compiled to WASM,
    TypeScript/React UI.
  center: Build the Rust engine that recomputes notebook cells incrementally and syncs them
    across collaborators with CRDTs.
  sources: [kickoff notes (undated)]          # no job description supplied

lists:
  - name: senior-engine
    target_n: 40
    recall_n: 500                              # about 12 times the target
    band: { minCracked: 70, maxCracked: 88, hideHighProfile: true }
      # starting band for a senior IC. Replace with a bracket around mara-example's
      # crackedScore after calibration: TBD(calibration)
    gates:
      - criterion: US based
        note: '"No visa sponsorship right now, so US based only."'
        filter: country=united states&requireLocation=true
        confirm: details.contact.location.country (read `raw` when source is github)
        on_unknown: drop
      - criterion: has written code in the last two years
        note: '"I don''t want someone who hasn''t written code in two years."'
        filter: pushedAfter=2024-10-08
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
        signal: match.repos[].role is owner, or details.githubProfile.repos[].owned with commits
      - criterion: worked at a peer product company
        note: '"Ex Figma, Notion, Linear, Observable, Retool, Hex people would be amazing."'
        signal: found by the profile funnel with pastCompanies; confirm the employer in
          details.identity.experience[] with current=false
      - criterion: in NYC already
        note: '"NYC or willing to move."'
        signal: details.contact.location.city is New York (or state New York). Unknown scores zero
      - criterion: senior scope
        note: '"1 senior engineer for the engine team"'
        signal: profile funnel with experienceTier=senior; experience[].title and startDate.
          Unknown scores zero and stays in
    lanes: [incremental-computation, crdt-sync, query-engine, embedded-database,
            spreadsheet-engine, text-editor, rust-wasm-data-engine, built-for-fun-systems]

  - name: new-grad
    target_n: 20
    recall_n: 300                              # the graduation gate confirms on few rows
    band: { minCracked: 40, maxCracked: 80 }   # ASSUMED. No new-grad benchmark was named
    gates:
      - criterion: US based
        note: '"No visa sponsorship right now, so US based only."'
        filter: country=united states&requireLocation=true
        confirm: details.contact.location.country (read `raw` when source is github)
        on_unknown: drop
      - criterion: graduated 2025, or graduating 2026 or 2027
        note: '"New grads: graduated 2025 or graduating 2026/2027."'
        filter: none (profile funnel narrows with experienceTier=early, yoeMax=2)
        confirm: latest details.identity.education[].endDate, year parsed permissively, in 2025..2027
        on_unknown: second_list            # new-grad-unverified
    rank:
      - criterion: named school
        note: '"Top schools are a plus for the new grads (Waterloo, CMU, MIT, Berkeley were named)"
          but "I''d take a dropout with a great GitHub over a 4.0"'
        signal: found by the profile funnel with schools; confirm in details.identity.education[].school
      - criterion: Rust evidence
        note: '"Rust strongly preferred, would take C++ or Zig if the work is good."'
        signal: match.repos[].language is Rust
      - criterion: finished, owned project
        note: '"if they''re exceptional"; "Side projects that are actually finished."'
        signal: match.repos[].role is owner; repo has a README that explains the design
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
    seed_repos: [salsa-rs/salsa, TimelyDataflow/differential-dataflow, janestreet/incremental, Adapton/adapton.rust]
    seed_orgs: []
    seed_people: [mara-example]                 # plus the unnamed author once identified
    levers: { lang: "rust,cpp,zig,ocaml" }     # ASSUMED ocaml: much of this craft lives there
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
    seed_repos: [automerge/automerge, y-crdt/y-crdt, loro-dev/loro, josephg/diamond-types, vlcn-io/cr-sqlite]
    seed_orgs: [automerge, y-crdt, loro-dev]
    seed_people: []
    levers: { lang: "rust,cpp,zig,typescript" }
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
    seed_repos: [apache/datafusion, duckdb/duckdb, pola-rs/polars, risinglightdb/risinglight, MaterializeInc/materialize]
    seed_orgs: []
    seed_people: []
    levers: { lang: "rust,cpp,zig" }
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
    seed_repos: [tursodatabase/limbo, cberner/redb, spacejam/sled, erikgrinaker/toydb, cozodb/cozo]
    seed_orgs: []
    seed_people: []
    levers: { lang: "rust,cpp,zig" }
    priority: 2
    grade: TBD(probe)

  - lane: spreadsheet-engine
    maps_to: '"a spreadsheet engine"; the notebook recalculates cells'
    artifact: a spreadsheet formula engine with a parser, dependency graph and recalculation order
    queries:
      - spreadsheet formula engine with a dependency graph and recalculation order
      - Excel formula parser and evaluator with range references and array formulas
      - spreadsheet application with an infinite canvas and a Rust calculation core compiled to WebAssembly
      - terminal spreadsheet with formulas and cell dependency tracking
      - reactive notebook runtime that reruns cells in topological order when inputs change
    seed_repos: [ironcalc/IronCalc, handsontable/hyperformula, quadratichq/quadratic]
    seed_orgs: []
    seed_people: []
    levers: {}                                  # no lang lever: strong engines exist in TypeScript
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
    seed_repos: [helix-editor/helix, cessen/ropey, xi-editor/xi-editor, lapce/lapce, zed-industries/zed]
    seed_orgs: []
    seed_people: []
    levers: { lang: "rust,cpp,zig" }
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
    seed_repos: [duckdb/duckdb-wasm, rhashimoto/wa-sqlite, quadratichq/quadratic]
    seed_orgs: []
    seed_people: []
    levers: { lang: "rust,cpp,zig" }
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
    seed_people: [mara-example]
    levers: { lang: "rust,cpp,zig", minRepos: 5 }   # ASSUMED minRepos
    priority: 1 for new-grad, 2 for senior-engine
    grade: TBD(probe)

  # Benchmark lanes: after calibration, read what mara-example built. Each distinct artifact not
  # covered above becomes a lane card here. TBD(calibration)

exclude:
  current_companies: [hex, observable, rowboat]      # excludeCurrentCompanies, every call
  developer_ids:
    - <id of mara-example>                             # TBD(calibration)
    - <ids of the ~40 people Tessera already emailed> # BLOCKED: "list to follow"
    - <ids already returned, when paging>
  confirm_on_every_survivor:
    - details.githubProfile.core.organization and currentRole are not Hex, Observable or Rowboat
    - no details.identity.experience[] row with current=true at Hex, Observable or Rowboat
  note: pastCompanies matches the FULL employment history, so a profile-funnel hit on
    "hex" or "observable" may be a current employee. The confirm above is mandatory there.

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
  - trait: hybrid, 3 days in the Flatiron office
    note: '"Hybrid, 3 days in office. NYC or willing to move."'
    proxy: none. Question for the first call (relocation and office days)
  - trait: US work authorization without sponsorship
    note: '"No visa sponsorship right now"'
    proxy: none. US location is not authorization. Question for the first call
  - trait: comp fit, 190 to 240 base plus equity
    note: '"Comp for senior: 190 to 240 base plus equity."'
    proxy: none. Question for the first call. Used only to keep the band ceiling realistic

open_questions:
  - Waterloo is in Canada. '"Waterloo ... were named"' sits beside '"No visa sponsorship right
    now, so US based only."' Does the US gate apply to new grads who are Canadian or currently in
    Canada? Until answered, the US gate holds and Waterloo matches outside the US are dropped.
  - Who is "that guy who wrote the incremental computation library everyone uses"? Need the
    name or login. He sets the ceiling (maxCracked below him) and seeds a /similar call.
  - '"nobody from ... Rowboat"': current employees only, or anyone who ever worked there?
    Assumed current only. Ever-worked-there needs a read of experience[] on every survivor.
  - Hex and Observable are both off limits (current) and wanted (ex). Confirm that someone who
    left either company is fair game.
  - Is NYC a Gate or a preference? '"NYC or willing to move"' was binned as Rank. Should people
    outside commuting range be kept only if they have signalled willingness to move?
  - Is "not a manager" a hard pass for a tech lead who still ships code every week?
  - Seniority floor and ceiling for the senior hire, described as scope of work. The notes give
    only "senior" and the comp band.
  - What makes a new grad "exceptional" for this CTO? No new-grad benchmark was named, so the
    40-80 band is my assumption.
  - The already-emailed list: please send GitHub logins or profile URLs. Names or emails alone
    cannot be turned into ids by this API.
  - Other benchmark people. One (Mara) is thin for setting a band. Two more GitHub links, ideally.
  - Tessera's own GitHub org and public repos, for seeds and for excluding the current team.
  - Are C++ or Zig candidates with no Rust at all acceptable for the new-grad list too?
  - No job description was supplied. Needed as the role text for fit-rank.
  - Assumed and unconfirmed: the new-grad band, the ocaml and typescript lang levers,
    minRepos=5, every seed repo name (written from memory, not checked against the index),
    and the spelling of `lang`, `schools`, `pastCompanies` and company values.

output_columns: [login, id, list, lane, proving repo, stars, role, language, crackedScore,
  location (city, country, source, raw), current employer, current title, graduation year,
  rank notes, found by (code / profile / both), flags]
```

## Lever bindings

| Criterion | Bin | Filter at recall | Reach | Confirm by reading |
| --- | --- | --- | --- | --- |
| Kind of work | Lane | `q`, `repos`, `orgs`, `lang` per lane card. `subjects`/`techs` only with values seen in calibration | everyone | `match.repos[]` (`fullName`, `stars`, `language`) |
| Owns the work | Rank | none | | `match.repos[].role`, `details.githubProfile.repos[].owned`, `.commits` |
| Reputation band | per list | `minCracked`, `maxCracked`, `hideHighProfile=true` | everyone | `details.score.cracked.crackedScore` |
| Written code in two years | Gate | `pushedAfter=2024-10-08` | everyone | `details.github.gardenSummary` at `depth=deep` |
| US based | Gate | `country=united states&requireLocation=true` | everyone | `details.contact.location.country`, `source`, `raw` |
| NYC | Rank | none on the code funnel. Probe variant: `city=new york` | everyone | `details.contact.location.city`, `state` |
| Not a manager | Gate | none | | `details.identity.experience[]` where `current` is true: `title` |
| Off-limits employer | Exclude | `excludeCurrentCompanies=hex,observable,rowboat` | everyone | `details.githubProfile.core.organization`, `details.identity.experience[]` |
| Benchmarks, already contacted | Exclude | `exclude=<ids>` | everyone | id not in the exclude set |
| Ex Figma, Notion, Linear, Observable, Retool, Hex | Rank | `pastCompanies=figma,notion,linear,observable,retool,hex` (profile funnel) | linked profiles | `details.identity.experience[]`, `current` false |
| Named school | Rank, new-grad | `schools=university of waterloo,carnegie mellon university,massachusetts institute of technology,university of california berkeley` (profile funnel) | linked profiles | `details.identity.education[].school` |
| Graduation year 2025 to 2027 | Gate, new-grad | none. Narrow with `experienceTier=early`, `yoeMax=2` in the profile funnel | linked profiles | `details.identity.education[].endDate` |
| Senior scope | Rank, senior | `experienceTier=senior` (profile funnel) | linked profiles | `experience[].title`, `startDate` |
| Reachable | not a criterion in the notes | none. Read the free flags | everyone | `hasEmail`, `hasLinkedin` |
| Fit to the role text | final ordering | `POST /v1/fit-rank` (`logins` up to 50, `role`, `company: Tessera`) | logins you hold | `fit`, `gettable`, `bridgeable`, `bridge` |

## Planned calls

Shared suffixes:

```
SENIOR_CODE = minCracked=70&maxCracked=88&hideHighProfile=true&country=united states
              &requireLocation=true&pushedAfter=2024-10-08
              &excludeCurrentCompanies=hex,observable,rowboat&exclude=<ids>
GRAD_CODE   = minCracked=40&maxCracked=80&country=united states&requireLocation=true
              &pushedAfter=2025-10-08&excludeCurrentCompanies=hex,observable,rowboat&exclude=<ids>
```

**A. Calibration (Step 5)**

```
GET /v1/developers/enrich?logins=mara-example&depth=deep&facets=tags.repos
```

Record: `details.score.cracked.crackedScore` and `tier`, `details.githubProfile.core.followers`
and `totalStars`, stars on her best two or three `githubProfile.repos[]` with `owned` true,
`gardenSummary.activeWeeks`, `last90Days`, `lastActiveDay`, and the `subjects` / `technologies`
tags on her repos. Then: set the senior band to bracket her score, set an activity floor if her
garden is steady, copy real tag values into lane `subjects`/`techs` levers, add benchmark lanes for
anything she built that the lanes do not cover, put her `id` in `exclude`.

**B. Seed expansion**

```
GET /v1/developers/similar?login=mara-example&limit=50&depth=core
GET /v1/developers/similar?login=<unnamed author>&limit=50&depth=core     # after the client names him
```

`/similar` takes no filters, so band, country and exclusions are applied by reading the rows.

**C. Probe (Step 8): one page per query, 44 queries across 8 lanes, both lists share them**

```
GET /v1/developers/search?q=<lane query>&lang=<lane lang>&depth=core&limit=25&SENIOR_CODE
GET /v1/developers/search?repos=<lane seed_repos>&depth=core&limit=25&SENIOR_CODE      # one per lane with seeds
GET /v1/developers/enrich?ids=<the 25 ids>&depth=enriched                               # to confirm the gates
```

Per lane record: people returned (and `countStatus.shortfallReason` when short), owner matches
(`match.repos[].role == owner`; skip rows where `match.status` is `unattributed`), people inside
the band, people who pass the gates after enrich. Grade Rich / Mixed / Weak on the lane card.
Search and enrich share a per-account rate limit, so the probe runs in batches.

**D. Profile funnel, per list**

```
# senior-engine: peer-company preference
GET /v1/developers/search?pastCompanies=figma,notion,linear,observable,retool,hex
    &lang=rust,cpp,zig&q=<short lane q>&depth=enriched&limit=25
    &country=united states&requireLocation=true&excludeCurrentCompanies=hex,observable,rowboat&exclude=<ids>

# senior-engine: seniority preference
GET /v1/developers/search?experienceTier=senior&lang=rust,cpp,zig&q=<short lane q>&depth=enriched&limit=25&SENIOR_CODE

# new-grad: school preference and graduation-year narrowing
GET /v1/developers/search?schools=university of waterloo,carnegie mellon university,massachusetts institute of technology,university of california berkeley
    &experienceTier=early&lang=rust,cpp,zig&depth=enriched&limit=25&GRAD_CODE
GET /v1/developers/search?experienceTier=early&yoeMax=2&lang=rust,cpp,zig&q=<short lane q>&depth=enriched&limit=25&GRAD_CODE
```

Join both funnels on the developer `id`. Found by both: Rank bonus. Code funnel only: stays in,
that Rank item marked unknown.

**E. Full run, after redline:** page Rich lanes with `cursor` and `exclude` until `recall_n`,
enrich survivors at `depth=enriched` in batches of 25, apply the gate confirms, then
`POST /v1/fit-rank` in batches of 50 logins with the job description as `role`.

## Ready when

- The client has redlined the sort table and the spec and answered the open questions that block a run:
  the unnamed author, the already-emailed list, the Waterloo/US conflict.
- Calibration has replaced the default band.
- Each priority-1 lane grades Rich or Mixed, and every Gate has confirmed on real rows.
