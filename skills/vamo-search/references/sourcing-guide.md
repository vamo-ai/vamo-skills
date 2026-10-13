# Sourcing Developers by Evidence: A Field Guide for Agents

Reference for the `vamo-search` skill: the long-form method for taking a role from a search to a qualified list of people. `vamo-search` covers the calls and how to read results, `role-decomposition` turns intake notes into the search spec this guide runs, and `vamo-api-access` covers setup. The machine-readable spec at `https://api.vamotalent.ai/openapi.json` is the source of truth for parameters. When this guide and the spec disagree, the spec wins.

A working manual for an agent that sources software developers. It teaches two things at once: how great technical sourcing actually works, and how to do it with the Vamo Developer API. The through-line is simple. **Hire people for what they have built and what they care about, then reach them in a way that earns a reply.** Everything below is in service of that.

This is a reference, not an essay. Graze it. The value is in the volume of worked examples: query phrasings, qualification patterns, outreach bridges, full reasoning traces. Copy the shapes.

---

## Contents

1. The philosophy: why evidence sourcing wins
2. The engine: the work is plain language
3. The sourcing funnel: the shape of every run
4. The knobs: every capability, and when to reach for it
5. The craft of the phrase: writing queries that find real builders
6. The fan-out playbook: one role, many angles
7. Qualification: the questions that turn a list into a campaign
8. Reading a developer: what the signals mean
9. The bridge: outreach that gets replies
10. Reusable playbooks
11. The use-case library: 50 domains, worked (in `domain-library.md`)
12. Full reasoning traces
13. Quick reference

---

## 1. The philosophy: why evidence sourcing wins

Résumés describe what a person claims. Code describes what they actually did. Vamo reads the second one. That is the whole edge, and it produces better hires for a concrete reason: **when you find someone who already chose to build in your problem space, on their own time, you have found someone who will care about the work and be good at it on day one.**

Two axes carry almost all the value:

- **What they KNOW.** Demonstrated stack and depth, proven by shipped code.
- **What they CARE about.** The subjects and problems they return to again and again when nobody is paying them.

The second axis is the moat. Any tool can filter for "Rust." Only evidence sourcing surfaces the person who keeps building air-gapped secure key storage on weekends, which is precisely who will thrive on your air-gapped infra product. That is the feeling a great sourcing run delivers to a hiring team: _"I did not know this person existed, and they are exactly who I have been trying to describe."_

**Two ideas the system is built on. Internalize them; they change how you read every result.**

**A star is not a star.** Popularity is the easiest number in software to obtain and the least informative. A repo starred by five hundred drive-by accounts is weaker than one starred by ten developers whose own work is respected. Vamo weighs stars by who gave them, using signals that are hard to fake: commit access to serious projects that other people independently chose, and owned work that respected builders actually engage with. So when you see modest total stars next to a strong reputation score, that often means _found early by the right people, before the crowd arrived._ That is the discovery win.

**A commit is not a commit.** Volume is cheap. What matters is the character of the output and the calibre of the developers a person builds alongside. **devRank** (0 to 100, the `devrank` field) is graph-derived from exactly that. It cannot be inflated by committing more, and it cannot be bought. Read it as a percentile of standing among real builders, in bands:

| Band         | devRank   | Read as                                                           |
| ------------ | --------- | ----------------------------------------------------------------- |
| Elite        | 85 to 100 | Top 1%. Often celebrity maintainers; frequently hard to get.      |
| Expert       | 70 to 85  | Top 5%. Strong, still gettable. **The sweet spot for senior IC.** |
| Advanced     | 60 to 70  | Top 10%. Solid working developers.                                 |
| Intermediate | 35 to 60  | Broad middle.                                                     |
| Developing   | under 35  | Early, or thin public footprint.                                  |

**Placements, not raw numbers.** "Top 5% for shipping finished work" is a claim a hiring team can act on. "1,240 commits" is not. When you present or reason about a candidate, think in placements and bands. And remember: **a blank is unestablished, never a zero.** No public evidence of a thing means you have no reading on it, which is different from a low reading.

**The business value, stated plainly:**

- **Reply rates track fit, not flattery.** A lateral or half-step-up move gets the best reply rate. A genuine bridge ("we hit the same io_uring back-pressure wall you solved in your storage engine") outperforms "I was impressed by your GitHub" by a wide margin.
- **Gettable beats elite.** A Staff engineer at a trillion-dollar company with fourteen years in gets forty cold emails a week and will not answer a Series-A. The target is the middle-upper band: enough proof-of-work to write a real email about, enough room in their trajectory that the role reads as a step forward.
- **Deliverability is reputation.** A clean, well-qualified, personalized list protects the sender's domain. A sloppy blast burns it. Every part of the funnel below exists to protect that.

---

