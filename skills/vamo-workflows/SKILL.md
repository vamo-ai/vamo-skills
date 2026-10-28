---
name: vamo-workflows
description: Use when Vamo works together with other tools, or when work should run more than once. Covers the tools an agent can reach through connectors and MCP servers (Slack, applicant tracking systems such as Ashby, Greenhouse or Lever, Gmail or Outlook, Google Sheets and Calendar, HubSpot), with links to each tool's official setup docs, which tool owns which part of a task, patterns for the common hand-offs, example systems to build (a weekly talent digest, an applicant screen, sourced-to-drafted outreach, interview prep, a talent map, a pipeline refresh), where a scheduled agent can run, and the rules that keep a repeated run correct. Triggers "post new matches to Slack", "sync with our ATS", "write this back to Ashby", "put drafts in my Gmail", "run this every week", "send results to a Google Sheet", "build a sourcing agent", "what could we automate with Vamo".
metadata:
  version: "1.2.1"
  updated: "2026-10-28"
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
`POST /v2/developers`, or to the Vamo MCP `search` and `enrich` tools with the same bodies.

---

## Who owns what

| Question | Who answers |
| --- | --- |
| Who has built this kind of thing, and what is the evidence? | Vamo |
| Where does this candidate stand with us? | The applicant tracking system (Ashby, Greenhouse, Lever). For Ashby, follow `vamo-ashby` |
| What did the team say about them? | Slack |
| Did the message go out, and did they reply? | The mail tool (Gmail, Outlook) or the sequencer |
| Where does the list live for people who do not use the agent? | A spreadsheet |
| When are we talking to them? | The calendar |

Read from each tool through its connector when the agent has one, and write back the same way.
[`references/integrations.md`](references/integrations.md) has the official connector, MCP server
and API page for Slack, Ashby, Greenhouse, Lever, Gmail, Outlook, Google Sheets, Google Calendar
and HubSpot, and the options for running on a schedule.
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

### New matches posted to the team's chat

*"Every Monday, post the new people for this role to our hiring channel."*

1. Run the stored search with the seen list (see the weekly pattern below).
2. Post one short message to the channel the person named: the role, how many are new, and up to
   five people, each with one line on what they built and a link. Put the rest in a thread or a
   sheet.
3. Ask the team to react or reply on the people worth contacting. On the next run, read those
   reactions and replies, and add everyone to the seen list.

Post only where the person told you to. Never message a candidate from the team's chat.

### Applicants screened and written back to the tracking system

*"Screen this week's applicants for the backend role."*

1. Read the job's new candidates through the tracking system's connector, or from an export.
2. Look each one up with `vamo-enrich`, by the GitHub or LinkedIn link on the candidate.
3. Write back what the system allows, such as a note or a tag: standing, the work that shows it,
   location, and anything unknown. Keep the system's candidate id on every row.
4. Leave stage changes and rejections to a person. Report who was screened and who could not be
   matched.

The reverse works the same way: people found with `vamo-search` go into the system as new
candidates, through the connector or as the columns its import takes.

### Drafts left in the mail tool for approval

*"Draft outreach for these ten people in my inbox."*

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
3. Deliver only the new people, to the team's chat, a sheet or the tracking system, and add them
   to the seen list.

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

## Systems you can build

Each of these is the patterns above joined together. Describe them to the person as options, then
build the one they pick. The links for each tool are in
[`references/integrations.md`](references/integrations.md).

| System | Starts when | Tools | What the team gets | Where a person decides |
| --- | --- | --- | --- | --- |
| **Weekly talent digest** | A schedule, once a week | Vamo, the team's chat, a sheet | New people for each open role, with one line each and a link, and the rest in a sheet | They react to the people worth contacting |
| **Applicant screen** | New applicants arrive in the tracking system | The tracking system, Vamo | A note on each applicant with their standing and the work behind it | A recruiter moves stages and rejects |
| **Sourced to drafted** | A recruiter approves people in the digest | Vamo, the mail tool | One draft per approved person, in the recruiter's drafts folder | The recruiter edits and sends |
| **Interview prep** | An interview is booked on the calendar | The calendar, Vamo, the team's chat | Half a page on the candidate's work, posted before the interview | The interviewer reads it |
| **Talent map for a new role** | A hiring manager asks where to hire | Vamo, a sheet | A comparison of the same search across a few cities, with example people from each | The hiring manager picks where to open the role |
| **Pipeline refresh** | Monthly | The tracking system, Vamo | Past candidates whose recent work grew stronger, flagged for a second look | A recruiter decides who to contact again |

When a system runs without a person in the loop, it runs somewhere: a Claude Code routine, a
scheduled GitHub Action, an agent built with the Agent SDK, or a flow in n8n, Zapier or Make. The
same rules hold wherever it runs, and every message and stage change still waits for a person.

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
| A post landed in the wrong channel | The workflow picked a channel itself | Post only where the person named |
| Generic messages went out | Rows without a personal sentence were kept | `vamo-outreach` drops a row with no sentence it can stand behind |
| A field changed meaning between steps | Each step invented its own shape | One record shape, agreed first |
| The same candidate was added twice to the tracking system | Matched on name or email | Match on the system's candidate id, and on the Vamo `id` |
| A message went out without approval | A send was wired into the run | Drafts only. A person sends |
| The agent kept searching until it hit the target | No stopping rule | A maximum number of rounds, and report thin lanes |
