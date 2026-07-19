"use client";

import { useState } from "react";
import { enableEditorConsent, fetchReplay, type TimelineItem } from "@/lib/api";

export default function TimelinePage() {
  const [workspaceId, setWorkspaceId] = useState("");
  const [items, setItems] = useState<TimelineItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onLoad() {
    setLoading(true);
    setError(null);
    try {
      await enableEditorConsent(workspaceId);
      const next = await fetchReplay(workspaceId);
      setItems(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Timeline</h1>
      <p className="lead">Replay projected events for a workspace.</p>
      <section className="panel">
        <label htmlFor="workspace">Workspace ID</label>
        <input
          id="workspace"
          value={workspaceId}
          onChange={(e) => setWorkspaceId(e.target.value)}
          placeholder="uuid"
        />
        <button type="button" onClick={onLoad} disabled={!workspaceId || loading}>
          {loading ? "Loading…" : "Load replay"}
        </button>
        {error ? <p className="meta">{error}</p> : null}
        <div style={{ marginTop: "1rem" }}>
          {items.length === 0 ? (
            <p className="meta">No items yet.</p>
          ) : (
            items.map((item) => (
              <div className="item" key={item.event_id}>
                <strong>{item.type}</strong>
                <div className="meta">
                  {item.occurred_at} · {item.source} · offset {item.store_offset}
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}
