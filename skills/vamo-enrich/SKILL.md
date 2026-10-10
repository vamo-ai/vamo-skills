---
name: vamo-enrich
description: Use when the people are already known and the job is to learn more about them with the Vamo Developer API, for example a candidate about to be interviewed, a list exported from another sourcing tool or an applicant tracking system, GitHub usernames that need location, LinkedIn, contact details or a strength read, or one developer who needs a full research report. Also use when writing a personalized message grounded in what a developer built, or a one-page summary of a candidate for a hiring team. Triggers "is this candidate strong", "enrich this list", "look up these GitHub profiles", "prep me for this interview", "write a pitch sheet", "find their email", "run deep research on", "personalize this outreach".
metadata:
  version: "1.0.1"
  updated: "2026-10-09"
---

# Vamo Enrich

Search finds people. Enrichment starts from people you already have and fills in what their
GitHub profile alone does not show: a reputation read, resolved location, linked professional
identity, contact details, a written summary, and a full research report.

`vamo-api-access` covers setup. `vamo-search` covers finding people in the first place. The API
describes itself at `https://api.vamotalent.ai/openapi.json`, and that description wins over this
file on routes, parameters and fields.

---

## Start from a GitHub username

Every lookup is by GitHub username (`login`) or by developer `id`. A list from another tool
usually has a GitHub URL column: take the username from the URL. Rows with no GitHub username
are set aside and reported, since guessing one attaches the wrong person's work to a candidate.

| Call | Use it for | Limits |
| --- | --- | --- |
| `GET /v1/developers/enrich` | The profile at the depth you ask for | 25 logins or ids per call |
| `GET /v1/developers/summaries` | A short written summary of the person and of their key repositories | 25 per call. First read can be `pending`: read again |
| `GET /v1/developers/emails` | Email addresses observed for a developer | 25 per call |
| `POST /v1/deep-research/jobs` | A full research report, saved to the account | 25 subjects per job. Poll until done |
| `POST /v1/fit-rank` | Scoring people against a role text | 50 logins per call |

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

### A personalized message grounded in their work

*"Write a first email that shows we read their code."*

1. `enrich` and `summaries` for the person. Read the repository descriptions yourself.
2. Write one sentence that names something they built and says what it is. That sentence is
   different for every person and carries the message.
3. Then the sender's own short pitch, the same for everyone.

Rules for the sentence:

- State what they built and how it works. No praise words.
- Every claim traces to a field or a URL you read.
- If you cannot write the sentence from what you read, the person does not get a message yet.
- Vary the shape across a list so no two messages open the same way.

### Enrich a list from another tool

*"Here is an export from our sourcing tool. Add location, LinkedIn and how strong they are."*

1. Read the file. Find the GitHub column, extract usernames, drop duplicates.
2. `enrich` in batches of 25 at `depth=enriched`. Run batches a few at a time.
3. Write the file back with the original columns untouched and these added:

   `vamo_id, cracked_tier, cracked_score, city, country, location_source, linkedin_url,
   current_title, current_company, has_email, top_repo, top_repo_stars, status`

4. `status` is `matched`, `not_found`, or `no_github_username`. Every input row appears in the
   output.

### Screen applicants or a pipeline

*"Which of these applicants have real engineering work behind them?"*

- Enrich the list as above, then sort by tier and by evidence: owned repositories with real
  activity come before a high number alone.
- With the role text in hand, `fit-rank` the logins for a second read. It returns fit, how
  reachable the person is, and a short reason.
- Return the full list ranked. Leave the cut line to the person asking.

To move the result into an applicant tracking system, write the columns that system imports, or
hand the rows to the tracking system's own connector if the agent has one. Vamo supplies the
read on each person. The other system stores it.

### Deep research on a set of candidates

*"Run the full report on each finalist."*

1. `POST /v1/deep-research/jobs` with up to 25 logins.
2. Poll `GET /v1/deep-research/jobs/{id}` until every subject finishes. Polling also moves the
   job forward. Some subjects can finish while others report a reason they did not.
3. Read each report at `/v1/deep-research/reports/developers/{login}`. Reports stay with the
   account, so the team can read them again later.

A research job needs the account to have deep research enabled, and it can need a linked GitHub
connection. The error body says which. `vamo-api-access` covers the error fields.

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
