---
name: role-decomposition
description: Use when turning a job description, hiring-manager intake notes, or a kickoff-call transcript into a search spec for sourcing software engineers, before running any search. Also use when a role search returns generic or off-target people because the whole brief went into one query, when a client names benchmark people ("more like her"), or when criteria such as school, graduation year, past employers, location or seniority need to become exact filters. Triggers "decompose this role", "turn these intake notes into a search", "build the search spec", "define the lanes", "what should we search for this req", "generalize this across roles".
---

# Role Decomposition

Intake notes mix five kinds of statement, and a search engine treats each kind differently. Sort
every statement into its kind, turn the kind-of-work statements into **lanes**, and bind everything
else to an exact filter or an exact field you will read. The output is one spec that a person can
redline and an agent can run.

Written against the Vamo Developer API (`https://api.vamotalent.ai`, spec at `/openapi.json`, which
wins over this file when they disagree). The sorting and lane method holds for any search that
ranks people by what they built.

This skill stops at the spec. `vamo-sourcing-agent` runs the spec through the funnel, qualifies
people and writes the outreach angle. `vamo-search` covers API mechanics.

---

## The traps

Each of these produces a list that looks fine and is wrong.

1. **The whole brief in one `q`.** `q` is matched against what people built. A school, an employer,
   a city, a years-of-experience number or an adjective inside `q` filters nothing and pulls the
   ranking toward repos that happen to contain the word. Every non-work criterion leaves `q` and
   gets its own lever.
2. **Describing the person.** "Senior compiler engineer" matches no README. "A TypeScript type
   checker written in Rust" matches the people who wrote one. Queries describe artifacts.
3. **A preference promoted to a gate.** Most developers have no school or employer on file. Gating
   on a field removes everyone the data is silent about, including the strongest builders. Silence
   is unknown. Only a true gate may drop on unknown.
4. **A gate left as prose.** "US only" in a prompt is a wish. A gate needs a filter that binds and
   a field you read to confirm it, written down in the spec.
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
| Off-limits companies and people | Push-down exclusions. |
| People already contacted | Ids for `exclude` on every call. |
| Target count per list | Sizes the recall. |

If the notes leave any of these open, ask before you search:

- Which requirements would make you pass on the best builder you have seen?
- Which three people on your team, or outside it, would you clone? GitHub links please.
- Who is off limits: companies, portfolio, named people?
- Where must the person be, and is relocation or sponsorship possible?
- What is the seniority floor and ceiling, described as scope of work?
- Which parts of the product are hardest to hire for?

---

## Step 2. Sort every statement into five bins

Go through the notes line by line. Each statement lands in exactly one bin. Quote the note beside
it so the client can see where each line of the spec came from.

| Bin | What it is | Where it goes |
| --- | --- | --- |
| **Lane** | A kind of work the person has done | Queries and seeds (Step 4) |
| **Gate** | Binary. The client rejects anyone who fails it | A binding filter plus a field you verify (Step 6) |
| **Rank** | A preference. Nice to have | An ordering bonus. Unknown scores zero and stays in |
| **Exclude** | People and companies that must stay out | `excludeCurrentCompanies`, `exclude` |
| **Screen** | A trait no search can read | A proxy you can observe, or a named item for the human screen |

**Gate or Rank?** Ask: would the client pass on the best builder they have ever seen for failing
this? The client's own words usually answer it. "I'd take a dropout with a great GitHub over a
4.0" makes school a Rank. "No visa sponsorship" makes country a Gate. When the notes do not settle
it, bin it as Rank and list it under `open_questions`.

**Screen items need a proxy or an owner.** "Builds for fun" has a proxy: owned, finished side
projects and steady activity. "Good writer" has a proxy: READMEs and design notes that explain the
hard part. "High agency, low ego" has none. Write it as a question for the first call and keep it
out of the search.

