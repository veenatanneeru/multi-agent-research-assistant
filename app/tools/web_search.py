"""Web search tool used by the Researcher agent.

Step 2: real implementation.
  1. `_search_duckduckgo`  -> get a handful of candidate result URLs
  2. `_fetch_page_text`    -> download each page and strip it to plain text
  3. `search_web`          -> the public function the agent calls; combines
                              the two above and returns findings + sources

No API key is required anywhere in this file.
"""
import logging

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

MAX_RESULTS = 3          # how many search results to fetch per sub-question
FETCH_TIMEOUT = 10.0      # seconds, per page fetch
MAX_CHARS_PER_PAGE = 3000  # truncate long pages so we don't blow up the LLM prompt

# Some sites reject requests with no User-Agent header, so we set one that
# looks like an ordinary browser.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _search_duckduckgo(query: str, max_results: int = MAX_RESULTS) -> list[dict]:
    """Return a list of {"title": str, "url": str} search results.

    Uses the duckduckgo-search library, which scrapes DuckDuckGo's public
    search results — no API key, no account needed.
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                # duckduckgo-search returns dicts with "title", "href", "body"
                url = r.get("href")
                title = r.get("title", "")
                if url:
                    results.append({"title": title, "url": url})
    except Exception as exc:  # noqa: BLE001 - log and continue, don't crash the graph
        logger.warning("DuckDuckGo search failed for %r: %s", query, exc)

    return results


def _fetch_page_text(url: str) -> str:
    """Download a page and return its main readable text, truncated.

    Returns an empty string if the fetch or parse fails for any reason
    (dead link, timeout, non-HTML content, etc.) — callers should treat
    an empty string as "skip this source" rather than crash.
    """
    try:
        response = httpx.get(
            url, headers=HEADERS, timeout=FETCH_TIMEOUT, follow_redirects=True
        )
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch %s: %s", url, exc)
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Strip elements that are never useful content: scripts, styles, nav,
    # headers/footers, and ads typically live in these tags.
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return text[:MAX_CHARS_PER_PAGE]


def search_web(query: str) -> dict:
    """Search the web for `query` and return combined findings + sources.

    This is the function the Researcher agent (app/agents/researcher.py)
    calls for each sub-question. It never raises — on total failure it
    returns an empty summary so the graph can still complete and the
    Summarizer can report "no findings" honestly.
    """
    results = _search_duckduckgo(query)

    if not results:
        return {
            "summary": f"No search results found for: '{query}'.",
            "sources": [],
        }

    findings_parts = []
    sources = []

    for result in results:
        page_text = _fetch_page_text(result["url"])
        if not page_text:
            continue  # skip sources we couldn't fetch, don't fail the whole search

        findings_parts.append(f"Source: {result['title']}\n{page_text}")
        sources.append(result["url"])

    if not findings_parts:
        return {
            "summary": f"Found {len(results)} result(s) for '{query}' but "
            f"could not fetch content from any of them.",
            "sources": [],
        }

    summary = "\n\n---\n\n".join(findings_parts)
    return {"summary": summary, "sources": sources}
