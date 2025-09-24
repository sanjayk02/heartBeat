// src/project/asset-data/useFetchAllAssets.ts
import { useEffect, useRef, useState } from "react";
import type { Asset } from "./types";

type Result = {
  data: Asset[] | null;
  isLoading: boolean;
  error: Error | null;
};

const API_BASE = process.env.REACT_APP_API_BASE ?? "http://localhost:4000"; // change if needed

export default function useFetchAllAssets(projectKeyName: string | null): Result {
  const [data, setData] = useState<Asset[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const acRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!projectKeyName) {
      setData(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    // abort previous
    if (acRef.current) {
      try { acRef.current.abort(); } catch (_) {}
      acRef.current = null;
    }

    const ac = new AbortController();
    acRef.current = ac;

    let cancelled = false;

    const run = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const all: Asset[] = [];
        let page = 1;
        const perPage = 200; // tune: reduce if responses get too big

        while (true) {
          if (ac.signal.aborted) {
            // throw to break to catch -> handled as abort
            throw new Error("AbortError");
          }

          const params = new URLSearchParams();
          params.set("per_page", String(perPage));
          params.set("page", String(page)); // server expects 1-based

          const url = `${API_BASE}/api/projects/${encodeURIComponent(projectKeyName)}/reviews/assets?${params.toString()}`;

          // If you have auth helpers, add them here:
          // const headers = getAuthHeader(); // <-- implement/enable if needed
          const headers: Record<string,string> = { Accept: "application/json" };

          // DEBUG: you can uncomment this to inspect final URL
          // console.log("[useFetchAllAssets] fetching:", url);

          const res = await fetch(url, { method: "GET", headers: headers, signal: ac.signal });

          // treat 401 specially if you have token-refresh flow
          if (res.status === 401) {
            // optionally: handle auth (setNewToken etc.)
            throw new Error("Unauthorized");
          }
          if (!res.ok) {
            throw new Error("HTTP " + res.status);
          }

          const json = await res.json();

          const pageAssets = Array.isArray(json.assets) ? json.assets : [];
          all.push(...pageAssets);

          // stop if fewer than page size or server indicates end
          if (pageAssets.length < perPage) {
            break;
          }
          page += 1;
        }

        if (!cancelled) {
          setData(all);
        }
      } catch (err) {
        const e = err as any;
        if (e && (e.name === "AbortError" || e.message === "AbortError")) {
          // aborted -> ignore silently
        } else {
          setError(e instanceof Error ? e : new Error(String(e)));
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    run();

    return () => {
      cancelled = true;
      try { ac.abort(); } catch (_) {}
      acRef.current = null;
    };
  }, [projectKeyName]);

  return { data, isLoading, error };
}