**Statements that contradict each other go to `open_questions`.** A named school outside the
country Gate, a seniority ask that the comp band cannot reach, a remote-friendly line beside an
office requirement: record both quotes and ask. Resolving it yourself hides a decision that
belongs to the client.

---

## Step 3. Split into lists

Two populations with different gates are two lists. A senior hire and a new-grad hire share lanes
and nothing else: each gets its own band, gates, target count and output file. Deciding this now
prevents one blended list where the gates of one group quietly remove the other.

---

## Step 4. Define the lanes

A lane is one kind of builder who could do the job, named by the thing they would have built.
Draw lanes from five sources:

1. **Product subsystems.** One lane per hard subsystem the company builds.
2. **Artifacts named in the notes.** "A database, a query planner, a text editor" is three lanes
   handed to you.
3. **Adjacent crafts.** The same hard problem inside a different product. A sync-engine role
   reaches collaborative editors, multiplayer game netcode and offline-first mobile apps.
4. **The care axis.** What someone who loves this problem builds unpaid. This lane finds people a
   stack filter never will.
5. **Benchmark people.** Read what each one built. Every distinct artifact is a candidate lane.

Aim for four to nine lanes. Fewer means the role was read too literally. More means lanes are
synonyms of each other.

Each lane is a card:

```yaml
- lane: incremental-computation
  maps_to: the engine recomputes dependent cells when upstream data changes
  artifact: a library that tracks dependencies and recomputes only what changed
  queries:
    - incremental computation library with dependency tracking and memoized recomputation
    - spreadsheet formula engine with a dependency graph and recalculation order
    - reactive signals runtime with glitch-free propagation, written from scratch
    - build system that reruns only the steps whose inputs changed
  seed_repos: [salsa-rs/salsa]          # owner/name, for the `repos` lever
  seed_orgs: []                         # for `orgs`
  seed_people: []                       # logins for /v1/developers/similar
  levers: { lang: "rust,cpp,zig" }      # only what is specific to this lane
  priority: 1
```

Query rules:

- **Describe an artifact.** Name the thing and what makes it hard.
- **One idea per query.** Five narrow queries beat one wide one.
- **Name the mechanism.** "Tree shaking", "leader leases", "ICU plural rules", "rollback netcode".
- **Swap the artifact noun to widen.** Parser, then linter, formatter, minifier, bundler, language
  server.
- **Page before rewording.** When a query shows good owners, pull the next pages with `exclude`.
- **Work words only.** If a word describes the person's résumé, it belongs in Step 6.

The `vamo-sourcing-agent` domain library holds phrasing sets for fifty domains. Start a lane's
queries there when the domain is listed.

---

## Step 5. Calibrate the band from benchmark people

Benchmarks tell you what "strong" means for this client in numbers. Pull them once:

```
GET /v1/developers/enrich?logins=<benchmark logins>&depth=deep
```

Record for each: `details.score.cracked`, followers, stars on the repos they own, the star counts
of their best two or three repos, and `details.github.gardenSummary` (`activeWeeks`, `last90Days`,
`lastActiveDay`). That is the signature. Then set:

- **`minCracked` and `maxCracked`** to bracket the benchmarks. With no benchmarks, start a senior
  individual-contributor search at `minCracked=70&maxCracked=88`.
- **A ceiling for reach.** When the client names someone "too famous to get", use that person as a
  seed (`repos` with their project, `/v1/developers/similar` with their login), set `maxCracked`
  below them and add `hideHighProfile=true`.
- **An activity floor** from the garden summary, when the client wants people building now.
- **Tag vocabulary.** Add `facets=tags.repos` to the same call and read the subject and
  technology tags on the benchmarks' repos. `subjects` and `techs` are hard filters on those
  tags, so use values you have seen on a real row.

Add every benchmark id to `exclude`. If two benchmarks have very different signatures, the client
is describing two lists: return to Step 3.

---

## Step 6. Bind every criterion to a lever

