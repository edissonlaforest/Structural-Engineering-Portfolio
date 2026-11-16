"""Optional Brave Search API adapter for public lead discovery.

Only search-engine API results are consumed; the adapter does not crawl result pages.
Candidates are unverified and must be reviewed before CRM qualification or outreach.
"""

from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from laforest_bi.models import Lead
from laforest_bi.repository import add_lead


def normalize_brave_results(payload: dict, query: str) -> list[dict[str, str]]:
    web_results = payload.get("web", {}).get("results", [])
    normalized = []
    for item in web_results:
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        description = str(item.get("description", "")).strip()
        if not title or not url.startswith(("https://", "http://")):
            continue
        normalized.append({
            "company_name": title[:250],
            "description": (
                f"Unverified public search candidate. Search query: {query}. "
                f"Search snippet: {description}"
            ),
            "source_url": url,
            "source_name": "Brave Search API",
            "service_fit": "Research candidate — verify company and service fit",
        })
    return normalized


def search_brave(query: str, count: int = 20, api_key: str | None = None,
                 timeout: int = 20) -> list[dict[str, str]]:
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    if not 1 <= count <= 20:
        raise ValueError("Brave Search count must be between 1 and 20")
    token = api_key or os.getenv("BRAVE_SEARCH_API_KEY")
    if not token:
        raise RuntimeError("BRAVE_SEARCH_API_KEY is not configured")
    params = urlencode({"q": query, "count": count})
    request = Request(
        f"https://api.search.brave.com/res/v1/web/search?{params}",
        headers={"Accept": "application/json", "X-Subscription-Token": token},
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return normalize_brave_results(payload, query)


def discover_brave_leads(query: str, count: int = 20, db_path: str | None = None) -> int:
    """Store search results as unverified lead candidates."""
    results = search_brave(query, count)
    imported = 0
    for result in results:
        add_lead(Lead(
            company_name=result["company_name"],
            service_fit=result["service_fit"],
            description=result["description"],
            source_url=result["source_url"],
            source_name=result["source_name"],
        ), db_path)
        imported += 1
    return imported