## 2. The engine: the work is plain language

The single most important input in the whole system is the phrase that describes the work. It is **plain language, a description of the work, not a keyword match.** You write prose that reads like the repositories you hope to find, and Vamo ranks people whose real code looks like that.

```
POST /v2/developers/search
{"rank_by": ["v", "ANN", ["Embed", "<plain language description of the work>"]], "filters": [...], "limit": 50}
```

The difference this makes:

| Weak (keyword)     | Strong (describes the work)                                                         |
| ------------------ | ----------------------------------------------------------------------------------- |
| `react`            | `performance-focused react, virtualized lists, design systems, accessibility`       |
| `golang`           | `high-throughput backend services in go, connection pooling, backpressure`          |
| `machine learning` | `training-loop engineering, mixed-precision, distributed data parallel, checkpointing` |
| `devops`           | `kubernetes operators, custom controllers, reconciliation loops, CRDs`              |
| `security`         | `fuzzing harnesses, memory-safety bugs, sandbox escapes, exploit mitigation`        |

The keyword version ranks anyone who mentions the word. The work-description version ranks people whose repositories are _about_ the thing. Write the phrase specific and evocative. The more it reads like the README of the project you wish existed, the better it matches. Keep places, employers and seniority out of it: those are filters, and in the phrase they only drift the match.

Everything else in the request fences the population the phrase ranks. Lead with the work. Add filters for the facts.

---

## 3. The sourcing funnel: the shape of every run

Great sourcing is a narrowing funnel, and the size of every stage is proportional to how many finished candidates you need. Want 25? Start by recalling several hundred. Want 100? Start with thousands. Drop-off ratios between stages are roughly constant, so you scale the top to hit the bottom.

**The golden rule: widen the recall before you lower the bar. A bad list damages a sender's reputation.** If a stage leaves you thin, go back to the top and widen the recall. Never lower the bar downstream to fill a quota.

| Stage                   | Size (× target) | What happens                                          | API                                       |
| ----------------------- | --------------- | ----------------------------------------------------- | ----------------------------------------- |
| 1. Broad recall         | ~10 to 15×      | 3 to 5 _different_ searches, deliberately over-recall | `search` with phrasing N                  |
| 2. Hydrate              | ~10 to 15×      | pull full profiles for everyone found                 | `enrich?logins=` (batches)                |
| 3. Contactability       | ~3 to 5×        | keep those you can actually reach                     | `["has_email", "Eq", true]`, or keep `hasEmail` rows |
| 4. De-dupe / scrub      | ~3 to 5×        | drop anyone already contacted                         | your own outreach log, then `exclude`     |
| 5. Qualify              | ~1.5 to 2×      | the questions in section 7                              | read profile + `facets`                   |
| 6. Enrich the keepers   | ~1.5 to 2×      | fill missing company / seniority                      | `depth=enriched`                          |
| 7. Rank, diversify, cut | target          | band-score, spread across teams, write angles         | `depth=deep`, `facets=ai.match_rationale` |

Two notes that carry weight:

- **Report the funnel honestly to yourself.** "1,800 recalled → 25 delivered," with the drop reason at each stage, is how you know the run was healthy. A funnel that barely narrowed means the recall was too tight. A funnel that collapsed means the bar moved.
- **Niche domains recall less.** Work that mostly lives inside private companies (payments cores, fraud, ad-serving, internal platforms) shows up less in public code, so widen the recall and lean harder on professional history at qualify time (section 7, Q6).

---

## 4. The knobs: every capability, and when to reach for it

Base URL `api.vamotalent.ai`, auth `Authorization: Bearer $VAMO_API_KEY`. The fields, their types and the operators each takes are listed live at `GET /v2/developers/fields`.

Optional shell shorthand used in examples:

```bash
vamo()     { curl -s "https://api.vamotalent.ai$1" -H "Authorization: Bearer $VAMO_API_KEY"; }
vamoPost() { curl -s -X POST "https://api.vamotalent.ai$1" -H "Authorization: Bearer $VAMO_API_KEY" -H "content-type: application/json" -d "$2"; }
```

### The search engine

| Body | Does | Reach for it when |
| --- | --- | --- |
| `"rank_by": ["v", "ANN", ["Embed", "..."]]` | Ranks people by how close their real work is to the phrase. The engine. | Almost always. Describe the work. |
| `"rank_by": ["all_repo_text", "BM25", "..."]` | Keyword ranking over their repositories' text. | A term the phrase may not carry: a protocol, an acronym, a library name. Fuse it with the phrase lane. |
| `"queries": [lane, lane], "fuse": ["RRF", {"weights": [1, 1]}]` | Two or three lanes in one request, fused. | Phrase plus keyword, or two angles at once. Each lane has its own `filters` and `rank_by`. |
| `"sort": "devrank"` | Orders by reputation (also `followers`, `stars`, `recent`). | No work to match: "the strongest people at X". |