Every Gate, Rank and Exclude gets a row: the filter you send, and the field you read to confirm.

| Criterion | Filter at recall | Reach | Confirm by reading |
| --- | --- | --- | --- |
| Kind of work | `q`, `skills`, `repos`, `subjects`, `techs`, `lang`, `orgs` | everyone | `match.repos[]` (`fullName`, `stars`) |
| Owns the work | none | | `match.repos[].role` is `owner` |
| Reputation band | `minCracked`, `maxCracked`, `tier`, `hideHighProfile`, `minStars`, `maxStars` | everyone | `details.score.cracked` |
| Building now | `pushedAfter` | everyone | `details.github.gardenSummary` at `depth=deep` |
| Country or city | `country`, `city`, with `requireLocation=true` | everyone | `details.contact.location` (`country`, `city`, `raw`, `source`) |
| Works at X now | `employer` | everyone | `details.githubProfile.core` |
| Works at X now, by title data | `company`, `titles` | linked profiles | `details.identity.experience[]` |
| Used to work at X | `pastCompanies` | linked profiles | `details.identity.experience[]` |
| Off-limits employer | `excludeCurrentCompanies` | everyone | current employer on every survivor: `details.githubProfile.core`, `details.identity.experience[]` |
| School | `schools` | linked profiles | `details.identity.education[]` |
| Graduation year | none | | `education[].startDate`, `endDate` |
| Seniority | `experienceTier`, `yoeMin`, `yoeMax` | linked profiles | `experience[].title`, `current`, `startDate` |
| Company size, industry | `companySize`, `industries`, `peerCompanies` | linked profiles | `details.identity.experience[]` |
| Reachable | `requireEmail`, `requireLinkedin` | everyone | `hasEmail`, `hasLinkedin` on the row |
| Fit to the role text | `POST /v1/fit-rank` | logins you hold | `fit`, `gettable`, `bridgeable`, `bridge` |

`details.identity.*` and `details.contact.location` arrive at `depth=enriched`.

Four behaviors decide whether a gate holds:

- **`country`, `city` and `lang` filter on evidence.** A developer with no location on file passes
  a `country` filter. For a location Gate send `requireLocation=true` as well, then confirm
  `details.contact.location.country` on every survivor. A `source` of `github` is geocoded from a
  free-text string, so read `raw` beside it.
- **"Linked profiles" filters reach a subset.** They match only developers with a linked
  professional profile. Applied to the code funnel, they shrink it to that subset.
- **Dates are free text.** `startDate` and `endDate` come as the source rendered them. Parse the
  year permissively and treat an unparseable date as unknown.
- **`role` is conservative.** `owner` means the repo sits under their namespace. The lead author
  of an organization's repo reads as `contributor`. Check stars and the repo itself before
  discarding a contributor match on a real tool.

### Two funnels, joined

Run the lanes as two funnels and join them on `developerId`.

- **Code funnel.** Lane queries with the everyone-reach levers. This is where the builders are.
- **Profile funnel.** The linked-profile levers (`schools`, `pastCompanies`, `experienceTier`)
  paired with a lane's `lang`, `techs` or a short `q`. This finds the people a preference names.

A person found by both gets the Rank bonus. A person found only by the code funnel stays in with
that Rank item marked unknown.

When a linked-profile criterion is a true Gate (graduation year on a new-grad list), verify it by
reading the field after enrich and drop on unknown for that list. Then keep the unknowns as a
second list, labeled as unverified on that criterion, so strong builders with thin profiles are
still on the table for the client to judge.

---

## Step 7. Write the spec

One file. The client reads the top half. The agent runs the bottom half.

