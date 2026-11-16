"""SQLite database initialization and connection helpers."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS leads (
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
 score REAL,
 priority TEXT DEFAULT '',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS tenders (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT NOT NULL,
 buyer TEXT DEFAULT '',
 country TEXT DEFAULT '',
 location TEXT DEFAULT '',
 deadline TEXT DEFAULT '',
 publication_date TEXT DEFAULT '',
 estimated_value REAL,
 currency TEXT DEFAULT '',
 eligibility TEXT DEFAULT '',
 description TEXT DEFAULT '',
 source_url TEXT DEFAULT '',
 source_name TEXT DEFAULT '',
 status TEXT NOT NULL DEFAULT 'open',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS companies (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 company_name TEXT NOT NULL UNIQUE,
 website TEXT DEFAULT '',
 country TEXT DEFAULT '',
 sectors TEXT DEFAULT '',
 project_references TEXT DEFAULT '',
 service_fit TEXT DEFAULT '',
 research_notes TEXT DEFAULT '',
 source_urls TEXT DEFAULT '',
 verification_status TEXT NOT NULL DEFAULT 'needs_review',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS activities (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 entity_type TEXT NOT NULL,
 entity_id INTEGER NOT NULL,
 activity_type TEXT NOT NULL,
 note TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_tenders_deadline ON tenders(deadline);
"""


def database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", "data/laforest_bi.sqlite3"))


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    target = Path(path) if path else database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(path: str | Path | None = None) -> None:
    with connect(path) as connection:
        connection.executescript(SCHEMA)
