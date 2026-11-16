"""Persistence operations for the LAFOREST AI CRM."""

from __future__ import annotations

import json
from typing import Any

from laforest_bi.database import connect
from laforest_bi.models import Lead, Tender, CompanyProfile


def add_lead(lead: Lead, path: str | None = None) -> int:
    data = lead.to_dict()
    with connect(path) as db:
        cursor = db.execute(
            """INSERT INTO leads
            (company_name,contact_name,email,website,country,service_fit,description,
             source_url,source_name,status,ratings_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            tuple(data[key] for key in (
                "company_name", "contact_name", "email", "website", "country",
                "service_fit", "description", "source_url", "source_name", "status", "ratings"
            )),
        )
        return int(cursor.lastrowid)


def _lead_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["ratings"] = json.loads(item.pop("ratings_json") or "{}")
    return item


def list_leads(path: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    with connect(path) as db:
        rows = db.execute(
            "SELECT * FROM leads WHERE status=? ORDER BY id DESC" if status
            else "SELECT * FROM leads ORDER BY id DESC",
            (status,) if status else (),
        )
        return [_lead_dict(row) for row in rows.fetchall()]


def get_lead(lead_id: int, path: str | None = None) -> dict[str, Any] | None:
    with connect(path) as db:
        row = db.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
        return _lead_dict(row) if row else None


def update_lead_status(lead_id: int, status: str, path: str | None = None) -> bool:
    allowed = {"new", "qualified", "contacted", "meeting", "proposal", "won", "lost", "on_hold"}
    if status not in allowed:
        raise ValueError(f"Unsupported lead status: {status}")
    with connect(path) as db:
        cursor = db.execute(
            "UPDATE leads SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, lead_id),
        )
        return cursor.rowcount == 1


def add_tender(tender: Tender, path: str | None = None) -> int:
    with connect(path) as db:
        cursor = db.execute(
            """INSERT INTO tenders
            (title,buyer,country,location,deadline,publication_date,estimated_value,currency,
             eligibility,description,source_url,source_name,status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                tender.title, tender.buyer, tender.country, tender.location, tender.deadline,
                tender.publication_date, tender.estimated_value, tender.currency,
                tender.eligibility, tender.description, tender.source_url, tender.source_name,
                tender.status,
            ),
        )
        return int(cursor.lastrowid)


def list_tenders(path: str | None = None) -> list[dict[str, Any]]:
    with connect(path) as db:
        rows = db.execute("SELECT * FROM tenders ORDER BY deadline ASC, id DESC")
        return [dict(row) for row in rows.fetchall()]


def add_company(profile: CompanyProfile, path: str | None = None) -> int:
    with connect(path) as db:
        cursor = db.execute(
            """INSERT INTO companies
            (company_name,website,country,sectors,project_references,service_fit,
             research_notes,source_urls,verification_status)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(company_name) DO UPDATE SET
              website=excluded.website,country=excluded.country,sectors=excluded.sectors,
              project_references=excluded.project_references,service_fit=excluded.service_fit,
              research_notes=excluded.research_notes,source_urls=excluded.source_urls,
              verification_status=excluded.verification_status""",
            (
                profile.company_name, profile.website, profile.country, profile.sectors,
                profile.project_references, profile.service_fit, profile.research_notes,
                profile.source_urls, profile.verification_status,
            ),
        )
        return int(cursor.lastrowid or 0)


def add_activity(entity_type: str, entity_id: int, activity_type: str, note: str,
                 path: str | None = None) -> int:
    with connect(path) as db:
        cursor = db.execute(
            "INSERT INTO activities(entity_type,entity_id,activity_type,note) VALUES (?,?,?,?)",
            (entity_type, entity_id, activity_type, note),
        )
        return int(cursor.lastrowid)


def dashboard_metrics(path: str | None = None) -> dict[str, int]:
    with connect(path) as db:
        return {
            "total_leads": int(db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]),
            "open_tenders": int(db.execute(
                "SELECT COUNT(*) FROM tenders WHERE status='open'").fetchone()[0]),
            "active_pipeline": int(db.execute(
                """SELECT COUNT(*) FROM leads WHERE status IN
                ('qualified','contacted','meeting','proposal')""").fetchone()[0]),
            "won_leads": int(db.execute(
                "SELECT COUNT(*) FROM leads WHERE status='won'").fetchone()[0]),
        }