### The reputation dial (the gettability lever)

| Filter | Does | Reach for it when |
| --- | --- | --- |
| `["devrank", "Gte", 60]` | Floor on devRank. | Cut noise. `60` for solid, `70` for senior. |
| `["devrank", "Lte", 88]` | **Ceiling on devRank.** | **Cut celebrity maintainers who will not answer.** Pair with the floor and `["devrank", "NotEq", null]`, since `Lte` alone also keeps people with no devRank. |
| `["owned_stars_max", "Gte", 100]` | Their best own repository's stars. | Loose popularity floor. Use gently; the devRank band is the finer dial. |
| `["followers", "Lte", 5000]` | Ceiling on following. | A relevance-ordered pull where famous names crowd the top. |

The band is the heart of good sourcing. **devRank 70 to 88** is the phrase to memorize: it targets people whose work is real and whose trajectory still has room for your role.

### The evidence gates

| Body | Does | Reach for it when |
| --- | --- | --- |
| `"repos": {"names": ["<owner/name>"], "role": "contributor"}` | People who contribute to (or own: `owner`, `either`) the named repositories. | You can name the projects that define the space. Often stronger than any adjective in the phrase. |
| `"repos": {"names": [...], "hops": 2}` | People who work alongside those contributors. | The ecosystem around a project. |
| `"rank_by": ["v", "ANN", {"like": ["<owner/name>"]}]` | People whose work looks like the named repositories. | Comparable builders with no direct connection. |
| `["person_languages", "ContainsAny", ["rust:strong"]]` | Writes the language (`some`, `strong`, `primary` share). | A language is required. |
| `["last_active_at", "Gte", "<date>T00:00:00Z"]` | Active since a date. | Prefer people active recently. |
| `["contributed_repo_ids", "ContainsAny", {"repos_of": "<owner login>"}]` | Contributed to any repository that org or person owns. | One org's projects, as a filter inside a larger body. For a single repository use the `repos` clause. |

### The professional overlay

| Filter | Does | Reach for it when |
| --- | --- | --- |
| `["current_company_ids", "ContainsAny", {"company": [...]}]` | Current employer. | Target people at a specific company. |
| `["former_company_ids", "ContainsAny", {"company": [...]}]` | Worked there, now or before. | "Ex-fintech," "ex-infra-company." `past_company_ids` for people who have left. |
| `["Not", ["current_company_ids", "ContainsAny", {"company": [...]}]]` | Drop current employees of these. | Do not poach an investor's portfolio or your own team. |
| `["location_ids", "ContainsAny", {"place": [...]}]` | City (its metro area), region or country. | On-site or in-country roles. For remote roles, lead with the work and confirm location at qualify time to see the full field. |
| `["school_ids", "ContainsAny", {"school": [...]}]`, `["graduation_year", "Gte", 2023]` | School and graduation. | A school is a stated preference. Confirm in `details.identity.education` at `depth=enriched`. |
| `["title_function", "In", [...]]`, `["title_level", "In", [...]]`, `["current_title", "ContainsAnyToken", "..."]` | Role family, level, title words. | Seniority has to be bounded at recall time. |

Employer, school, graduation and title fields resolve from linked professional profiles, so they match the subset of developers who have one. Pages get small. Use them as a second funnel beside the code funnel and join the two on developer id. `role-decomposition` covers when a criterion like this should gate and when it should only rank.

### Contactability, depth, enrichment, paging

| Body | Does |
| --- | --- |
| `["has_email", "Eq", true]` | Only people with an email on file. |
| `["has_linkedin", "Eq", true]` | Only people with a matched LinkedIn profile. |
| `"garden": "summary" \| "full"` | With `depth=deep`. `summary` (the default) is a compact activity read: `activeWeeks`, `last90Days`, `lastActiveDay`. `full` is the day-by-day heatmap. |
| `"depth": "core" \| "enriched" \| "deep"` | `core` = GitHub profile; `enriched` = adds LinkedIn identity (title, company, seniority, recent roles); `deep` = adds the yearly activity garden. Start wide at `core`, escalate on the final list. |
| `"facets": ["ai.match_rationale", "ai.person_summary", "ai.repo_summaries"]` | On-demand AI add-ons. `ai.match_rationale` = plain-language "why this person fits this role," the fastest qualify-and-pitch. Resolve async: first read `pending`, call again for the value. The value is `{ matched, reasons }`; check `matched` before reading `reasons`. |
| `cursor`, `exclude`, `limit` | Page forward, skip ids you hold, size the page. |

### The lookups and the reports

