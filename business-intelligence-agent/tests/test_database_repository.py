import pytest

from laforest_bi.database import initialize_database
from laforest_bi.models import Lead, Tender
from laforest_bi.repository import (
    add_lead, add_tender, get_lead, list_leads, list_tenders,
    update_lead_status, dashboard_metrics, save_lead_ratings,
)


def test_lead_can_be_created_and_retrieved(tmp_path):
    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    lead_id = add_lead(Lead(company_name="Example Engineering", country="Canada"), db)
    lead = get_lead(lead_id, db)
    assert lead is not None
    assert lead["company_name"] == "Example Engineering"
    assert lead["country"] == "Canada"


def test_pipeline_status_is_validated(tmp_path):
    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    lead_id = add_lead(Lead(company_name="Example"), db)
    assert update_lead_status(lead_id, "proposal", db) is True
    assert get_lead(lead_id, db)["status"] == "proposal"
    with pytest.raises(ValueError):
        update_lead_status(lead_id, "invented-status", db)


def test_tender_is_stored_and_metrics_update(tmp_path):
    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    add_tender(Tender(title="Bridge rehabilitation", buyer="Public Works",
                      deadline="2027-02-01"), db)
    assert list_tenders(db)[0]["title"] == "Bridge rehabilitation"
    assert dashboard_metrics(db)["open_tenders"] == 1


def test_list_leads_can_filter_by_status(tmp_path):
    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    lead_id = add_lead(Lead(company_name="Qualified Co"), db)
    update_lead_status(lead_id, "qualified", db)
    assert len(list_leads(db, status="qualified")) == 1
    assert list_leads(db, status="new") == []



def test_lead_qualification_persists_score_without_destroying_ratings(tmp_path):
    from laforest_bi.qualification import qualify_lead
    from laforest_bi.lead_scoring import DEFAULT_WEIGHTS

    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    ratings = {criterion: 4 for criterion in DEFAULT_WEIGHTS}
    lead_id = add_lead(Lead(company_name="Scoring Co", ratings=ratings), db)
    result = qualify_lead(lead_id, db)
    assert result["score"] == 80.0
    stored = get_lead(lead_id, db)
    assert stored["score"] == 80.0
    assert stored["ratings"] == ratings
    assert stored["status"] == "qualified"


def test_database_initialization_migrates_legacy_leads_table(tmp_path):
    import sqlite3

    db = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(db) as connection:
        connection.execute("""
            CREATE TABLE leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_name TEXT DEFAULT '',
                email TEXT DEFAULT '',
                website TEXT DEFAULT '',
                country TEXT DEFAULT '',
                service_fit TEXT DEFAULT '',
                description TEXT DEFAULT '',
                source_url TEXT DEFAULT '',
                source_name TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'new',
                ratings_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute(
            "INSERT INTO leads(company_name, status) VALUES (?, ?)",
            ("Legacy Company", "new"),
        )
    initialize_database(str(db))
    lead = get_lead(1, str(db))
    assert lead is not None
    assert lead["score"] is None
    assert lead["priority"] == ""


def test_lead_and_tender_imports_deduplicate_by_source_url(tmp_path):
    db = str(tmp_path / "dedupe.sqlite3")
    initialize_database(db)
    first_lead = add_lead(Lead(
        company_name="Bridge Partner", source_url="https://example.org/company"
    ), db)
    second_lead = add_lead(Lead(
        company_name="Bridge Partner Updated", source_url="https://example.org/company"
    ), db)
    assert first_lead == second_lead
    assert len(list_leads(db)) == 1

    first_tender = add_tender(Tender(
        title="Bridge tender", source_url="https://example.gov/tender/123"
    ), db)
    second_tender = add_tender(Tender(
        title="Bridge tender duplicate", source_url="https://example.gov/tender/123"
    ), db)
    assert first_tender == second_tender
    assert len(list_tenders(db)) == 1



def test_save_lead_ratings_validates_and_resets_previous_score(tmp_path):
    from laforest_bi.lead_scoring import DEFAULT_WEIGHTS

    db = str(tmp_path / "ratings.sqlite3")
    initialize_database(db)
    lead_id = add_lead(Lead(company_name="Ratings Co"), db)
    ratings = {criterion: 3 for criterion in DEFAULT_WEIGHTS}
    assert save_lead_ratings(lead_id, ratings, db) is True
    stored = get_lead(lead_id, db)
    assert stored["ratings"] == ratings
    assert stored["score"] is None
    assert stored["priority"] == ""
    with pytest.raises(ValueError):
        save_lead_ratings(lead_id, {"project_relevance": 99}, db)
