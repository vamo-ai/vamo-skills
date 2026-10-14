---
name: vamo-outreach
description: Use when writing to software engineers about a role, for one person or a whole list. Covers personalized technical outreach grounded in what the person actually built, read through Vamo, and linked to the problem the hiring team works on. Two openings per person (one leads with their work, one with the role), subject lines, a short follow-up sequence, a quality check before anything is handed over, and merge fields for a sending tool. A person approves every message; the agent never sends. Triggers "write outreach to", "draft an email to this engineer", "personalize these messages", "write a first email that shows we read their code", "draft a sequence for this list", "write a follow-up", "what should I say to this candidate".
metadata:
  version: "1.0.0"
  updated: "2026-10-14"
---

# Personalized outreach

Engineers get a lot of recruiting mail, and most of it could have been sent to anyone. A message
gets read when its first line proves the sender looked at the person's work, and gets answered
when the ask is small and clear. This skill writes that message from what Vamo shows about the
person, and links it to the problem the team is hiring for.

`vamo-enrich` fills in the person. `vamo-search` finds people to write to. A sending tool, such as
a mail client or a sequencer, sends. The workflow around it is in `vamo-workflows`.

## Rules

- **Who you write to matters more than how.** A strong message to the wrong person gets nothing.
  Write first to the people whose work is closest to the problem, and say so when a list is weak.
- **Every claim traces to something you read.** A repository, its description or README, a field
  on the profile. If you cannot point to it, it does not go in the message.
- **Name the work and say what it does.** Praise words carry nothing. "Your scheduler that keeps
  jobs running through a node failure" says more than "your impressive project".
- **Say who you are and why you are writing, early.** No mystery, no bait.
- **One ask, as a question that can be answered in a line.** "Open to a 20 minute call next
  week?" beats "let me know if you might be interested".
- **Short.** A first message stays under 100 words. Follow-ups are shorter.
- **Assume nothing about how they feel about their job.** Do not mention how long they have been
  there or guess that they are looking.
- **A person approves every message.** Prepare drafts. Never send, never schedule, never press a
  button that sends. Get an email address with `vamo-enrich` only for people who will actually be
  written to, at the moment they will be.

## What you need

| Input | Where it comes from | If it is missing |
| --- | --- | --- |
| The person | A GitHub username, a LinkedIn profile, or a row from a search | Ask for one. A name alone is not enough |
| The role | A few lines: what the team builds, the hard problem in it, stage, location or remote | Ask once: "What does the team build, and what is the hard part?" |
| The sender | Name, role, company, and anything they are willing to share, such as compensation | Leave a clear placeholder, and list it in the notes |
| The channel | Email, LinkedIn message, or another | Default to email |

## 1. Read the person

Look the person up with `vamo-enrich` at the depth that shows their work (`core` or `deep`), with
the written summaries. Then read the repository descriptions and READMEs yourself.

Pick **one piece of work** to open with. In order of preference:

1. Something they own and still work on, close to the team's problem.
2. A substantial contribution to a project the team uses or competes with.
3. Their strongest work overall, when nothing is close.

Read what the project does, how, and at what scale. Engineers recognize their own work instantly,
and a vague or wrong description reads worse than none.

If nothing they built can carry a specific sentence, they do not get a personalized message yet.
Say so, and suggest the person check again later or lead with the role instead.

## 2. Find the link

Write one sentence that links their work to the problem the team works on. The link is about the
problem, so it stays concrete:

- "We are building `<what the team builds>`, and the hard part is `<the problem>`. Your
  `<project>` deals with the same thing."

Keep it to the problem. Do not tell them they are a perfect fit or exactly what the role needs.

## 3. Write two openings

Every person gets two versions, so the sender can choose, and so the two can be compared over a
list.

**A. Lead with their work.** First line: the specific thing they built and what it does. Then who
you are and the link to the team's problem. Then the question.

**B. Lead with the role.** First line: one concrete detail that makes the role worth reading:
the problem, the team, the stage, or compensation if the sender shares it. Then who you are, why
you thought of them (their work, in one clause), and the question.

Then two subject lines for each. Specific and plain: the project, the problem or the role. No
"quick question", no all-caps, nothing that pretends to be a reply.

Pick the version to recommend: A when the work is strong and close to the problem, B when the
role is the stronger story or the work is less specific.

## 4. Follow-ups

Two at most, only if there was no reply, and each adds something new:

1. **A few days later.** One new fact: another thing they built, who they would work with, or
   what the first months look like. Same question, asked again plainly.
2. **About a week after that.** Two or three lines. Close the thread politely and leave the door
   open.

Never "just bumping this", never guilt, never a fake deadline.

## 5. Check before handing over

Rewrite any message that fails one of these:

- The first line names their actual work, or a concrete fact about the role. No "I came across
  your profile", no "I was impressed by".
- Every claim about them traces to something you read.
- The sender and the reason for writing are clear.
- One question, answerable in a line.
- Under 100 words for a first message.
- Nothing about their tenure, their feelings about their job, or whether they are looking.
- None of: "exciting opportunity", "fast-growing", "passionate", "rockstar", "ninja", "guru",
  "synergy", "leverage", "touch base", "circle back", "just checking in".
- Across a list, no two messages open with the same sentence shape.

## Output

For one person:

```
To: <name> (<github username>)
Work it opens with: <project>, <one plain sentence on what it does>
Recommended: A or B, and why in one line

Version A
Subject: <option 1> | <option 2>
<message>

Version B
Subject: <option 1> | <option 2>
<message>

Follow-up 1: <message>
Follow-up 2: <message>

Before sending: <placeholders to fill, anything you could not confirm>
```

For a list, return one row per person with the fields a sending tool merges, plus the variant
tag:

`email, first_name, subject, opening_line, link_line, body, variant, github_url, notes`

- A person with no opening line you can stand behind gets no row, so a sending tool cannot send
  them a generic message by accident. List them separately with the reason.
- Split the list between A and B and keep the `variant` column. Replies by variant tell you
  which opening works for this role. Change one thing at a time.

Examples, with invented people, are in [`references/examples.md`](references/examples.md).

## Pitch it to the sender

A recruiter usually wants ready-to-paste drafts and a short note on what to fill in. A founder or
an engineer writing to a peer can sound like themselves: offer to match a past message they liked.
Write in the sender's voice once you have seen it, and keep the rules above.