| Endpoint                                                                     | Does                                                                                      |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `POST /v2/developers/similar` `{"like_person": "<login>", "intent": "same"}` | Seed one known developer, get people who build like them. The "more like this one" lever. |
| `GET /v2/developers/enrich?logins=`                                          | Full profiles for logins you already hold.                                                |
| `POST /v2/developers` `{"linkedin": [...], "depth": "enriched"}`             | Look people up by LinkedIn profile, login or id.                                          |
| `GET /v2/developers/summaries?logins=`                                       | Short AI summary by login.                                                                |
| `POST /v1/fit-rank` `{"logins":[…],"role":"…","company":"…"}`              | Score up to 50 logins against a role. Returns `fit` (0 to 2), `gettable`, `bridgeable` and a short `bridge` reason, best fit first. A second opinion on your own qualification, and a first draft of the bridge. |
| `GET /v2/developers/emails?logins=`                                          | Get the email addresses observed for a developer. The contact step.                                   |
| `POST /v2/deep-research/jobs` `{"subject":"developers","logins":[…]}`        | Persist a full dossier on a person. The report is saved to the account and readable from then on.                           |
| `POST /v2/deep-research/jobs` `{"subject":"repos","repos":[…]}`              | Persist a full dossier on a repo. Build a library of domain repos and reuse.              |
| `GET /v2/deep-research/reports/{developers/<login> \| repos/<owner>/<name>}` | Read a finished report.                                                                   |

---

## 5. The craft of the phrase: writing queries that find real builders

The best recall comes from **running several distinct phrasings of the same role as separate searches**, then merging. Different phrasings hit different corners of the space, and that spread is where recall comes from. These phrasings are not synonyms of the job title. They are descriptions of _what good work in this area looks like_, from a few angles: how a practitioner would describe it, how a researcher would, how a job post would, and the specific subsystems a strong person would have touched.

**Rule of thumb: 3 to 5 distinct phrasings per role, each its own search.**

Example, for a distributed-systems role, run all of these:

```bash
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","raft consensus implementation from scratch"]],"filters":["is_bot","Eq",false],"limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","lsm-tree storage engine, compaction, write amplification"]],"filters":["is_bot","Eq",false],"limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","distributed transaction coordinator, two-phase commit, MVCC"]],"filters":["is_bot","Eq",false],"limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","gossip membership protocol, failure detection, anti-entropy"]],"filters":["is_bot","Eq",false],"limit":50}'
```

None of these is "distributed systems engineer". Each names a concrete, checkable artifact a strong person in this space would have built. That is the technique. The full library in `domain-library.md` gives phrasing sets for 50 domains.

**Read the repo, not the repo name.** A repository called `raft` might be someone's homework. A repository called `notes` might be a production consensus library. Rank on what the code and README describe, which is exactly what the phrase matches on, and confirm at qualify time.

---

## 6. The fan-out playbook: one role, many angles

Beyond multiple phrasings, these structural angles widen a run. Run them as separate pulls, de-dupe with `exclude`, and merge.

1. **The phrasing spread (primary).** 3 to 5 phrasings, as above.
2. **The project gate.** `"repos": {"names": [...], "role": "contributor"}` for people who contribute to the defining projects.
3. **The ecosystem.** `"repos": {"names": [...], "hops": 2}` pulls the people who work alongside a project's contributors.
4. **The look-alike.** `similar` with `like_person` set to a known great person in the space. Seed a dream hire or a current star, get the neighborhood.
5. **The repo-analog.** Deep-research a canonical repo in the domain (`subject:"repos"`), read its report to sharpen your phrasings and to name notable contributors, then `similar` on the best of them. The repo report is saved to the account after the first run, so build a library.

Seed these from the hiring company itself. Read their product and their public repos. The canonical projects in their space, and the people who maintain them, are your seeds.

---

## 7. Qualification: the questions that turn a list into a campaign

Recall is generous on purpose, so qualification is where the run is won or lost. There are two failure modes, and the whole rubric exists to prevent them:

- **Overqualified (the dead list).** A high devRank feels like a win and is often a miss. Staff-and-above titles, celebrity maintainers, and big-tech-lifers do not answer early-stage cold mail. This is the most common way a list dies.
- **Too thin (nothing to send).** One forty-star toy repo, no company, no way to reach them. Nothing to personalize, nothing to verify, nothing to send.

The target is the middle-upper band: enough proof-of-work to write a real email about, enough room in their story that the role is a step forward.

**These two failure modes describe a full-time hire. For part-time expert, advisory or review work the first one inverts: depth is the point, senior titles are the target, and Q1 and Q2 become "would this person take on outside work of this kind" (see playbook K). Depth still does not mean fame: set aside people with a very large public following on any list, since they are a different outreach problem from a senior developer.

Run each keeper through eight questions. Two clear fails, or four unknowns, and you cut.**

