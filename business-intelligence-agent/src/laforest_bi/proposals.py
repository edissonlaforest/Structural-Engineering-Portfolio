"""Proposal draft generation from explicit user-approved project information."""

from __future__ import annotations

from pathlib import Path
from datetime import date


def generate_proposal_draft(
    *, client_name: str, project_title: str, scope: str, deliverables: str,
    assumptions: str, exclusions: str, schedule: str, fee_basis: str,
    prepared_by: str = "Eng. Edisson Laforest | Senior Structural Engineer",
) -> str:
    required = {"client_name": client_name, "project_title": project_title,
                "scope": scope, "deliverables": deliverables}
    missing = [key for key, value in required.items() if not value.strip()]
    if missing:
        raise ValueError(f"Required proposal fields are missing: {', '.join(missing)}")
    return f"""# Technical and Commercial Proposal — Draft

**Prepared for:** {client_name}
**Project:** {project_title}
**Prepared by:** {prepared_by}
**Date:** {date.today().isoformat()}
**Status:** DRAFT — subject to professional and commercial review

## 1. Understanding of the assignment
{scope}

## 2. Proposed deliverables
{deliverables}

## 3. Assumptions and information required
{assumptions or "To be confirmed with the client before engagement."}

## 4. Exclusions
{exclusions or "Define exclusions before issuing the proposal."}

## 5. Schedule
{schedule or "To be agreed after review of the complete scope and required inputs."}

## 6. Fee basis
{fee_basis or "Commercial fee to be confirmed after scope, deliverables, schedule, and contractual conditions are agreed."}

## 7. Professional review and authorization
This is a drafting aid, not an issued offer or engineering certification. Confirm scope, applicable codes, design criteria, insurance, professional registration requirements, taxes, payment terms, liability, and all commercial conditions before submission. Do not include unverified references, credentials, calculations, or commitments.

**Prepared by:** {prepared_by}
"""


def write_proposal_draft(output_path: str | Path, **fields: str) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(generate_proposal_draft(**fields), encoding="utf-8")
    return destination
