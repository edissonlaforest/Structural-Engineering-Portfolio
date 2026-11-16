"""Scheduled polling loop for configured public leads and tender sources."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import yaml

from laforest_bi.discovery import import_configured_feeds
from laforest_bi.search_provider import discover_brave_leads

LOGGER = logging.getLogger("laforest_bi.monitor")


def load_search_queries(config_path: str | Path) -> list[dict[str, Any]]:
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8")) or {}
    searches = config.get("searches", [])
    if not isinstance(searches, list):
        raise TypeError("The search configuration 'searches' field must be a list.")
    enabled = []
    for item in searches:
        if not isinstance(item, dict):
            raise TypeError("Each search configuration must be a mapping.")
        if item.get("enabled", False):
            query = str(item.get("query", "")).strip()
            if not query:
                raise ValueError("Enabled search entries require a query.")
            count = int(item.get("count", 10))
            if not 1 <= count <= 20:
                raise ValueError("Search count must be between 1 and 20.")
            enabled.append({"query": query, "count": count})
    return enabled


def run_monitor_cycle(
    *,
    feeds_config: str | Path = "config/sources.yaml",
    searches_config: str | Path = "config/search_queries.yaml",
) -> dict[str, int]:
    """Run one configured discovery cycle; failures are surfaced to the caller."""
    feed_count = import_configured_feeds(feeds_config)
    search_count = 0
    for item in load_search_queries(searches_config):
        search_count += discover_brave_leads(item["query"], item["count"])
    LOGGER.info("Cycle completed: %s tender notices, %s search candidates.",
                feed_count, search_count)
    return {"tenders_imported": feed_count, "leads_discovered": search_count}


def run_monitor(
    interval_hours: float = 24,
    *,
    feeds_config: str | Path = "config/sources.yaml",
    searches_config: str | Path = "config/search_queries.yaml",
    run_once: bool = False,
) -> None:
    """Run a foreground monitor. Stop with Ctrl+C or the host process manager."""
    if interval_hours <= 0:
        raise ValueError("interval_hours must be greater than zero.")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    interval_seconds = interval_hours * 3600
    while True:
        try:
            run_monitor_cycle(
                feeds_config=feeds_config,
                searches_config=searches_config,
            )
        except Exception:
            LOGGER.exception("Monitoring cycle failed; it will retry at the next interval.")
        if run_once:
            return
        LOGGER.info("Next discovery cycle in %.2f hours.", interval_hours)
        time.sleep(interval_seconds)
