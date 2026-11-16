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


def test_configured_feed_import_skips_disabled_sources(tmp_path, monkeypatch):
    from laforest_bi import discovery

    config = tmp_path / "sources.yaml"
    config.write_text(
        "feeds:\n"
        "  - name: enabled-feed\n"
        "    url: https://example.org/feed.xml\n"
        "    category: tender\n"
        "    enabled: true\n"
        "  - name: disabled-feed\n"
        "    url: https://example.org/disabled.xml\n"
        "    enabled: false\n",
        encoding="utf-8",
    )
    calls = []
    monkeypatch.setattr(
        discovery, "import_feed_tenders",
        lambda url, name, db_path=None: calls.append((url, name)) or 2,
    )
    assert discovery.import_configured_feeds(config) == 2
    assert calls == [("https://example.org/feed.xml", "enabled-feed")]


def test_normalize_brave_results_marks_candidates_unverified():
    from laforest_bi.search_provider import normalize_brave_results

    payload = {"web": {"results": [{
        "title": "Regional Bridge Consultants",
        "url": "https://example.org/services",
        "description": "Bridge inspection and design services."
    }]}}
    results = normalize_brave_results(payload, query="bridge engineering Canada")
    assert len(results) == 1
    assert results[0]["company_name"] == "Regional Bridge Consultants"
    assert results[0]["source_url"] == "https://example.org/services"
    assert "verify" in results[0]["service_fit"].lower()
