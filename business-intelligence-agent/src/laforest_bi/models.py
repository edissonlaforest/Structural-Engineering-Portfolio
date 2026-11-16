"""Typed records used by LAFOREST AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json


@dataclass
class Lead:
    company_name: str
    contact_name: str = ""
    email: str = ""
    website: str = ""
    country: str = ""
    service_fit: str = ""
    description: str = ""
    source_url: str = ""
    source_name: str = ""
    status: str = "new"
    ratings: dict[str, float] | None = None
    id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["ratings"] = json.dumps(self.ratings or {}, ensure_ascii=False)
        return data


@dataclass
class Tender:
    title: str
    buyer: str = ""
    country: str = ""
    location: str = ""
    deadline: str = ""
    publication_date: str = ""
    estimated_value: float | None = None
    currency: str = ""
    eligibility: str = ""
    description: str = ""
    source_url: str = ""
    source_name: str = ""
    status: str = "open"


@dataclass
class CompanyProfile:
    company_name: str
    website: str = ""
    country: str = ""
    sectors: str = ""
    project_references: str = ""
    service_fit: str = ""
    research_notes: str = ""
    source_urls: str = ""
    verification_status: str = "needs_review"
