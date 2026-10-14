# Connecting the other tools

Reference for the `vamo-workflows` skill: where each tool's official connector or API is
documented, and the one thing to know about signing in. Every link was checked on 2026-10-14.
Vendors move these pages often. If a link has moved, search the vendor's developer site for "MCP"
or "API".

Prefer, in order: a connector the person's AI tool already offers, the vendor's own MCP server,
then the vendor's API. Each step down needs more setup from the person.

## Chat: Slack

| What | Where |
| --- | --- |
| Slack's own MCP server (search, send, draft, threads, reactions) | https://docs.slack.dev/ai/slack-mcp-server/ |
| Claude's Slack connector (search; Team and Enterprise) | https://claude.com/docs/connectors/slack |
| Post a message | https://docs.slack.dev/reference/methods/chat.postMessage/ |
| Read a thread | https://docs.slack.dev/reference/methods/conversations.replies/ |
| Read reactions | https://docs.slack.dev/reference/methods/reactions.get/ |

Sign-in: OAuth through a Slack app, and a workspace admin approves which AI tools may connect.

## Applicant tracking systems

**Ashby**

| What | Where |
| --- | --- |
| Ashby's MCP announcement (ChatGPT, Claude, Cursor) | https://www.ashbyhq.com/blog/all/mcp-blog |
| API reference | https://developers.ashbyhq.com/ |
| Create a candidate, add a note, add a tag | https://developers.ashbyhq.com/reference/candidatecreate , https://developers.ashbyhq.com/reference/candidatecreatenote , https://developers.ashbyhq.com/reference/candidateaddtag |
| Set a custom field | https://developers.ashbyhq.com/reference/customfieldsetvalue |
| Authentication | https://developers.ashbyhq.com/docs/authentication |

Sign-in: an API key that an Ashby admin creates, with read and write set per module. Ask for only
the modules the workflow touches.

**Greenhouse**

| What | Where |
| --- | --- |
| Greenhouse's MCP server (US-hosted, OAuth) | https://support.greenhouse.io/hc/en-us/articles/53944054829083-Greenhouse-MCP-security-FAQ |
| Harvest API v3 | https://harvestdocs.greenhouse.io/docs/getting-started |
| Candidates, applications, notes | https://harvestdocs.greenhouse.io/reference/get_v3-candidates , https://harvestdocs.greenhouse.io/reference/get_v3-applications , https://harvestdocs.greenhouse.io/reference/post_v3-notes |

Sign-in: a Greenhouse site admin sets the MCP scopes under Dev Center, MCP Access. Changing them
makes everyone sign in again.

**Lever**

| What | Where |
| --- | --- |
| API (opportunities, notes, tags) | https://hire.lever.co/developer/documentation |

Sign-in: an API key from Settings, Integrations and API. Lever had no MCP server when checked.

## Mail and calendar

**Gmail and Google Calendar**

| What | Where |
| --- | --- |
| Claude's Google Workspace connectors (Gmail, Calendar, Drive) | https://support.claude.com/en/articles/10166901-use-google-workspace-connectors |
| Google's own MCP servers (developer preview) | https://developers.google.com/workspace/guides/configure-mcp-servers |
| Create a Gmail draft | https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.drafts/create |
| Create a calendar event, find free time | https://developers.google.com/workspace/calendar/api/v3/reference/events/insert , https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query |

Sign-in: Google OAuth. On a Claude Team or Enterprise plan an owner turns the connectors on
first. Google's own MCP servers need a Google Cloud project and a place in the preview.

**Outlook and Microsoft 365**

| What | Where |
| --- | --- |
| Claude's Microsoft 365 connector | https://support.claude.com/en/articles/15183774-connect-to-microsoft-365 |
| Create a draft message | https://learn.microsoft.com/en-us/graph/api/user-post-messages |

Sign-in: a Microsoft admin consents once. Drafting mail needs a further admin step.

## Sheets and CRM

| What | Where |
| --- | --- |
| Append rows to a Google Sheet | https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets.values/append |
| HubSpot's MCP server | https://developers.hubspot.com/docs/build-with-ai/remote-mcp-server |

## Where an agent runs on a schedule

| Option | Where | Good for |
| --- | --- | --- |
| Claude Code routines (research preview) | https://code.claude.com/docs/en/routines | A weekly run with no machine of your own. They use claude.ai connectors |
| Claude Code in GitHub Actions | https://code.claude.com/docs/en/github-actions , with a schedule: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule | A run the team can read and change in a repository |
| Claude Agent SDK | https://code.claude.com/docs/en/agent-sdk/overview | Your own agent, in your own code |
| n8n | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/ , https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/ | A visual flow on a schedule, calling an API or an MCP server |
| Zapier MCP | https://docs.zapier.com/mcp/home | Giving an agent actions in apps that have no MCP server of their own |
| Make | https://developers.make.com/mcp-server | The same, for teams already on Make |

## Adding an MCP server to the agent

| Tool | Where |
| --- | --- |
| Claude Code | https://code.claude.com/docs/en/mcp |
| Claude on the web or desktop | https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp |
| Codex | https://learn.chatgpt.com/docs/extend/mcp |
| Cursor | https://cursor.com/docs/mcp |
| ChatGPT | https://developers.openai.com/plugins/deploy/connect-chatgpt |
| The protocol itself | https://modelcontextprotocol.io/specification/latest |
