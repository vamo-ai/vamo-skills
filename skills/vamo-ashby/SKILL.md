---
name: vamo-ashby
description: Use when Vamo and Ashby work together on a hiring pipeline. Vamo supplies what people built; Ashby holds the pipeline; your agent does the reading, judging and writing. Covers checking what is connected, reading a job's pipeline, finding more people like the strongest candidates, adding Vamo context to candidates as notes you write, starting a search from an Ashby role, leaving out people already in Ashby, saving search results to an Ashby job or project, drafting outreach and recording that someone was contacted. Every write to Ashby is previewed and confirmed first. Triggers "pull my Ashby pipeline", "find more like my best candidates", "who in this pipeline actually ships code", "enrich my Ashby candidates", "add Vamo notes to these candidates", "search from my Ashby role", "leave out people already in Ashby", "save these to Ashby", "add them to my Ashby project", "draft outreach for this Ashby job", "note that I reached out".
metadata:
  version: "1.0.0"
  updated: "2026-10-28"
---

# Vamo with Ashby

Ashby holds the pipeline: jobs, candidates, stages, notes and sequences. Vamo knows what engineers
have built. Your agent sits between the two. It reads from both, makes the judgment calls, writes
the notes and the outreach, and asks the person before anything changes in Ashby.

Vamo never writes prose into Ashby on its own. Every note and every message in this skill is written
by your agent, in the person's own voice, and confirmed by them.

`vamo-search` finds people. `vamo-enrich` explains how to read a Vamo profile. `vamo-outreach` covers
writing first messages. This skill covers the parts that involve Ashby.

---

## 1. Check what is connected

Three things can be connected. Check them before you start: the right path depends on which are
there.

| Connection | What it gives you | How to check |
| --- | --- | --- |
| **Vamo** (the MCP connector or an API key) | Search, similar people, lookups, deep research | `vamo-setup` covers it |
| **Ashby's own connector** (the person signs in to Ashby) | Reading jobs, candidates, stages and notes as that person. Writing notes, moving stages and putting a candidate on a job. What it can do follows the person's own Ashby permissions | Look for Ashby tools in your tool list |
| **Vamo's Ashby connection** (an Ashby API key added in Vamo under Setup > Connections) | Saving new candidates into Ashby, saving people to an Ashby project, adding notes, and leaving people already in Ashby out of Vamo searches. It also lets work keep running when no one is in a session | `GET /v1/apps/ashby` returns the connection. With the Vamo connector, the Ashby tools appear only when it is on |

`GET /v1/apps/ashby` answers:

- **`install` with `missingPermissions: []`.** Everything below works.
- **`install` with `needsReconnect: true`.** Ask the person to paste their Ashby key again in Setup > Connections.
- **`install` with entries in `missingPermissions`.** Ask an Ashby admin to turn those on for the key, then paste it again.
- **`install: null`.** Not connected yet. An account owner or admin connects it in Setup > Connections.
- **`403` with `reason: FEATURE_NOT_ENABLED`.** The Ashby app is not switched on for this account. The person can ask Vamo to switch it on. Until then, use Ashby's own connector for Ashby and Vamo for the rest.

With only Ashby's own connector, every recipe still works except saving new candidates, saving to a
project, and the automatic "leave out people in Ashby". For that last one, pass the people's Vamo
ids as `exclude` on a search (step 3).

## 2. Ground rules

- **Your agent writes, Vamo supplies facts.** Notes, summaries, fit judgments and messages are
  yours. Vamo gives you what the person built, their devRank, their links and their history.
- **Preview every write.** Show the person what will change in Ashby (who, which job or project,
  the exact note text) and wait for a yes. Vamo's write routes take `confirm: false` for a preview
  and `confirm: true` to write.
- **Work evidence only in Ashby.** Write about repositories, contributions, languages and what the
  person shipped. Never write school, age, graduation year, photo, location, gender, nationality or
  employer prestige into an Ashby note, even when Vamo returns them. Notes are read by hiring teams
  and reviewed for fairness.
- **Never guess a GitHub username** from a name or an email address. Match on the GitHub or
  LinkedIn link on the Ashby candidate. Set aside anyone with neither and say so.
- **Keep the Ashby candidate id** on every row you carry between the two systems.

## 3. Recipes

### Pull a job's pipeline and see who ships code

1. Read the job's candidates through Ashby's own connector: name, stage, and the GitHub and LinkedIn
   links on each one. Without that connector, ask for a CSV export of the job's candidates.
