"""Evidence-based company research profile workflow."""

from __future__ import annotations

from laforest_bi.models import CompanyProfile
from laforest_bi.repository import add_company


def save_company_research(
    company_name: str, *, website: str = "", country: str = "", sectors: str = "",
    project_references: str = "", service_fit: str = "", research_notes: str = "",
    source_urls: str = "", verification_status: str = "needs_review",
    db_path: str | None = None,
) -> int:
    allowed = {"needs_review", "partially_verified", "verified"}
    if verification_status not in allowed:
        raise ValueError(f"verification_status must be one of {sorted(allowed)}")
    if not company_name.strip():
        raise ValueError("company_name is required")
    if verification_status == "verified" and not source_urls.strip():
        raise ValueError("Verified company profiles must include source URLs")
    return add_company(CompanyProfile(
        company_name=company_name.strip(), website=website.strip(), country=country.strip(),
        sectors=sectors.strip(), project_references=project_references.strip(),
        service_fit=service_fit.strip(), research_notes=research_notes.strip(),
        source_urls=source_urls.strip(), verification_status=verification_status,
    ), db_path)
