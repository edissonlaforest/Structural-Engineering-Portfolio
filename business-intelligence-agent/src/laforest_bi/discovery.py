"""Public-source ingestion for leads and tender notices.

Feed URLs must be configured by the operator after checking source terms.
This module does not crawl arbitrary websites or bypass access controls.
"""

from __future__ import annotations

import csv
from pathlib import Path

import feedparser

from laforest_bi.models import Lead, Tender
from laforest_bi.repository import add_lead, add_tender
from laforest_bi.company_research import save_company_research


def import_leads_csv(file_path: str | Path, db_path: str | None = None) -> int:
    count = 0
    with Path(file_path).open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            name = (row.get("company_name") or "").strip()
            if not name:
                continue
            add_lead(Lead(
                company_name=name,
                contact_name=(row.get("contact_name") or "").strip(),
                email=(row.get("email") or "").strip(),
                website=(row.get("website") or "").strip(),
                country=(row.get("country") or "").strip(),
                service_fit=(row.get("service_fit") or "").strip(),
                description=(row.get("description") or "").strip(),
                source_url=(row.get("source_url") or "").strip(),
                source_name=(row.get("source_name") or "CSV import").strip(),
            ), db_path)
            count += 1
    return count


def import_tenders_csv(file_path: str | Path, db_path: str | None = None) -> int:
    count = 0
    with Path(file_path).open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            title = (row.get("title") or "").strip()
            if not title:
                continue
            value = (row.get("estimated_value") or "").strip()
            add_tender(Tender(
                title=title, buyer=(row.get("buyer") or "").strip(),
                country=(row.get("country") or "").strip(),
                location=(row.get("location") or "").strip(),
                deadline=(row.get("deadline") or "").strip(),
                publication_date=(row.get("publication_date") or "").strip(),
                estimated_value=float(value) if value else None,
                currency=(row.get("currency") or "").strip(),
                eligibility=(row.get("eligibility") or "").strip(),
                description=(row.get("description") or "").strip(),
                source_url=(row.get("source_url") or "").strip(),
                source_name=(row.get("source_name") or "CSV import").strip(),
            ), db_path)
            count += 1
    return count


def parse_feed(feed_url: str, source_name: str, category: str = "tender") -> list[dict[str, str]]:
    """Parse one operator-configured RSS/Atom feed."""
    parsed = feedparser.parse(feed_url)
    if parsed.bozo and not parsed.entries:
        raise ValueError(f"Could not parse feed from {source_name}: {parsed.bozo_exception}")
    items = []
    for entry in parsed.entries:
        items.append({
            "title": str(entry.get("title", "")).strip(),
            "summary": str(entry.get("summary", "")).strip(),
            "url": str(entry.get("link", "")).strip(),
            "published": str(entry.get("published", entry.get("updated", ""))).strip(),
            "source_name": source_name,
            "category": category,
        })
    return items


def import_feed_tenders(feed_url: str, source_name: str,
                        db_path: str | None = None) -> int:
    count = 0
    for item in parse_feed(feed_url, source_name, "tender"):
        if item["title"] and item["url"]:
            add_tender(Tender(
                title=item["title"], description=item["summary"],
                publication_date=item["published"], source_url=item["url"],
                source_name=source_name,
            ), db_path)
            count += 1
    return count



def import_companies_csv(file_path: str | Path, db_path: str | None = None) -> int:
    count = 0
    with Path(file_path).open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            name = (row.get("company_name") or "").strip()
            if not name:
                continue
            save_company_research(
                name,
                website=(row.get("website") or ""),
                country=(row.get("country") or ""),
                sectors=(row.get("sectors") or ""),
                project_references=(row.get("project_references") or ""),
                service_fit=(row.get("service_fit") or ""),
                research_notes=(row.get("research_notes") or ""),
                source_urls=(row.get("source_urls") or ""),
                verification_status=(row.get("verification_status") or "needs_review"),
                db_path=db_path,
            )
            count += 1
    return count


def import_configured_feeds(config_path: str | Path = "config/sources.yaml",
                             db_path: str | None = None) -> int:
    """Import enabled tender feeds from an operator-maintained YAML registry."""
    import yaml

    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8")) or {}
    feeds = config.get("feeds", [])
    if not isinstance(feeds, list):
        raise ValueError("The sources YAML 'feeds' field must be a list")
    imported = 0
    for feed in feeds:
        if not isinstance(feed, dict):
            raise ValueError("Each configured feed must be a mapping")
        if not feed.get("enabled", False):
            continue
        url = str(feed.get("url", "")).strip()
        name = str(feed.get("name", "")).strip()
        if not url.startswith("https://") or not name:
            raise ValueError("Enabled feeds require a name and an HTTPS URL")
        if feed.get("category", "tender") != "tender":
            continue
        imported += import_feed_tenders(url, name, db_path)
    return imported