```yaml
role:
  company: <name, stage, size, what they ship>
  center: <one sentence: the work at the middle of this role>
  sources: [job description, kickoff notes <date>]

lists:
  - name: senior-engine
    target_n: 40
    band: { minCracked: 70, maxCracked: 88, hideHighProfile: true }
    gates:
      - criterion: US based
        note: '"No visa sponsorship right now, so US based only"'
        filter: country=united states&requireLocation=true
        confirm: details.contact.location.country
        on_unknown: drop
    rank:
      - criterion: Rust evidence
        note: '"Rust strongly preferred, would take C++ or Zig if the work is good"'
        signal: match.repos[].language is Rust
      - criterion: worked at a peer product company
        note: '"Ex Figma, Notion, Linear ... would be amazing"'
        signal: profile funnel with pastCompanies
    lanes: [incremental-computation, crdt-sync, query-engine, spreadsheet-engine, text-editor]

lanes:
  - <lane cards from Step 4>

exclude:
  current_companies: [<off-limits employers>]      # excludeCurrentCompanies
  developer_ids: [<benchmarks>, <already contacted>]

screen:
  - trait: builds for fun
    note: '"Side projects that are actually finished"'
    proxy: owned repos with releases and a README that explains the hard part
  - trait: high agency, low ego
    proxy: none. Question for the first call.

open_questions:
  - Is NYC a Gate, or is "willing to move" enough to keep a strong person elsewhere in the US?

output_columns: [login, lane, proving repo, stars, role, band, location, source, rank notes, flags]
```

Rules for the file:

- Every Gate has `filter`, `confirm` and `on_unknown`.
- Every line that came from the notes carries the quote.
- Every Screen item has a proxy or the words "question for the first call".
- Anything you could not bind goes under `open_questions`. Nothing is dropped silently.

---

## Step 8. Probe, grade, tune

Before the full run, test the lanes. One page per query, `depth=core`, `limit` between 10 and 25.

For each lane record four numbers: people returned, owner matches, people inside the band, people
who pass the Gates after enrich. Then grade it:

| Grade | Reading | Next move |
| --- | --- | --- |
| Rich | Most rows are owners of real tools inside the band | Page deeper with `exclude` |
| Mixed | Good people among tutorials, lists and forks | Tighten the artifact wording, add a mechanism |
| Weak | Few owners, or off-topic | Rewrite as a concrete artifact, or seed with `repos` |

Record the grade on the lane card and show weak lanes to the client. A lane that stays weak after
a rewrite is a finding about where this work lives in public: move it to the profile funnel.

The spec is ready when each priority-1 lane grades Rich or Mixed and every Gate has confirmed on
real rows. Hand it to `vamo-sourcing-agent`.

---

## Worked sort

Notes from a kickoff call for a fictional company building a collaborative data notebook with a
Rust engine:

| Statement in the notes | Bin | Becomes |
| --- | --- | --- |
| "Built a database, a spreadsheet engine, a query planner, a CRDT library, a text editor" | Lane | Five lane cards |
| "Their own sync layer and an incremental query engine" | Lane | Product-subsystem lanes, seeds from their repos |
| "People who build things for fun" | Screen | Proxy: owned, finished side projects. Also a care-axis lane |
| "Rust strongly preferred, would take C++ or Zig" | Rank | `lang=rust,cpp,zig` on engine lanes, Rust as bonus |
| "Not a manager" | Gate | Confirm current `experience[].title`. Unknown stays in |
| "Top schools are a plus ... I'd take a dropout with a great GitHub" | Rank | Profile funnel with `schools`, bonus only |
| "Graduated 2025 or graduating 2026/2027" | Gate, new-grad list | Read `education[].endDate`. Unknown goes to the unverified list |
| "Ex Figma, Notion, Linear would be amazing" | Rank | Profile funnel with `pastCompanies` |
| "Do NOT contact anyone currently at Hex or Observable" | Exclude | `excludeCurrentCompanies` |
| "US based only" | Gate | `country` with `requireLocation=true`, confirm on enrich |
| "NYC or willing to move" | Rank | `city` as bonus. Open question on relocation |
| "190 to 240 base" | Screen | Human screen. Informs the band ceiling |
| "High agency, low ego. Good writers" | Screen | Writing has a README proxy. Agency goes to the first call |
| "More people like Mara" | Calibrate | Enrich her, set the band, exclude her id |
| "Probably too famous to get" | Calibrate | Seed with his project, ceiling below him |
| "40 senior candidates and 20 new grads" | Lists | Two lists, two targets |

