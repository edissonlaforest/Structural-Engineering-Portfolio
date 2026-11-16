import csv

from laforest_bi.database import initialize_database
from laforest_bi.discovery import import_leads_csv, import_tenders_csv
from laforest_bi.repository import list_leads, list_tenders


def test_import_leads_csv_preserves_source(tmp_path):
    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    csv_path = tmp_path / "leads.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "company_name", "country", "source_url", "source_name"
        ])
        writer.writeheader()
        writer.writerow({
            "company_name": "Bridge Consult", "country": "USA",
            "source_url": "https://example.org/company", "source_name": "Test directory"
        })
    assert import_leads_csv(csv_path, db) == 1
    lead = list_leads(db)[0]
    assert lead["source_url"] == "https://example.org/company"
    assert lead["source_name"] == "Test directory"


def test_import_tenders_csv(tmp_path):
    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    csv_path = tmp_path / "tenders.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["title", "buyer", "deadline"])
        writer.writeheader()
        writer.writerow({"title": "Road bridge design", "buyer": "Transport Agency",
                         "deadline": "2027-01-30"})
    assert import_tenders_csv(csv_path, db) == 1
    assert list_tenders(db)[0]["buyer"] == "Transport Agency"


def test_import_companies_csv_records_verification_and_sources(tmp_path):
    from laforest_bi.discovery import import_companies_csv
    from laforest_bi.repository import list_companies

    db = str(tmp_path / "test.sqlite3")
    initialize_database(db)
    csv_path = tmp_path / "companies.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "company_name", "country", "source_urls", "verification_status"
        ])
        writer.writeheader()
        writer.writerow({
            "company_name": "Verified Engineering", "country": "USA",
            "source_urls": "https://example.org/about", "verification_status": "verified"
        })
    assert import_companies_csv(csv_path, db) == 1
    companies = list_companies(db)
    assert companies[0]["company_name"] == "Verified Engineering"
    assert companies[0]["verification_status"] == "verified"
