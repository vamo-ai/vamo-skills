---
name: vamo-workflows
description: Use when wiring the Vamo Developer API into something that runs more than once: your own sourcing or hiring agent, a recurring search, a pipeline that enriches people before a message goes out, or a hand-off between Vamo and other tools such as an applicant tracking system, an email sender or a spreadsheet. Also use when designing the data that moves between those steps. Triggers "build a sourcing agent", "automate this search", "run this every week", "pipe Vamo data into our sequences", "sync with our ATS", "connect Vamo to our workflow", "what should the agent loop look like".
metadata:
  version: "1.0.0"
  updated: "2026-10-09"
---

# Vamo Workflows

A one-off search is a conversation. A workflow is the same work made repeatable: fixed inputs,
fixed steps, a record of what ran, and a clean hand-off to whatever acts next. This skill covers
the patterns and the rules that keep a repeated run correct.

Vamo's part in any workflow is the same: who the people are and the evidence for it. Sending
mail, storing candidates and scheduling belong to other tools. `vamo-api-access` covers setup,
`vamo-search` finds people, `vamo-enrich` fills in people you hold, and `role-decomposition`
turns a role into a search spec. The API's own description at
`https://api.vamotalent.ai/openapi.json` wins over this file on routes and fields.

---

## Rules for anything that runs twice

- **The developer `id` is the key.** It is stable across renames. Store it with every record and
  join on it. Usernames change.
- **Keep a seen list.** Store the ids already returned, contacted or rejected, and send them in
  `exclude`. A second run should return new people.
- **Save the spec, not the results.** Keep the queries, filters and band that produced a list.
  The list goes stale. The spec can be run again.
- **Batch and pace.** Lookups take up to 25 people per call. Run searches in parallel groups of
  about eight. Search and lookup share a rate limit per account, listed in the spec.
- **Wait for background values.** Summary and rationale facets resolve in the background. Read
  once, then read again for anything still `pending`.
- **Allow time.** A search can take ten to twenty seconds. Use a timeout of at least sixty.
- **One key per agent.** Name it for the agent, grant what that agent calls, and keep it out of
  logs, prompts and output files.
- **Carry unknowns through.** A blank location or title stays blank in the output with a flag.
  A step that fills a blank with a guess corrupts every step after it.
- **A person approves anything that leaves.** The workflow prepares messages and updates. A
  human sends them.

---

## The record that moves between steps

Agree on one shape and every step can be replaced without touching the others.

```json
{
  "vamo_id": "<developer id>",
  "login": "<github username>",
  "name": "<name>",
  "found_by": ["<lane or source>"],
  "proving_repo": { "full_name": "<owner/name>", "stars": 0, "role": "owner" },
  "what_they_built": "<one plain sentence>",
  "cracked": { "tier": "<tier>", "score": 0 },
  "location": { "city": null, "country": null, "raw": null, "source": null },
  "current": { "title": null, "company": null },
  "links": { "github": "<url>", "linkedin": null },
  "has_email": false,
  "flags": ["<each unknown or assumption>"]
}
```

For a spreadsheet, the same fields flattened to columns.

---

## Patterns

### Your own sourcing agent

The loop, with the skill that covers each step:

1. **Decompose** the role into a spec (`role-decomposition`).
2. **Probe** each lane with one page and grade it.
3. **Run** the lanes that graded well, paging with the seen list (`vamo-search`).
4. **Fill in** the people you would keep (`vamo-enrich`).
5. **Qualify** on evidence you read, and rank.
6. **Hand over** records in the shape above, with what ran and what is unknown.

Give the agent a stopping rule before it starts: a target count, a maximum number of rounds, and
the instruction to report a thin lane instead of lowering the bar to fill a quota.

### A search that runs every week

1. Store the spec and the seen list.
2. Each run: the same lanes, with `pushedAfter` set to the last run date to favor people active
   since then, and `exclude` carrying the seen list.
3. Deliver only the new people, and add them to the seen list.

When a run comes back empty, say so. A quiet week is information.

### Enrichment in front of a message

*Every message that goes out carries one sentence about the recipient's own work.*

1. Input: the recipient list with GitHub usernames.
2. For each person: profile and summaries (`vamo-enrich`), then write the sentence about what
   they built.
3. Output one row per person with the fields your sending tool merges into its template:

   `email, first_name, repo_name, what_they_built, opening_sentence, github_url`

4. A person with no sentence you can stand behind gets no row. The sending tool then cannot
   send them a generic message by accident.

The sending tool keeps the template, the schedule and the unsubscribe handling. This workflow
supplies the part that differs per person.

### Screening what is already in your tracking system

1. Export the candidates, or read them through the tracking system's connector.
2. Enrich by GitHub username (`vamo-enrich`), add tier, evidence and location.
3. Write the result back as fields on each candidate, or as a file in the system's import
   format.

The reverse works the same way: a list built in `vamo-search` leaves as the columns the tracking
system imports.

### A list from another sourcing tool

Export it, enrich it, and return the same rows with the added columns. Keep the source tool's
own identifier column untouched so the file can be matched back.

### Vamo beside other tools in one agent

An agent that also has a web search tool, a tracking-system connector and a mail tool can do a
whole task in one conversation. Keep the division clear:

| Question | Who answers |
| --- | --- |
| Who has built this kind of thing, and what is the evidence? | Vamo |
| What does the public web say about this person or company? | The web search tool |
| What is this candidate's status with us? | The tracking system |
| Did the message go out, and did they reply? | The mail tool |

When two sources disagree about a person, show both and say which field came from where.

---

## What a finished run reports

- The spec that ran: queries, filters, band.
- Counts at each step, with the reason for each drop.
- New people this run, and how many were excluded as already seen.
- Every unknown and assumption, per person.
- What was prepared and is waiting for a person to approve.

## Common mistakes

| Symptom | Cause | Fix |
| --- | --- | --- |
| The weekly run returns the same people | No seen list | Store ids and send them in `exclude` |
| Two records for one person | Joined on username | Join on `id` |
| A run stops halfway with nothing saved | One long sequential pass | Parallel groups, and write results as each group returns |
| Generic messages went out | Rows without a personal sentence were kept | Drop the row when there is no sentence |
| A field changed meaning between steps | Each step invented its own shape | One record shape, agreed first |
| The agent kept searching until it hit the target | No stopping rule | A maximum number of rounds, and report thin lanes |