---

## Common mistakes

| Symptom | Cause | Fix |
| --- | --- | --- |
| Results match the stack and nobody is right | One query built from the job title | Lanes from artifacts (Step 4) |
| School or employer words in `q` | Résumé criteria left in the query | Move them to Step 6 levers |
| Strong builders missing from the list | A preference run as a filter on the code funnel | Two funnels, joined |
| Non-US people on a US-only list | `country` sent alone | Add `requireLocation=true`, confirm after enrich |
| Managers and directors on an IC list | No seniority confirm | Read `experience[].title` on survivors |
| The client's own team in the results | Benchmarks not excluded | Benchmark ids in `exclude` |
| Tutorials and awesome-lists at the top | Query names a topic | Name the artifact and the mechanism |
| The client says "this is not what I meant" | Spec never shown before the run | Send the Step 7 file for redline first |

---

## Drop-in prompt

```
You are decomposing a role into a search spec for the Vamo Developer API
(https://api.vamotalent.ai, spec at /openapi.json). Do not search yet.

INPUTS: job description, intake notes, benchmark people (GitHub logins), off-limits
companies and people, already-contacted ids, target count.

1. SORT. Go through the notes line by line. Put each statement in exactly one bin and quote it:
   LANE (a kind of work), GATE (binary, the client rejects on failure), RANK (preference,
   unknown stays in), EXCLUDE (off limits, confirmed on every survivor), SCREEN (no search can read it: give a proxy you can
   observe, or mark it a question for the first call). Unsure between GATE and RANK: RANK, and
   add an open question. Two statements that contradict each other: quote both as an open question.

2. LISTS. Populations with different gates are separate lists with their own band and target.

3. LANES. Four to nine. One per hard product subsystem, per artifact named in the notes, per
   adjacent craft, one for what a person who loves this problem builds unpaid, and one per
   distinct thing a benchmark person built. Each lane: what it maps to, the artifact in one
   sentence, 5-15 queries, seed repos, seed orgs, seed people, lane-specific levers.
   Queries describe an ARTIFACT and its mechanism, one idea each. Schools, employers, cities,
   years and adjectives never go in q.

4. CALIBRATE. Enrich the benchmark logins at depth=deep. Read cracked score, followers, owned
   stars, gardenSummary. Bracket them with minCracked/maxCracked. No benchmarks: 70-88 for a
   senior IC. Add benchmark ids to exclude.

5. BIND. For every GATE, RANK and EXCLUDE write the filter you send and the field you read to
   confirm. Use subjects/techs values seen on a real row. country/city/lang filter on evidence: add requireLocation=true and confirm
   details.contact.location on every survivor. schools, pastCompanies, company, titles,
   experienceTier, yoeMin/yoeMax reach only developers with a linked profile: run them as a
   second funnel and join on developerId. Graduation year has no filter: read
   education[].endDate. A GATE drops on unknown only when the spec says so, and the unknowns go
   to a second, labeled list.

6. WRITE the spec as YAML: role, lists (target, band, gates with filter/confirm/on_unknown,
   rank), lanes, exclude, screen, open_questions, output_columns. Quote the note behind every
   line. Nothing is dropped silently.

7. PROBE. One page per query at depth=core, limit 10-25. Per lane record returned, owner
   matches, in band, pass gates. Grade Rich / Mixed / Weak. Page rich lanes with exclude,
   rewrite weak ones as concrete artifacts, and show weak lanes in the spec.

Stop after the spec and the lane grades. Ask the client to redline it before the full run.
```
