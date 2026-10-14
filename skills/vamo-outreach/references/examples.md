# Outreach examples

Reference for the `vamo-outreach` skill. The people, projects, companies and roles here are
invented. Each example shows what was read, the link, and the two versions.

## 1. A strong match, work leads

**Role.** A seed-stage team building a real-time voice assistant for clinics. The hard part is
holding latency under 300 ms while people interrupt each other.

**What was read.** `<login>` owns `<project>`, a streaming speech pipeline with interruption
handling, active in the last month. The README describes a buffer that drops stale audio when the
speaker changes.

**Link.** Interruptions are the hard part of the team's product, and the project solves that.

Version A

> Subject: interruption handling in `<project>`
>
> Hi `<first name>`, `<project>` drops stale audio the moment the speaker changes. That is the
> problem we hit every day. I'm `<sender>`, hiring at `<company>`: we build a voice assistant for
> clinics, and keeping replies under 300 ms while people talk over each other is our hardest
> problem. Open to a 20 minute call next week to compare notes?

Version B

> Subject: voice latency at `<company>`
>
> Hi `<first name>`, we are a seed-stage team building a voice assistant for clinics, and our
> hardest problem is holding latency under 300 ms through interruptions. I'm `<sender>`, and I
> thought of you because of the buffering in `<project>`. Would you be up for a short call next
> week?

Recommended: A. The work is close to the problem and specific enough to lead.

## 2. The work is good but not close, role leads

**Role.** Infrastructure for a payments company: moving a ledger to a new database with no
downtime.

**What was read.** `<login>` maintains `<project>`, a schema migration tool for a popular
database, with steady activity over two years.

**Link.** Migrations without downtime are the role's main job.

Version B is recommended here: the role is the stronger story, and the tool explains why you
thought of them in one clause.

> Subject: a zero-downtime ledger migration
>
> Hi `<first name>`, we are moving a payments ledger to a new database this year without taking
> it offline. I'm `<sender>` at `<company>`, and I'm writing because you maintain `<project>`, so
> you have thought about this problem more than most. Would you take a 20 minute call to hear the
> plan?

## 3. Not enough to personalize

**What was read.** `<login>` has a strong standing but every owned repository is a fork or a
course exercise, and the summaries name no specific work.

**Output.** No row. Note: "No specific work to open with. Check again in a month, or write with
version B and leave out the line about their work."

## Follow-ups for example 1

Follow-up 1, four days later:

> `<first name>`, one more detail: you would work directly with `<name>`, who built our current
> audio stack and is stuck on the same interruption problem. Still open to a short call?

Follow-up 2, a week after that:

> I'll leave it here. If voice latency is ever something you want to work on full time, my inbox
> is open.
