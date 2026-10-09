# vamo-skills

Agent skills for finding people and things. The Vamo skills are written for an agent that calls
the [Vamo](https://vamotalent.ai) Developer API directly: a key, an HTTP client and these files
are everything it needs.

Each skill is a single markdown file with YAML frontmatter, in the standard
`skills/<name>/SKILL.md` layout. They are plain prose, no code, no dependencies, no build
step. An agent reads one and behaves better.

## Skills

| Skill | Version | What it's for |
|---|---|---|
| [`vamo-api-access`](skills/vamo-api-access/SKILL.md) | 1.1.0 | **Start here.** Access to the Vamo Developer API from any agent: getting it, storing it so it persists, opening the network path, verifying, reading errors. Includes a curl walkthrough of every route and per-platform notes. |
| [`fanout-search`](skills/fanout-search/SKILL.md) | 1.0.1 | Turning one topic into 25–40 queries plus a known-item arm, then ranking the union. Corpus-agnostic: GitHub, arXiv, web, vector index, internal DB. |
| [`vamo-search`](skills/vamo-search/SKILL.md) | 1.1.1 | Choosing the right endpoint and filter, and reading what comes back: the two filter families, short pages, unknowns. |
| [`role-decomposition`](skills/role-decomposition/SKILL.md) | 1.2.1 | Turning a job description and intake notes into a search spec: lanes, gates, rank signals, exclusions, each bound to an exact filter and a field to confirm. |
| [`vamo-sourcing-agent`](skills/vamo-sourcing-agent/SKILL.md) | 1.1.1 | Running a role end to end with the Vamo API: recall, qualification, the outreach angle per person. Ships with a 50-domain query library. |

`fanout-search` is the general method. `vamo-search` applies it to one specific API and adds
that API's levers and response traps.

For a full sourcing run, use them in order. `vamo-api-access` gets the connection working.
`role-decomposition` turns what the hiring team said into a spec. `vamo-sourcing-agent` runs that
spec through the funnel and writes the outreach angle for each person. `vamo-search` is the
reference for reading results underneath both.

### The spec is the source of truth

The API describes itself at `https://api.vamotalent.ai/openapi.json`, generated from the running
service. These skills teach method: what to try, in what order, and how to check the answer. They
point at the spec for routes, parameters and fields, and where a skill and the spec disagree, the
spec wins. When a skill has to explain something the spec should have said, the fix belongs in
the spec, and the skill gets shorter.

## Why these exist

Both encode failures that are silent, the kind where the output looks fine and is wrong:

- **One query is not a search.** A human query is a topic; a search engine wants a facet.
  Running the user's words verbatim and taking page one is the single biggest quality loss in
  any retrieval task.
- **Keyword search under-retrieves famous things.** When something is canonical, everyone
  else's description of it outranks the thing itself. Measured on a 863-hit GitHub sweep:
  seven load-bearing repos in the field appeared only as mentions inside other repos'
  descriptions, and zero were returned as results.
- **A filter you sent is a different claim from a field you confirmed.** Some filters leave
  people in when the data is silent, and some reach only part of the population. A list built
  on filters alone looks complete and carries people who fail the requirement.
- **A brief is several kinds of statement.** Work, hard requirements, preferences and exclusions
  each need a different mechanism. Put them all in one query and most of them do nothing.

## Install

The skills are plain markdown in the standard `skills/<name>/SKILL.md` layout, so they work in
any agent that reads skills, and in any agent that can read a file and follow it. Pick the row
that matches your agent. Start with `vamo-api-access` in every case: it stores your API access
and opens the network path.

| Your agent | Install | Use |
| --- | --- | --- |
| Claude Code | `/plugin install vamo --marketplace vamo-ai/vamo-skills` | `/vamo:vamo-api-access`, `/vamo:role-decomposition`, and so on |
| Claude on the web or desktop | **Customize**, **Plugins**, **Add**, **Add marketplace**, enter `vamo-ai/vamo-skills`, then install **vamo** | Type `/` and pick `vamo:<skill>` |
| Any agent with a skills directory | Copy the folders under `skills/` into that directory | By name, or let the agent pick from the description |
| Any agent at all | Tell it: *"Read https://raw.githubusercontent.com/vamo-ai/vamo-skills/main/skills/vamo-api-access/SKILL.md and follow it"* | One skill per message |

Older Claude Code versions use two steps: `/plugin marketplace add vamo-ai/vamo-skills`, then
`/plugin install vamo@vamo-skills`.

To upload single skills instead of the plugin, each [release](https://github.com/vamo-ai/vamo-skills/releases)
carries one zip per skill.

**Your API key is never part of these files.** `vamo-api-access` explains where it goes.

Each skill also ends with a self-contained **drop-in prompt** block where one applies, for
handing to a smaller model verbatim.

## Staying current

Skills change as the API does. Each one carries `metadata.version` and `metadata.updated` in its
header. [`skills.json`](skills.json) lists the current version of every skill, and
[`CHANGELOG.md`](CHANGELOG.md) says what changed.

**When to check**

- Once a week while you are using the skills regularly.
- Before setting up a new person or a new machine.
- When the API rejects a parameter or a field that a skill mentions.
- When a skill and `openapi.json` disagree.

**How to check**

```bash
curl -s https://raw.githubusercontent.com/vamo-ai/vamo-skills/main/skills.json \
  | jq -r '.skills | to_entries[] | "\(.key) \(.value.version) (\(.value.updated))"'
```

Compare each line with the version in the header of the copy you have installed. An agent can
run this check itself at the start of a session and tell you which skills are behind.

**How to update.** A plugin install updates from the marketplace: in Claude Code run
`/plugin marketplace update vamo-skills`, and on the web and desktop apps the marketplace syncs
from this repository. For copied folders or uploaded zips, replace the skill with the new one. A private `vamo-access` skill is separate and stays as it is.

**What the numbers mean.** A new minor version changes what an agent should do. A patch version
is a wording fix. A major version means the earlier behavior is now wrong.

## Adding a skill

1. `skills/<name>/SKILL.md`, frontmatter with `name`, `description` and `metadata` holding
   `version` and `updated`. Add the skill to `skills.json` and `CHANGELOG.md`. Heavy reference
   material goes in `skills/<name>/references/` and is linked from the skill.
2. Write the `description` for *retrieval*, not for humans: state when to use it and include
   the phrases a user would actually say. That string is how an agent decides to load it.
3. Lead with the traps. Agents need the failure modes up front; humans need the happy path up
   front. These are written for agents.
4. Assert only what you verified. Cite the spec, the route tree, or the measurement.
5. Teach method and point at the spec for routes and parameters. If the spec is missing
   something an agent needs, open a change against the spec as well.
6. On every change, raise the version in the header and in `skills.json`, add a changelog
   line, and run `bash scripts/package.sh` to build the zips for the release. `skills.json` also carries each
   skill's display `title`, `category` and `files`; the packaging script fails if `files` and
   the folder disagree.

## Contents policy

These files are written to be publishable: no keys, no account identifiers, no corpus or
population sizes, no prices, no customer names, no internal infrastructure detail. Public API
surface and method only. Examples name no real company, school, person or repository: those
values are angle-bracket placeholders. Technology names appear only as search vocabulary.
