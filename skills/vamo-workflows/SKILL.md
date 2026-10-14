---
name: vamo-workflows
description: Use when Vamo works together with other tools, or when work should run more than once. Covers the tools an agent can reach through its own connectors (Slack, an applicant tracking system such as Ashby, Greenhouse or Lever, Gmail or Outlook, Google Sheets, a calendar, a CRM), which tool owns which part of a task, patterns for the common hand-offs (new matches posted to Slack, applicants screened and written back to the tracking system, drafts left in Gmail for approval, a search that runs every week into a sheet), the record that moves between steps, and the rules that keep a repeated run correct. Triggers "post new matches to Slack", "sync with our ATS", "write this back to Ashby", "put drafts in my Gmail", "run this every week", "send results to a Google Sheet", "build a sourcing agent", "connect Vamo to our workflow".
metadata:
  version: "1.2.0"
  updated: "2026-10-14"
---

# Vamo Workflows

Vamo answers one question: who has built this kind of thing, and what is the evidence. Everything
around it lives in other tools: the conversation in Slack, the candidates in a tracking system,
the mail in Gmail, the list in a sheet. Most AI tools can reach those through connectors (built-in
integrations or MCP servers the person adds). This skill covers how to coordinate them, the
hand-offs that come up most, and the rules that keep a repeated run correct. `vamo-setup` covers setup,
`vamo-search` finds people, `vamo-enrich` fills in people you hold, and `vamo-outreach` writes to
them. The API's own description at
`https://api.vamotalent.ai/openapi.json`, and the live field list at `GET /v2/developers/fields`,
win over this file on routes and fields.

Searches go to `POST /v2/developers/search` as one JSON body, and lookups to
`POST /v2/developers`. On the production host those routes can answer `404` or `503` until the v2
engine is switched on there. A workflow then runs the v1 route of the same name, and the run report
says in one line that it ran on v1.

---

## Who owns what

| Question | Who answers |
| --- | --- |
| Who has built this kind of thing, and what is the evidence? | Vamo |
| Where does this candidate stand with us? | The applicant tracking system (Ashby, Greenhouse, Lever) |
| What did the team say about them? | Slack |
| Did the message go out, and did they reply? | The mail tool (Gmail, Outlook) or the sequencer |
| Where does the list live for people who do not use the agent? | A spreadsheet |
| When are we talking to them? | The calendar |

Read from each tool through its connector when the agent has one, and write back the same way.
When two tools disagree about a person, show both and say which field came from where. When a
connector is missing, say which one would help and fall back to a file the person can import.

Each tool keeps its own job. Vamo does not store candidates or send mail, and the tracking system
does not decide who is strong.

---

## Rules for anything that runs twice

- **The developer `id` is the key.** It is stable across renames. Store it with every record and
  join on it. Usernames change.
- **Keep a seen list.** Store the ids already returned, contacted or rejected, and send them in
  `exclude` (up to 1000 per search). A second run should return new people.
- **Save the spec, not the results.** Keep the search bodies that produced a list, exactly as
  sent. The list goes stale. The bodies can be run again.
- **Validate before you schedule.** Send each stored body to `POST /v2/developers/search/validate`
  when you save it and before each run. A field can be renamed or disabled between runs, and the
  `hint` says what to change.
- **Batch and pace.** Lookups take up to 25 people per call. Search allows 10 requests per second
  per key, so run searches in parallel groups of about eight. A `429` carries `Retry-After`.
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
  "devrank": null,
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

### New matches posted to Slack

*"Every Monday, post new people for this role to #hiring-backend."*

1. Run the stored search with the seen list (see the weekly pattern below).
2. Post one short message: the role, how many are new, and up to five people, each with one line
   on what they built and a link. Put the rest in a thread or a sheet.
3. Ask the channel to react or reply on the people worth contacting, and read the replies on the
   next run to update the seen list.

Post to a channel the person named. Never message a candidate from Slack.

### Applicants screened and written back to the tracking system

*"Screen this week's applicants for the backend role in Ashby."*

1. Read the job's new candidates through the connector, or from an export.
2. Look each one up with `vamo-enrich`, by the GitHub or LinkedIn link on the candidate.
3. Write back what the system allows, such as a note or a tag: standing, the work that shows it,
   location, and anything unknown. Keep the system's candidate id on every row.
4. Leave stage changes and rejections to a person. Report who was screened and who could not be
   matched.

The reverse works the same way: people found with `vamo-search` go into the system as new
candidates, through the connector or as the columns its import takes.

### Drafts left in Gmail for approval

*"Draft outreach for these ten people in my Gmail."*

1. Write each message with `vamo-outreach`.
2. Create drafts through the mail connector, one per person, addressed and ready. Never send.
3. Tell the person where the drafts are, and which version each one uses.

For a sequencer, hand over the merge fields `vamo-outreach` returns instead. The sequencer keeps
the template, the schedule and the unsubscribe handling.

### A search that runs every week

1. Store the spec and the seen list.
2. Each run: the same stored bodies, with `exclude` carrying the seen list. To favor people
   active since the last run, add `"sort": "recent"`, or the filter
   `["last_active_at", "Gte", "<last run date>T00:00:00Z"]`. Activity is partial data, so the
   filter leaves out people with no activity on file. Prefer the sort unless recency is a gate.
3. Deliver only the new people, to Slack, a sheet or the tracking system, and add them to the
   seen list.

When a run comes back empty, say so. A quiet week is information.

### Your own sourcing agent

The loop, with the skill that covers each step:

1. **Decompose** the role into a spec (`vamo-search`, `references/role-decomposition.md`).
2. **Probe** each lane with one page and grade it.
3. **Run** the lanes that graded well, paging with the seen list (`vamo-search`).
4. **Fill in** the people you would keep (`vamo-enrich`).
5. **Qualify** on evidence you read, and rank.
6. **Hand over** records in the shape above, to the tool the team works in, with what ran and what
   is unknown. Draft messages with `vamo-outreach` if asked.

Give the agent a stopping rule before it starts: a target count, a maximum number of rounds, and
the instruction to report a thin lane instead of lowering the bar to fill a quota.

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
| A stored search starts failing with a 400 | A field it names was renamed or disabled | Validate stored bodies before each run and apply the `hint` |
| Two records for one person | Joined on username | Join on `id` |
| A run stops halfway with nothing saved | One long sequential pass | Parallel groups, and write results as each group returns |
| Generic messages went out | Rows without a personal sentence were kept | `vamo-outreach` drops a row with no sentence it can stand behind |
| A field changed meaning between steps | Each step invented its own shape | One record shape, agreed first |
| The same candidate was added twice to the tracking system | Matched on name or email | Match on the system's candidate id, and on the Vamo `id` |
| A message went out without approval | A send was wired into the run | Drafts only. A person sends |
| The agent kept searching until it hit the target | No stopping rule | A maximum number of rounds, and report thin lanes |
