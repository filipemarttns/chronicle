"use client";

import { useState } from "react";
import { searchMemory, type SearchHit } from "@/lib/api";

export default function SearchPage() {
  const [workspaceId, setWorkspaceId] = useState("");
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<SearchHit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSearch() {
    setLoading(true);
    setError(null);
    try {
      const next = await searchMemory(workspaceId, query);
      setHits(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Search</h1>
      <p className="lead">Token-overlap memory search over indexed event chunks.</p>
      <section className="panel">
        <label htmlFor="workspace">Workspace ID</label>
        <input
          id="workspace"
          value={workspaceId}
          onChange={(e) => setWorkspaceId(e.target.value)}
          placeholder="uuid"
        />
        <label htmlFor="query">Query</label>
        <input
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="pagination auth middleware"
        />
        <button type="button" onClick={onSearch} disabled={!workspaceId || !query || loading}>
          {loading ? "Searching…" : "Search"}
        </button>
        {error ? <p className="meta">{error}</p> : null}
        <div style={{ marginTop: "1rem" }}>
          {hits.map((hit) => (
            <div className="item" key={hit.chunk_id}>
              <strong>score {hit.score.toFixed(2)}</strong>
              <div className="meta">{hit.snippet}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
