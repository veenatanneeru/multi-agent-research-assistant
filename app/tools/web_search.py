"""Web search tool used by the Researcher agent.

Step 2 (final): uses Tavily's search API instead of scraping
DuckDuckGo. Tavily is built for AI agents, returns clean already-
summarized content per result, and is far more reliable than free
scraping. Requires TAVILY_API_KEY in .env.
"""
import logging

from tavily import TavilyClient

from app.config.settings import settings

logger = logging.getLogger(__name__)

MAX_RESULTS = 3  # how many search results to fetch per sub-question


def search_web(query: str) -> dict:
    """Search the web for `query` using Tavily and return findings + sources.

    This is the function the Researcher agent (app/agents/researcher.py)
    calls for each sub-question. It never raises — on failure it returns
    an empty summary so the graph can still complete and the Summarizer
    can report "no findings" honestly.
    """
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY is not set; skipping search.")
        return {
            "summary": "No search performed: TAVILY_API_KEY is not configured.",
            "sources": [],
        }

    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(
            query=query,
            max_results=MAX_RESULTS,
            include_answer=False,
        )
    except Exception as exc:  # noqa: BLE001 - log and give up, don't crash the graph
        logger.warning("Tavily search failed for %r: %s", query, exc)
        return {
            "summary": f"Search failed for '{query}': {exc}",
            "sources": [],
        }

    results = response.get("results", [])

    if not results:
        return {
            "summary": f"No search results found for: '{query}'.",
            "sources": [],
        }

    findings_parts = []
    sources = []

    for result in results:
        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", "")

        if not content:
            continue

        findings_parts.append(f"Source: {title}\n{content}")
        sources.append(url)

    if not findings_parts:
        return {
            "summary": f"Found {len(results)} result(s) for '{query}' but "
            f"none had usable content.",
            "sources": [],
        }

    summary = "\n\n---\n\n".join(findings_parts)
    return {"summary": summary, "sources": sources}
