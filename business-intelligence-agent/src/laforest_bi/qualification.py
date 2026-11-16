"""Lead qualification orchestration."""

from __future__ import annotations

from laforest_bi.lead_scoring import score_opportunity
from laforest_bi.database import connect
from laforest_bi.repository import get_lead, update_lead_status


def qualify_lead(lead_id: int, db_path: str | None = None) -> dict:
    lead = get_lead(lead_id, db_path)
    if lead is None:
        raise ValueError(f"Lead {lead_id} was not found")
    ratings = lead.get("ratings") or {}
    result = score_opportunity(ratings)
    with connect(db_path) as db:
        db.execute(
            "UPDATE leads SET score=?, priority=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (result.score, result.priority, lead_id),
        )
    if result.score >= 60 and lead["status"] == "new":
        update_lead_status(lead_id, "qualified", db_path)
    return {
        "lead_id": lead_id, "company_name": lead["company_name"],
        "score": result.score, "priority": result.priority,
        "breakdown": result.breakdown,
    }
