# Container Diagram

C4 Level 2 — runnable containers in the reference deployment.

```mermaid
C4Container
    title Chronicle Containers

    Person(dev, "Developer / Operator")

    System_Boundary(clients, "Capture & Experience") {
        Container(ext_vscode, "Editor Extension", "TypeScript", "Emits editor/terminal/git events")
        Container(ext_browser, "Browser Extension", "TypeScript", "Opt-in page visit events")
        Container(web, "Web Console", "Next.js", "Timeline, search, analytics UI")
        Container(desktop, "Desktop Shell", "Tauri", "Local control plane")
        Container(mcp, "MCP Server", "Python", "Tool surface for assistants")
    }

    System_Boundary(backend, "Chronicle Backend") {
        Container(api, "API", "FastAPI", "Ingest, query, authn, consent")
        Container(worker, "Workers", "Celery", "Project, embed, graph, retention")
        Container(scheduler, "Scheduler", "Celery Beat", "Periodic jobs")
        ContainerDb(pg, "PostgreSQL", "Postgres + pgvector", "Event store, read models, vectors")
        ContainerDb(redis, "Redis", "Redis", "Broker, cache, rate limits")
    }

    Rel(dev, web, "Uses")
    Rel(dev, desktop, "Uses")
    Rel(ext_vscode, api, "HTTPS JSON")
    Rel(ext_browser, api, "HTTPS JSON")
    Rel(web, api, "HTTPS JSON")
    Rel(desktop, api, "HTTPS JSON")
    Rel(mcp, api, "In-process or HTTPS")
    Rel(api, pg, "SQL")
    Rel(api, redis, "Queue / cache")
    Rel(worker, pg, "SQL")
    Rel(worker, redis, "Consume jobs")
    Rel(scheduler, redis, "Enqueue")
```

## Container responsibilities

| Container | Writes | Reads |
| --- | --- | --- |
| API | Event log, outbox, auth artifacts | Read models for queries |
| Workers | Projections, embeddings, graph, analytics | Event log, outbox |
| Scheduler | Job schedules via broker | Configuration |
| PostgreSQL | Durable state | — |
| Redis | Ephemeral broker/cache state | — |

Clients never receive database credentials.
