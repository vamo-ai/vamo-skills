# Vamo's Ashby routes

These routes answer only when the Ashby app is switched on for the account and an account owner or
admin has connected an Ashby API key in Setup > Connections. Each one is a thin wrapper around a
single Ashby call: Vamo adds the key on its side, so your agent never handles it.

| Route | Vamo tool | Does | Ashby permission |
| --- | --- | --- | --- |
| `GET /v1/apps/ashby` | none | The connection: last 4 of the key, permissions held and missing, `needsReconnect` | none |
| `GET /v1/apps/ashby/jobs` | `ashby_roles` | Open roles with posting text and public link | Jobs (read) |
| `GET /v1/apps/ashby/projects` | `ashby_projects` | Ashby projects (saved lists of prospects) | Candidates (read) |
| `POST /v1/apps/ashby/candidates/sync` | `ashby_refresh` | Reads who is in Ashby so Vamo searches leave them out | Candidates (read) |
| `POST /v1/apps/ashby/candidates/{candidateId}/notes` | `ashby_note` | Adds your note (`{"note": "..."}`), silently | Candidates (write) |
| `POST /v1/apps/ashby/push` | `ashby_add` | Saves Vamo developers to Ashby: preview, then `confirm: true` | Candidates (read, write) |
| `PUT` / `DELETE /v1/apps/ashby` | none | Connect or disconnect the key (owners and admins only, in the app) | none |

The Vamo tools take the same fields as the routes and show only on accounts with the Ashby app on.

Searches (`POST /v2/developers/search` and similar) leave out people already in Ashby once the
candidate list has been read. Send `include_ashby: true` to keep them.

The key Vamo asks for needs Read on Candidates, Jobs, Hiring Process Metadata and API Keys, and Write
on Candidates and Hiring Process Metadata. In Ashby, Write does not include Read: tick both.