1. **Would this person reply to this company for this role?** A lateral or half-step-up move gets the best reply rate. Cut clear downgrades (Staff or Director being pitched a Senior IC seat), and cut different functions (an engineering manager, a solutions architect, or a devrel for a hands-on IC req). They may be excellent; they will not switch into a step down or a different job.

2. **Overqualified?** Cut when several of these stack: Elite band plus a Staff-plus title; big-tech plus an early-stage seat with no comp story; a top repo in the many-thousands of stars (celebrity maintainer); a very large following. Target senior IC in **devRank 70 to 88**.

3. **Underqualified or too thin?** Cut a best repo under ~40 stars with no LinkedIn, a devRank under ~60 for a senior role, or a profile that is all tutorials, forks, dotfiles, and awesome-lists. Cut the total ghost with no bio, company, location, or LinkedIn.

4. **Compensation fit.** Soft signal, score it, do not hard-cut on it. Someone outside a high-cost metro against a high-cost band is frequently a strong yes, when the role allows it.

5. **Location.** For on-site or hybrid roles, confirm country from the strongest available evidence rather than a raw profile string. Evidence ladder, strongest first: LinkedIn country, then Vamo's resolved country, then university location, then employer headquarters plus a work email, then the raw GitHub location string (treat this last one as a hint to confirm, since "london" can mean the UK or Ontario). For remote roles, lead with the work and confirm region at the end so you see the full field.

6. **Real technical evidence?** Two modes. If the work is the kind that lives in public code, require a repo whose README maps to a must-have for the role (read the description, do not trust the name). If the work mostly lives inside companies (payments, fraud, ad-serving, internal platforms), qualify on professional history instead: tenure at a company whose product _is_ the domain, adjacent open-source as a proxy, and public talks or writing. Record which mode you used for each candidate.

7. **Justify seniority from the nature of the work, not a years-of-experience number.** Evidence ladder, strongest first: current title plus company plus tenure, then trajectory (Engineer → Senior → Staff), then the scale and scope of what they have owned, then the reputation band as a corroborator. Use a years number only as a tiebreak or a contradiction flag.

8. **Is there a specific thing to write the email about?** This is the gate that turns a list into a campaign. Name one concrete, checkable artifact tied to this role: a repo, a subsystem, a technique they used. If you cannot write that one sentence on the first try, the candidate fails, regardless of how good the scores look.

### Check the identity before you trust it

A linked professional profile is matched to a GitHub account, and a match can point at a different person with the same name. One wrong link corrupts the title, the employer, the school and the location together. Before using anything under `details.identity`:

- Compare the name on the row with the name and headline on the linked profile. No overlap means you set the linked profile aside and work from the GitHub side.
- Read `city`, `country` and `raw` together. The resolved country can be empty when the city or the raw string plainly names the place.
- Treat a location as confirmed when two sources agree: `details.contact.location` with `source` of `linkedin` beside a GitHub `raw` string that fits, or an employer and a work email domain that fit.
- When a years-of-experience figure and the account's `joinedAt` disagree by several years, suspect the link before you suspect the person.

### Rank, diversify, cut

Search order compares rows inside one query. Across queries and lanes you rank on evidence you read. A scoring shape that works:

| Signal | Weight | Reading |
| --- | --- | --- |
| Reputation in the gettable middle | high | Peaks near the center of your band and falls off toward both ends. The top of the range is penalized on purpose. |
| Repo evidence | high | A matched tool they own with real adoption. Lower for a toy, lower again for a celebrity project. |
| Identity completeness | medium | Linked profile that passed the name check, an email on file, a confirmed country. |
| Seniority evidence | medium | Title plus tenure first, then trajectory, then scope, then the band as corroboration. |
| Recent activity | medium | `gardenSummary.activeWeeks`, `last90Days`, `lastActiveDay`. |
| Reach penalties | negative | Very large following, a clear step down in title, a different function. |

`POST /v1/fit-rank` gives an independent read (`fit`, `gettable`, `bridgeable`) against the role text. Use it to check your own ordering and to catch people you scored too high on reputation alone.

Then diversify before you cut, so the list is many conversations and not one:

- A cap per repository and a cap per employer. A list drawn from one team is one conversation.
- A cap per primary language unless the role is single-language.
- For a remote role, a cap per country.
- Keep the top of the list to target, and hold the next group as a documented reserve.

### What to hand over

Two artifacts. A table for the sequence tool, and a brief for the person who has to trust it.

The table, one row per person: name, proving repo, repo stars, why they match, LinkedIn URL, GitHub URL, email, current title, current company, tenure, company source, country, country source, seniority source, band, evidence mode, outreach angle, flags.

