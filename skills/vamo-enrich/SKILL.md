---
name: vamo-enrich
description: Use when the people are already known and the job is to learn more about them with Vamo. They can come from anywhere. Candidates in an applicant tracking system such as Ashby, Greenhouse or Lever, LinkedIn profiles, applicants from a job post, a spreadsheet, a list exported from another sourcing tool, or one person about to be interviewed. Covers matching each row to a developer, a strength read, resolved location, LinkedIn, current role, contact details, written summaries, screening applicants for real engineering work, a one-page summary for a hiring team, and a full research report. Triggers "is this candidate strong", "enrich this list", "enrich our Ashby candidates", "look up these LinkedIn profiles", "screen these applicants", "prep me for this interview", "write a pitch sheet", "find their email", "run deep research on".
metadata:
  version: "1.3.0"
  updated: "2026-10-14"
---

# Vamo Enrich

Search finds people. Enrichment starts from people you already have, wherever they came from,
and fills in what a résumé or a profile alone does not show: what they built, a reputation read,
resolved location, linked professional identity, contact details, a written summary, and a full
research report.

`vamo-setup` covers setup. `vamo-search` covers finding people in the first place.
`vamo-outreach` writes to them. The API
describes itself at `https://api.vamotalent.ai/openapi.json`, and that description wins over this
file on routes, parameters and fields.

---

## Where your people come from

| Source | How to get them | What to match on |
| --- | --- | --- |
| An applicant tracking system (Ashby, Greenhouse, Lever and others) | The system's connector, if your agent has one, or a CSV export of a job's candidates | The GitHub and LinkedIn links on the candidate. Keep the system's candidate id on every row |
| LinkedIn profiles | A list of profile URLs, or a search export | The profile URL itself |
| Applicants from a job post or a form | The form's export, or the résumés | GitHub and LinkedIn links in the answers or in the résumé text |
| A spreadsheet or another sourcing tool | The file | Its GitHub or LinkedIn column |
| One person | A name with a link, from the conversation | Ask for a GitHub or LinkedIn link if only a name was given |

Read the source through its own connector when the agent has one: it saves an export, and the
results can go back the same way (see `vamo-workflows`). Never guess a GitHub username from a
name or an email address. A guess attaches someone else's work to a candidate.

## Start from a GitHub username or a LinkedIn profile

Every lookup is by GitHub username (`login`), LinkedIn profile, or developer `id`. A list from
another tool usually has a GitHub URL column: take the username from the URL. A row with only a
LinkedIn URL can be looked up by that URL. Rows with neither are set aside and reported, since
guessing one attaches the wrong person's work to a candidate.

| Call | Use it for | Limits |
| --- | --- | --- |
| `POST /v2/developers` with `{"logins": [...], "linkedin": [...], "ids": [...], "depth": "enriched"}` | The profile at the depth you ask for, by any mix of identifiers. Results come back in the order sent | 25 inputs per call |
| `GET /v2/developers/enrich?logins=a,b&depth=enriched` (or `ids=`) | The same by query string, for logins or ids | 25 per call |
| `GET /v2/developers/summaries` | A short written summary of the person and of their key repositories | 25 per call. First read can be `pending`: read again |
| `GET /v2/developers/emails` | Email addresses observed for a developer | 25 per call |
| `POST /v2/developers/similar` with `{"like_person": "<login>", "intent": "same"}` | More people like one you hold | Up to 100 per page |
| `POST /v2/deep-research/jobs` | A full research report, saved to the account | 25 subjects per job. Poll until done |

With the Vamo MCP tools, `enrich` takes the same identifiers and depth as `POST /v2/developers`,
and `deep_research` starts, checks and reads reports. Summaries and email addresses are API
calls.

## What each depth adds

| Depth | You get | Read it at |
| --- | --- | --- |
| `core` | Profile, top repositories with descriptions and languages, cracked score and tier | `details.githubProfile`, `details.score.cracked` |
| `enriched` | Linked professional identity, employment and education history, social links, resolved location | `details.identity`, `details.contact` |
| `deep` | A year of contribution activity as a compact summary | `details.github.gardenSummary` |

Ask for the depth the task needs. A strength check needs `core`. A location or employer needs
`enriched`. A read on whether someone is building right now needs `deep`.

Reading rules that prevent wrong claims:

- **An absent field is unknown.** No location, no education, no linked profile: say unknown.
  Never turn silence into "none".
