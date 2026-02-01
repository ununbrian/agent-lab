from typing import List, Dict
from tavily import TavilyClient
import os

def tavily_search(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing TAVILY_API_KEY in .env")

    client = TavilyClient(api_key=api_key)
    resp = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
        include_answer=False,
        include_raw_content=False,
    )

    out: List[Dict[str, str]] = []
    for r in resp.get("results", []):
        out.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": (r.get("content", "") or "")[:400],
        })
    return out