- **Why they match** is two to four sentences that stand alone: what the repo is, which requirement it proves and how (the technique, the subsystem, the design choice visible in the code or README), and one concrete fact about the work. Read the README before writing it.
- **Source columns are never blank.** Each says where the fact came from, and an inferred value is marked inferred.
- **Evidence mode** is `oss`, `professional` or `both`, from Q6.
- **Flags** holds every unknown. It is the column the reader scans first.

The brief: the parsed requirements, the funnel counts at every stage with the reason for each drop, the people as readable cards, the reserve, the near-misses cut on a single criterion (comp, location, already contacted) since those come back when the role changes, and every query you ran, verbatim, so the run can be repeated.

---

## 8. Reading a developer: what the signals mean

- **devRank and band.** Standing among real builders. Read it as a percentile in a band. Use it as a gettability dial via a `devrank` floor and ceiling (`Gte` and `Lte`, plus `NotEq null`). Present it to a hiring team as a placement ("top 5% by the calibre of engineers they build alongside"), never as a raw number and never as a role-specific percentile.
- **Stars, in context.** A high star count from respected engineers is strong. A modest star count with a strong reputation band often means found early. Read stars through who gave them, which the reputation signals already do for you.
- **The contribution garden (`depth=deep`).** Literal proof of ship. A steady multi-year strip on a young account is a high-slope early-career signal. A dense recent strip is momentum. Sparse-but-aligned still beats prolific-but-off-topic.
- **Identity (`depth=enriched`).** Title, company, tenure for right-sizing seniority and background.
- **Match rationale (`facets=ai.match_rationale`).** The system's own plain-language read on why this person fits the role. The fastest way to both qualify and draft the bridge.
- **The deep-research report.** The full dossier, with placements and strengths. Use it to arm the outreach and the hiring-team conversation. Remember: a blank strength is unestablished, not a zero.

---

## 9. The bridge: outreach that gets replies

A cold email to a developer has two parts. The **pitch** (the role, the comp, the ask) is the sender's voice and is the same for the whole list. The **bridge** is the one sentence that says _why this person's work is relevant to this role_, and it is different for every single person. Economize the pitch if you must. Never economize the bridge. The bridge is the exact judgement that does not scale, which is why it is the whole job.

**The bridge is a claim connecting two things, not a compliment.** "I was impressed by your project" praises a repo and says nothing about the role. A bridge names what they built and ties it to the work:

> "You wrote `<repo>`, a distributed LSM-tree store on a thread-per-core runtime. We are building the same shape of thing and hit the same io_uring back-pressure wall you worked through."

**The shape of a good bridge:**

1. What the repo is, in plain language: what problem it solves and how.
2. Which requirement it proves, named specifically (the technique or subsystem, not "your skills").
3. What it means for this role.

**Good vs weak bridges:**

| Weak | Strong |
| --- | --- |
| "Your work on `<framework>` got my attention!" | "Your custom autograd engine in `<repo>` is exactly the layer we are rewriting for our training stack." |
| "I checked out your project and was impressed." | "Your `raft` implementation handles leader-lease reads, which is the exact correctness problem our new storage tier has open." |
| "Love your GitHub!" | "You have shipped three CRDT libraries. We are moving our collaborative editor off OT and onto CRDTs and want someone who has felt these tradeoffs." |

**The rules of the house voice** (apply to every candidate-facing and client-facing word):

- **No flattery.** State what they built and what it has to do with the work. "I was impressed by" is a tell that the note was scraped.
- **If you cannot write the bridge, do not send.** Thin evidence means the touch parks with a reason. Below the evidence bar, refuse rather than flatter.
- **Vary the shape.** Sample across rhetorical shapes (an observation, a question, a specific technical detail, a shared context, a contrast) so no two consecutive sends read the same. Identical bodies at volume are what spam filters cluster on, so variance is deliverability as well as taste.
- **Front-load personalization.** The first touch carries the bridge. Later touches can lean on the sender's authored copy.
- **No em dashes. No "not X, it's Y" constructions. No aphorisms.**
- **No pedigree talk, no self-congratulation.** Let the work speak. Do not argue why the product is better.
- **Never reference age**, explicitly or by implication ("teenage," "young"). Use school or enrollment stage only. This is a compliance line; check the final copy for it before sending.
- **No population or corpus sizes, no lines-of-code or commit counts.** Use placements and bands.
- **Every claim traces to a field or a URL.** No invented titles, companies, or tenure. Mark an inferred employer as inferred; an inferred employer that turns out to be a former one is the fastest way to burn a first touch.

---

## 10. Reusable playbooks

**A. Job description → qualified list.** Parse the JD into must-haves and a domain. Run the 7-stage funnel (section 3). Output a table: name, repo, repo stars, why they match, LinkedIn, GitHub, email, title, company, tenure, country, seniority evidence, band, devRank, evidence mode, cold-email angle, flags. Plus a short brief with the parsed requirements, the honest funnel counts, and the exact queries run.