- **A linked profile can belong to someone else with the same name.** Compare the name on the
  row with the name and headline on the linked profile before using its title, employer or
  location.
- **Location has three parts.** Read `city`, `country` and `raw` together. The resolved country
  can be empty while the others name the place.
- **Education lists can start with a secondary school.** Read every entry.
- **The cracked score is a standing among builders.** Present the tier (Elite, Expert,
  Advanced). A raw number means little to a hiring team.

---

## Recipes

### Before an interview: is this person strong?

*"I'm interviewing this candidate tomorrow. What should I know from their GitHub?"*

1. `enrich` at `depth=deep`, with the summary facets.
2. Read: tier, the three or four repositories they own with real activity, what each one does,
   how steady the last year has been, and current role.
3. Hand back half a page:
   - one line on standing
   - two or three things they built, each in a plain sentence a non-specialist can follow
   - what the work suggests asking about in the interview
   - what is unknown

Describe the work. Leave the hiring decision to the person asking.

### A one-page summary of a candidate for a hiring team

*"Write a pitch sheet for this developer."*

1. Start a deep-research job for the login, poll it, and read the report.
2. Lead with the two or three strongest placements the report gives, and the repositories that
   back them. Several related strengths together are a pattern worth naming.
3. One page: who they are, what they built, the proof, links.

A strength the report could not grade is unestablished. Leave it out and say so if asked.

### Contact details

*"Find another way to reach this developer."*

- Every profile carries `hasEmail`, so you know before asking whether there is an address.
- `emails` returns every address observed. Prefer an address at the current employer's domain
  for work topics and a personal address otherwise.
- `details.contact.socials` and the linked profile at `depth=enriched` give other routes.
- Get addresses for the people who will actually be contacted, at the moment of contact.

### A message grounded in their work

*"Write a first email that shows we read their code."*

Use the `vamo-outreach` skill. It reads the person with the calls above, links their work to the
role, and drafts the message for a person to approve.

### Enrich a list from another tool or an applicant tracking system

*"Here are this job's candidates from Ashby. Add location, LinkedIn and how strong they are."*

1. Read the file. Find the GitHub column, extract usernames, drop duplicates. For rows with no
   GitHub column, take the LinkedIn URL.
2. Look up in batches of 25 at `depth=enriched` with `POST /v2/developers`, sending `logins` and
   `linkedin` together. Run batches a few at a time.
3. Write the file back with the original columns untouched and these added:

   `vamo_id, cracked_tier, cracked_score, city, country, location_source, linkedin_url,
   current_title, current_company, has_email, top_repo, top_repo_stars, status`

4. `status` is `matched`, `not_found`, or `no_github_username` (a row with neither a GitHub
   username nor a LinkedIn URL). Every input row appears in the output.

### Screen applicants or a pipeline

*"Which of these applicants have real development work behind them?"*

- Enrich the list as above, then sort by tier and by evidence: owned repositories with real
  activity come before a high number alone.
- With the role text in hand, read each person's strongest work against what the role needs,
  and say in one line why they rank where they do.
- Return the full list ranked. Leave the cut line to the person asking.

To move the result into an applicant tracking system, write the columns that system imports, or
hand the rows to the tracking system's own connector if the agent has one. Vamo supplies the
read on each person. The other system stores it.

### Deep research on a set of candidates

*"Run the full report on each finalist."*

1. `POST /v2/deep-research/jobs` with up to 25 logins.
2. Poll `GET /v2/deep-research/jobs/{id}` until every subject finishes. Polling also moves the
   job forward. Some subjects can finish while others report a reason they did not.
3. Read each report at `/v2/deep-research/reports/developers/{login}`. Reports stay with the
   account, so the team can read them again later.

A research job needs the account to have deep research enabled, and it can need a linked GitHub
connection. The error body says which. `vamo-troubleshooting` covers the error fields.

---

## Common mistakes

| Symptom | Cause | Fix |
| --- | --- | --- |
| A candidate shows someone else's employer | A linked profile for a different person with the same name | Compare names before trusting linked fields |
| "No location" for someone in a known city | Only `country` was read | Read `city` and `raw` |
| The summary field is empty | It was still `pending` | Read the same request again |
| Rows vanish from an enriched file | Unmatched rows were dropped | Keep every row and set `status` |
| A message praises the wrong project | The repository name was read, the description was not | Read the description and README text |
| Research job returns partial results | Some subjects could not be researched | Report which, with the reason given |
