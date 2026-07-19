import { apiBase } from "@/lib/api";

export default function HomePage() {
  return (
    <main>
      <h1>Chronicle</h1>
      <p className="lead">
        Developer Memory Engine console. Capture flows into the event log; timeline and
        search read from projected memory.
      </p>
      <section className="panel">
        <p className="meta">
          API base: <code>{apiBase()}</code>
        </p>
        <p className="meta ok">Local-first · consent-scoped · rebuildable projections</p>
        <p style={{ marginTop: "1.25rem" }}>
          <a href="/timeline">Open timeline</a>
          {" · "}
          <a href="/search">Search memory</a>
        </p>
      </section>
    </main>
  );
}