**B. "Find more like our best engineer."** Seed `similar` with `like_person` set to a star employee or dream hire, widen with a phrase that captures what makes them great, and read the seed's deep-research report to name what to look for. The similar set is the spine; the semantic query catches who the graph misses.

**C. Talent map / benchmark cohort.** Rank a cohort in a space by reputation band plus subject fit. Each row: who (LinkedIn), the signals (band, stack), the iconic repos, and a language-proof repo linked. A map a hiring team can browse.

**D. Poach an adjacent team.** `current_company_ids` or `former_company_ids` with the competitor and a phrase for the sub-area you want, a `Not` on `current_company_ids` for anyone off-limits. Qualify hard on Q1 (would they move) and Q2 (not so senior they are unreachable).

**E. Maintainers and contributors of a project you admire.** Deep-research the repo, read the report for notable contributors, then `enrich` and `similar` on the strongest. The highest-precision way to find people who have built the exact thing.

**F. Candidate benchmark / one-pager.** Deep-research a single developer, read the placements, render a one-page pitch sheet: persona descriptor, the contribution garden as proof of ship, the two or three strongest placements. Two high signals beat one; several related strengths is a pattern.

**G. Rehydrate a known list.** Have logins already? `enrich?logins=` in batches (or `POST /v2/developers` with LinkedIn profiles), then qualify. No search needed.

**H. Early-career list.** `["graduation_year", "Gte", <year>]` finds people with a linked profile that lists a graduation; run it as one lane, and a second lane with artifact queries and a band set from a benchmark. Keep people whose matched repo is a real tool they own. Enrich at `depth=enriched`, confirm location, then read `details.identity.education[]`: ignore secondary schools, parse the years permissively, and keep people whose university dates fit the window. Rank by activity from the garden summary. Deliver two lists: verified graduates, and highly active builders whose education is silent, labeled as unverified. A strong school is a ranking bonus on either list. Missing education is common among the strongest builders, so a school gate removes most of them.

**I. Deep contributors to projects the client respects.** Search `repos` with the named projects (`role: contributor`) and run a repo deep-research on each to read its contributors. Keep people with a long contribution record on one project: many months, substantive changes, `repos[].commits` to back it. A burst of small pull requests across many famous repos reads as farming. Leave out the primary maintainers of projects that compete directly with the client when the client knows them personally.

**J. Two tiers of outreach.** Split the final list by how much hand work each person merits. A small top tier (top of the band, an owned tool with real users, a priority lane) gets a hand-written note. Everyone else who passes gets the standard sequence with a per-person bridge. Lead each note with the part of the company's work that matches the lane the person came from.

**K. Part-time expert bench.** For advisory, review or task-authoring work, recall with a floor and no ceiling, since principal and staff engineers are the people wanted. Give each area of expertise in the description its own lane, and rank people found in several lanes first. Treat contributors to the canonical projects of the field as primary evidence and confirm depth with `repos[].commits` or a repo deep-research report. Owned teaching implementations and benchmark harnesses count, because the work is explaining and measuring. Segment the list by region when terms differ by region. Leave permission for outside work and conflict of interest to the first call, and flag anyone employed by a company the client works with.

---

## 11. The use-case library: 50 domains, worked

Read `domain-library.md` when you are writing phrasings of the work for a role. It holds 50 worked domains across systems and infrastructure, AI and machine learning, domain-driven and mission work, product and craft, data, and interest and archetype lenses. Each entry gives the weekend-builder read, phrasings to run as separate searches, ways to widen, the evidence that surfaces a real one, and a qualify tell plus a bridge angle.

**Do the fan-out in your head before you touch Vamo.** If someone genuinely loved this problem, what would they have built, and how would they describe it? Write three to six of those descriptions as separate phrasings, name a seed person or a canonical repo, and only then run the searches.

---

## 12. Full reasoning traces

How an agent should actually think through a run, start to finish.

### Trace A. Series-A voice-AI startup, two senior engineers, remote-US-friendly

**Think.** The company builds real-time voice agents. A great fit has felt latency and turn-taking pain, on their own projects, not just used an API. Remote-friendly, so I lead with the work and confirm location at the end. Senior IC, so target the gettable expert band, avoid celebrity maintainers.

**Recall (over-fetch ~12×).** Four phrasings, separate searches:

```bash
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","low-latency voice agents, turn-taking, barge-in"]],"filters":["is_bot","Eq",false],"limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","streaming ASR and TTS, realtime inference"]],"filters":["is_bot","Eq",false],"limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","webrtc audio transport, jitter buffers"]],"filters":["is_bot","Eq",false],"limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","voice activity detection, endpointing"]],"filters":["is_bot","Eq",false],"limit":50}'
```

