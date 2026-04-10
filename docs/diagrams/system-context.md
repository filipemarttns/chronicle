# System Context Diagram

C4 Level 1 — Chronicle and its actors.

```mermaid
C4Context
    title Chronicle System Context

    Person(dev, "Developer / Operator", "Captures work, queries memory, manages consent")
    Person(teammate, "Teammate", "May share workspace memory when authorized")

    System(chronicle, "Chronicle", "Developer Memory Engine — ingest, timeline, search, graph, sync")

    System_Ext(vscode, "VS Code / Cursor", "Editor host for capture extension")
    System_Ext(browser, "Web Browser", "Host for opt-in research capture")
    System_Ext(githost, "Git Host", "GitHub/GitLab APIs for PR metadata")
    System_Ext(mcpclient, "MCP Client", "Assistant runtime consuming Chronicle tools")
    System_Ext(oidc, "IdP / OIDC", "Optional external authentication")

    Rel(dev, vscode, "Works in")
    Rel(dev, browser, "Researches in")
    Rel(dev, chronicle, "Operates console / desktop")
    Rel(vscode, chronicle, "Emits events over HTTPS")
    Rel(browser, chronicle, "Emits opt-in events")
    Rel(chronicle, githost, "Fetches PR metadata")
    Rel(mcpclient, chronicle, "Invokes memory tools")
    Rel(chronicle, oidc, "Validates tokens when configured")
    Rel(teammate, chronicle, "Queries shared workspace if permitted")
```

## Narrative

Developers interact with Chronicle through capture surfaces and the web/desktop consoles. All durable facts enter Chronicle as Events. External systems never write Timeline, Memory, or Knowledge Graph projections directly.

## Trust summary

| Boundary | Trust note |
| --- | --- |
| Extension → API | Authenticated; consent-gated categories |
| Browser → API | Opt-in; redaction applied |
| MCP → API | Scoped tools; redaction + audit |
| API → Git host | Outbound credentials stored as secrets |
| Operator → data plane | Full control on self-hosted deployments |

See also: [containers.md](containers.md), [../security/threat-model.md](../security/threat-model.md).
