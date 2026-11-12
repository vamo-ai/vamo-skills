---
name: vamo-outreach
description: Use when writing to software engineers about a role, for one person or a whole list. Starts with describing the role well in a few lines, then drafts personalized technical outreach that links one thing the person actually built, read through Vamo, to the work the team is hiring for. Covers the role pitch, choosing the right repository, the first message, subject lines, follow-ups, answering a reply, a check before anything is handed over, and merge fields for a sending tool. A person approves every message, and the agent never sends. Triggers "write outreach to", "draft an email to this engineer", "personalize these messages", "write a first email that shows we read their code", "help me pitch this role", "draft a sequence for this list", "write a follow-up", "they replied, what do I say".
metadata:
  version: "1.1.0"
  updated: "2026-11-12"
---

# Personalized outreach

This skill drafts first messages, follow-ups and replies to engineers about a role. Each first
message links one thing the person built to the work the team is hiring for. The sender keeps
control of the role pitch, the ask and the signature. The agent writes the part that changes per
person, and a person approves every message before it is sent.

`vamo-enrich` fills in the person. `vamo-search` finds people to write to. `vamo-workflows` covers
putting drafts into a mail tool or a sequencer.

## 1. Describe the role first

Write the role down once, before any message. Every message reuses it, so a few minutes here
makes the whole list better. Ask the sender for what is missing, in one message:

| Part | What good looks like |
| --- | --- |
| **One-line pitch** | "We're building `<what the product does>` for `<who uses it>`." Under 150 characters. What the company makes, in plain words |
| **The work** | One or two sentences on what this person would build, and the hard part of it |
| **Three reasons to care** | Taken from the job description or the sender, never invented. Stage, team, a hard problem, ownership, compensation if the sender shares it |
| **Facts** | Title, seniority, location or remote, and the main languages or systems |
| **The ask** | A 15 to 20 minute call, a reply, or a short chat with the hiring manager |
| **The sender** | Name, role, company, and a link the candidate can check |

If the sender pastes a job description, draft these parts from it and ask them to confirm or
correct. Keep the pitch plain: what the company does and who it is for, with no adjectives about
the company itself.

Use the facts to keep each message accurate. Do not list them back in the message.

## 2. Choose who to write to first

Start with the people whose work is closest to the role. A message to someone whose work does not
fit gets no reply however it is worded. Put these people later in the list, or leave them out:

- The role would be a step down, or a different job from the one they do now.
- They founded or run a company that is still active.
- Their current employer comes from an old profile. Mark it as inferred, and leave the employer
  out of the message.

Say so when a list is thin, rather than writing to weaker matches to fill it.

## 3. Read the person and pick one repository

Look the person up with `vamo-enrich` (`core` or `deep`, with summaries), or the Vamo MCP `enrich`
tool. Read the repository descriptions and READMEs yourself.

Pick the **one repository that best shows they can do this role's work.** A famous repository
that has nothing to do with the role is the wrong choice. Then check:

- **Built or contributed.** Say "built" or "wrote" only for a repository they own. For anything
  else, say "contributes to" or "worked on".
- **What it does.** Describe it from its description and README, in one plain clause. Do not add
  technical details that are not there.
- **No good repository.** If nothing they built relates to the role, do not pretend. Write the
  message from the role side, or leave the person out and say why.

## 4. Write the first message

These rules come from the prompts Vamo's sequence product used to write thousands of first
messages that read like a person wrote them. The full prompts, with placeholders, are in
[`references/system-prompt.md`](references/system-prompt.md). Follow them closely.

**Tone.** Conversational and direct: "I checked out", "I noticed", "I saw". Short, punchy
sentences. No formal phrases like "aligns perfectly" or "significantly accelerate", no
exclamation marks, no selling.

**The line about their work (the opener).** One or two sentences, usually one:

- They own it: "I checked out your `<repository>` project (`<link>`) and was impressed by
  `<detail>`."
- They contributed: "I checked out your work on `<repository>` (`<link>`) and was impressed by
  `<detail>`."
- No description to go on: "I checked out your `<repository>` project (`<link>`) and was
  impressed by your work."
- No repository worth naming: "I came across your GitHub and was impressed by your work on
  `<topic from the role>`." Never say you checked out a project you did not name.

`<detail>` is under 12 words and comes only from the description or README. The link is the
repository's own URL, under its real owner, right after the name. Never "I checked out your
GitHub profile". Never include or invent a link to the person's LinkedIn.

Keep their work to that line. Long, clever lines about someone's repository are what make outreach
read as written by AI. Do not add another sentence about it, explain why it matters, describe who
else uses it, or reach for a metaphor.

**If the sender has a template**, it holds the greeting, pitch, ask and signature, with an
`{opener}` slot. Write only the opener, put it in the slot, fill the name and repository fields,
and change nothing else. A template with no `{opener}` slot is sent as written.

**If there is no template**, write the whole message in three or four short paragraphs, under
120 words:

1. "Hi `<first name>`," on its own line and a blank line, then the opener.
2. "My name is `<sender>`, and I'm `<working on X, or hiring for Y>`." Add the sender's link if
   there is one.
3. One sentence that connects them to the role: "Your experience with `<skill>` could be a great
   fit for `<the team or what it builds>`."
4. The ask: "Would you be open to a quick chat? Let me know if you have time this week."

Then the sender's signature.

**Subject lines.** "Your project `<repository>` caught my eye", or the sender's own format when
they have one. Offer a second option that names the repository or the role.

## 5. Follow-ups

Only the first message is personalized. Follow-ups are short:

1. **A few days later.** Two or three sentences. Add one new thing: who they would work with,
   what the first months look like, or another piece of their work. Ask the same question again.
2. **About a week after that.** Two sentences that give an easy out, and say you will not write
   again.

Do not write "just bumping this" or set a deadline that is not real.

## 6. When they reply

Answer what they actually said first. Two to four sentences, in their tone. If they asked a
question, answer it, or say who can. If they said no, thank them and stop. Take the sender's
instructions as a guide for the reply, not as words to copy.

## 7. Check before handing over

Rewrite a message that fails any of these:

- The opener names their actual work in the shape from section 4, or the person was left out.
  Their work is not described anywhere else in the message.
- Every claim about them comes from something you read. "Built" only for repositories they own.
- One question, answerable in a line.
- Under 120 words for a whole first message. With a template, only the opener changed.
- Nothing about their tenure, how they feel about their job, or whether they are looking.
- No em dashes, and no "not X, it's Y" sentences.
- None of: "passionate", "perfect fit", "aligns
  perfectly", "reach out", "I hope this finds you well", "excited to connect", "exciting
  opportunity", "showcases", "deep expertise", "rockstar", "just checking in", "the kind of".

## Output

For one person:

```
To: <name> (<github username>)
Repository: <owner/name>, <one plain clause on what it does>, built or contributed

Subject: <option 1> | <option 2>
<message>

Follow-up 1: <message>
Follow-up 2: <message>

Before sending: <placeholders to fill, anything you could not confirm>
```

For a list, one row per person with the fields a sending tool merges:

`email, first_name, subject, opening, body, repo, github_url, notes`

- A person with no repository you can stand behind gets no row, so a sending tool cannot send them
  a generic message by mistake. List them separately with the reason.
- Get email addresses with `vamo-enrich` only for the people who will be written to.

Worked examples, with invented people, are in [`references/examples.md`](references/examples.md).