2. Look them up in Vamo by GitHub username or LinkedIn link, 25 at a time
   (`POST /v2/developers` with `depth: "enriched"`, or the `enrich` tool).
3. Report what each person built, in a table: name, stage, devRank tier, the one or two
   repositories that show their best work, and anyone Vamo could not match. Present the devRank
   tier (Elite, Expert, Advanced), not the raw number.

### Find more like the strongest candidates

1. Pull the pipeline (above). Ask the person which candidates are the bar, or propose the strongest
   two or three from what they built and confirm.
2. For each one, ask Vamo for similar people: `POST /v2/developers/similar` with
   `{"like_person": "<login>", "intent": "same"}`, or the `similar` tool. Add the role's facts
   (place, seniority) as filters.
3. Leave out everyone already in Ashby:
   - **With Vamo's Ashby connection**, refresh the list of who is in Ashby first
     (`POST /v1/apps/ashby/candidates/sync`, or the `ashby_refresh` tool). Searches then leave those
     people out on their own;
     `include_ashby: true` keeps them.
   - **Without it**, pass the Vamo ids of the pipeline you looked up as `exclude`.
4. Merge the lists, drop repeats, and show each person with why they match: the repository or the
   shared work that links them to the candidate they came from.

### Add Vamo context to candidates

1. Pull the candidates and look them up in Vamo (above).
2. Write one short note per person. Use what they built, and nothing from the "never write" list in
   step 2. Keep it under 80 words: one line on what they work on, the one or two repositories that
   show it with a link each, and their devRank tier. Sign it "from Vamo" so the team knows the source.
3. Show all the notes and wait for a yes.
4. Write them through Ashby's own connector (add a note), or with Vamo's Ashby connection:
   `POST /v1/apps/ashby/candidates/{candidateId}/notes` with `{"note": "<text>"}` (the `ashby_note`
   tool).

### Start a search from an Ashby role

1. Read the role: Ashby's own connector, or `GET /v1/apps/ashby/jobs` (the `ashby_roles` tool) for
   open roles with their posting text and public link.
2. Hand the posting to `vamo-search` (a job description is a supported starting point). Leave out
   people already in Ashby as above.

### Save search results to Ashby

Use this after a search, when the person says "save these" or "add them to Ashby".

1. Optionally ask where they go: an Ashby job (`GET /v1/apps/ashby/jobs`), an Ashby project, which
   is a saved list of prospects (`GET /v1/apps/ashby/projects`, the `ashby_projects` tool), or both.
2. Optionally write a short note for each person, the same way as above.
3. Preview: `POST /v1/apps/ashby/push` (the `ashby_add` tool) with
   `{"people": [{"developerId": "<id>", "note": "<your note>"}], "jobId": "<id>", "projectId": "<id>"}`.
   Each person comes back `new` (will be created), `in_ashby` (already there) or `not_found`. Show it.
4. On a yes, send the same body with `"confirm": true`. New people are created with their GitHub
   link, the Vamo tag and the Vamo devRank, GitHub and profile fields. People already in Ashby are
   saved to the project and get the note. Repeat while `remaining` is above 0.

### Draft outreach and record it

1. Write the messages with `vamo-outreach`. A person approves every message, and the agent never
   sends.
2. To run them as an Ashby sequence, the person enrolls the candidates in Ashby and pastes or edits
   the copy there. Use Ashby's own connector for this if it offers sequences.
3. After the person sends, record it on the candidate: a note such as "Reached out on <date> about
   <role>", written and confirmed like any other.

## 4. When something fails

| Answer | What it means | What to do |
| --- | --- | --- |
| `403` `FEATURE_NOT_ENABLED` | The Ashby app is not on for this account | Use Ashby's own connector; ask Vamo to switch it on |
| `409` `ASHBY_NOT_CONNECTED` | No Ashby key in Vamo | An owner or admin connects it in Setup > Connections |
| `409` `ASHBY_NEEDS_RECONNECT` | The key must be pasted again | Same place |
| `409` `ASHBY_MISSING_PERMISSION` | The key lacks the permission in `detail.permission` | An Ashby admin turns it on for the key, then reconnect |
| `422` `ASHBY_KEY_REFUSED` | Ashby did not accept the key | Check it was copied whole and is active |
| `429` | Ashby is limiting requests | Wait a minute and retry |
| `502` | Ashby did not answer | Retry shortly |

The Vamo routes in this skill appear in the API description once the Ashby app is on for the
account. `references/routes.md` lists them in one place.
