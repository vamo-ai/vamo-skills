# vamo-skills

Agent skills for finding people and things.

Each skill is a single markdown file with YAML frontmatter, in the standard
`skills/<name>/SKILL.md` layout. They are plain prose — no code, no dependencies, no build
step. An agent reads one and behaves better.

## Skills

| Skill | What it's for |
|---|---|
| [`fanout-search`](skills/fanout-search/SKILL.md) | Turning one topic into 25–40 queries plus a known-item arm, then ranking the union. Corpus-agnostic: GitHub, arXiv, web, vector index, internal DB. |
| [`vamo-search`](skills/vamo-search/SKILL.md) | Using the [Vamo](https://vamotalent.ai) developer-search API without misreading a result or overspending. |
| [`role-decomposition`](skills/role-decomposition/SKILL.md) | Turning a job description and intake notes into a search spec: lanes, gates, rank signals, exclusions, each bound to an exact filter and a field to confirm. |
| [`vamo-sourcing-agent`](skills/vamo-sourcing-agent/SKILL.md) | Running a role end to end with the Vamo API: recall, qualification, the outreach angle per person. Ships with a 50-domain query library. |

`fanout-search` is the general method. `vamo-search` applies it to one specific API and adds
that API's levers, response traps, and cost model.

For a full sourcing run, use them in order. `role-decomposition` turns what the hiring team said
into a spec. `vamo-sourcing-agent` runs that spec through the funnel and writes the outreach
angle for each person. `vamo-search` is the reference for the API underneath both.

## Why these exist

Both encode failures that are silent — the kind where the output looks fine and is wrong:

- **One query is not a search.** A human query is a topic; a search engine wants a facet.
  Running the user's words verbatim and taking page one is the single biggest quality loss in
  any retrieval task.
- **Keyword search under-retrieves famous things.** When something is canonical, everyone
  else's description of it outranks the thing itself. Measured on a 863-hit GitHub sweep:
  seven load-bearing repos in the field appeared only as mentions inside other repos'
  descriptions, and zero were returned as results.
- **Ranking fields lie if you don't read their metadata.** A relevance score whose direction
  inverts by backend will hand you your worst matches as your best, and nothing in the
  response will look wrong.

## Install

**Claude Code** — copy a skill directory into either location:

```bash
# available everywhere
cp -r skills/fanout-search ~/.claude/skills/

# or scoped to one project
cp -r skills/fanout-search .claude/skills/
```

**Anything else** — the files are plain markdown. Paste the body into a system prompt, load it
as a tool description, or serve it as a doc. Each skill also ends with a self-contained
**drop-in prompt** block you can hand to a weaker model verbatim.

## Adding a skill

1. `skills/<name>/SKILL.md`, frontmatter with `name` and `description`. Heavy reference
   material goes in `skills/<name>/references/` and is linked from the skill.
2. Write the `description` for *retrieval*, not for humans: state when to use it and include
   the phrases a user would actually say. That string is how an agent decides to load it.
3. Lead with the traps. Agents need the failure modes up front; humans need the happy path up
   front. These are written for agents.
4. Assert only what you verified. Cite the spec, the route tree, or the measurement.

## Contents policy

These files are written to be publishable: no keys, no account identifiers, no corpus or
population sizes, no internal infrastructure detail. Public API surface and method only.