Plus a look-alike and an ecosystem angle:

```bash
vamoPost /v2/developers/similar '{"like_person":"<a-notable-realtime-voice-builder>","intent":"same","limit":25}'
vamoPost /v2/developers/search '{"repos":{"names":["<a-voice-oss-repo>"],"role":"contributor"},"sort":"devrank","limit":25}'
```

**Hydrate and gate.** De-dupe across angles with `exclude`. Keep `hasEmail`. Now apply the band on the merged set by re-pulling the promising phrasings with `["devrank", "Gte", 70], ["devrank", "Lte", 88], ["devrank", "NotEq", null]` added to `filters`, which drops the celebrity maintainers who will not answer a Series-A.

**Qualify (the 8 questions).** Cut a Staff-at-big-tech (Q1, Q2). Cut a profile that is one starter-kit fork (Q3). For each keeper, confirm the repo README is genuinely about audio latency, not a thin wrapper (Q6). Confirm seniority from title plus tenure at `depth=enriched` (Q7). For each, write the one-sentence bridge (Q8); if I cannot, cut.

**Arm the final list.** `depth=deep` and `facets=ai.match_rationale` on the top ~20. Get emails for those.

**Bridge, per person.** "Your `barge-in` handling in `<repo>` cancels TTS on interrupt inside 80ms, which is the exact responsiveness bar we are building to." Vary the shape across the list.

### Trace B. Poach payments engineers from an adjacent company, senior, US on-site

**Think.** Payments cores live inside companies, so public code is thin. I qualify mostly on professional history, and use any ledger repo as a bonus proof. On-site, so country is a hard gate, confirmed from strong evidence.

**Recall.** Compose the professional overlay with the work:

```bash
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","double-entry ledgers, idempotent payment APIs, reconciliation"]],"filters":["And",[["former_company_ids","ContainsAny",{"company":["<company>","<company>"]}],["location_ids","ContainsAny",{"place":["United States"]}],["is_bot","Eq",false]]],"depth":"enriched","limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","payments infrastructure, money movement, PCI"]],"filters":["And",[["devrank","Gte",65],["devrank","Lte",88],["devrank","NotEq",null],["is_bot","Eq",false]]],"depth":"enriched","limit":50}'
vamoPost /v2/developers/search '{"rank_by":["v","ANN",["Embed","payment processing"]],"filters":["And",[["person_languages","ContainsAny",["go:strong","go:primary"]],["is_bot","Eq",false]]],"depth":"enriched","limit":50}'
```

**Qualify.** Q6 in professional mode: tenure at a company whose product is payments counts as evidence even without a public ledger repo. Q7: title plus company plus tenure from `details.identity`. Q1: keep laterals and half-steps-up, cut anyone the role would be a downgrade for.

**Bridge.** Lead with the résumé fact tied to a concrete role need, backed by any repo: "You spent three years on the ledger core at `<company>`. We are standing ours up now and want someone who has handled reconciliation at volume."

---

## 13. Quick reference

**The engine.** The phrase is plain language. Describe the work; facts go in `filters`. Run 3 to 5 distinct phrasings as separate searches.

**The gettability band.** devRank 70 to 88 for senior IC (`Gte 70`, `Lte 88`, `NotEq null`). Floor cuts noise, ceiling cuts celebrities. Never `sort: devrank` without a ceiling.

**Depth ladder.** `core` to recall wide → `enriched` for identity on the final list → `deep` for the garden on finalists. `facets=ai.match_rationale` to qualify and draft in one.

**Contact and research.** `hasEmail` to gate → `emails?logins=` for the finalists' addresses. `similar` for look-alikes. Deep-research repos once and reuse the saved report.

**The funnel.** Recall ~10 to 15× → hydrate → contactable ~3 to 5× → scrub already-contacted → qualify ~1.5 to 2× → enrich keepers → rank and cut to target. A bad list damages a sender's reputation. Widen the top, never lower the bar.

**The 8 questions.** Would they reply · overqualified · too thin · comp fit · location proven · real technical evidence · seniority from the work · a specific thing to write about. Two fails or four unknowns, cut.

**The bridge.** One sentence tying what they built to this role. A claim, not a compliment. If you cannot write it, do not send.

**House voice.** No flattery, no em dashes, no "not X, it's Y," no pedigree, no age, no population or LOC counts. Every claim traces to a field or a URL. Vary the shape.

**The five habits of a great sourcing agent.**

1. Start from a hypothesis about the person, not the JD's keywords.
2. Write a rich phrase of the work; fan out to several phrasings and angles; over-recall.
3. Target the gettable band; qualify against the eight questions.
4. Read evidence (repos, garden, band, match rationale) before you decide.
5. Write a real bridge per person; if the evidence is too thin to bridge, do not send.
