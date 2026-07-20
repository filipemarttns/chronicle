const API_URL = process.env.NEXT_PUBLIC_CHRONICLE_API_URL ?? "http://localhost:8000";
const API_TOKEN = process.env.NEXT_PUBLIC_CHRONICLE_API_TOKEN ?? "";

export function apiBase(): string {
  return API_URL.replace(/\/$/, "");
}

function authHeaders(extra?: HeadersInit): HeadersInit {
  const headers: Record<string, string> = {
    ...(extra as Record<string, string> | undefined),
  };
  if (API_TOKEN) {
    headers.Authorization = `Bearer ${API_TOKEN}`;
  }
  return headers;
}

export type TimelineItem = {
  event_id: string;
  type: string;
  occurred_at: string;
  source: string;
  store_offset: number;
  session_id?: string | null;
  summary?: string;
};

export type SearchHit = {
  chunk_id: string;
  score: number;
  snippet: string;
  citations: string[];
};

export async function fetchReplay(workspaceId: string): Promise<TimelineItem[]> {
  const url = new URL(`${apiBase()}/v1/timelines/replay`);
  url.searchParams.set("workspace_id", workspaceId);
  url.searchParams.set("limit", "50");
  const res = await fetch(url, { cache: "no-store", headers: authHeaders() });
  if (!res.ok) {
    throw new Error(`timeline failed: ${res.status}`);
  }
  const data = await res.json();
  return data.items ?? [];
}

export async function searchMemory(workspaceId: string, query: string): Promise<SearchHit[]> {
  const res = await fetch(`${apiBase()}/v1/search`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ workspace_id: workspaceId, query, limit: 20 }),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`search failed: ${res.status}`);
  }
  const data = await res.json();
  return data.hits ?? [];
}

export async function enableEditorConsent(workspaceId: string): Promise<void> {
  const res = await fetch(`${apiBase()}/v1/consent`, {
    method: "PUT",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      workspace_id: workspaceId,
      categories: {
        editor: true,
        terminal: true,
        git: true,
        browser: false,
        assistant: false,
        build: true,
      },
    }),
  });
  if (!res.ok) {
    throw new Error(`consent failed: ${res.status}`);
  }
}
