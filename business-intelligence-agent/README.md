# LAFOREST AI — Engineering Business Intelligence System (E-BIS)

A research and business-development platform for structural engineering, infrastructure consulting, and construction services.

## Purpose

LAFOREST AI helps identify and qualify prospective clients, monitor public tenders and procurement notices, research companies and projects, maintain a traceable opportunity pipeline, and prepare draft outreach and proposal materials for human review.

## Initial scope

- Discover relevant public opportunities across target markets.
- Capture source URL, retrieval date, publication/deadline dates, location, scope, and eligibility notes.
- Score opportunities using transparent weighted criteria.
- Store leads and opportunities in a structured database.
- Generate research summaries and draft outreach; never send messages or submit bids automatically.

## Target services

Structural and bridge engineering; structural inspections and assessments; seismic evaluation and retrofit; BIM/Revit; infrastructure consulting; technical due diligence; construction support; and engineering automation.

## Target markets

United States, Canada, Dominican Republic, Caribbean, France, Brazil, Africa, and the Middle East. Market coverage will be configurable.

## Opportunity scoring

Each criterion is rated from 0 to 5 and converted to a weighted score out of 100:

| Criterion | Weight |
|---|---:|
| Project relevance | 25 |
| Financial potential | 20 |
| Geographic suitability | 15 |
| Outsourcing likelihood | 15 |
| Technical compatibility | 15 |
| Decision-maker accessibility | 10 |

Priority bands: 80–100 high priority; 60–79 qualified; 40–59 monitor; below 40 low priority. This score is a triage aid, not a probability of winning.

## Operating principles

1. Prefer official procurement portals, public company sources, and authorized APIs.
2. Respect site terms, robots rules, privacy requirements, rate limits, and access controls.
3. Do not bypass login controls, CAPTCHAs, paywalls, or technical restrictions.
4. Preserve provenance for every material claim and opportunity.
5. Require human approval before external outreach, bid submission, payments, contract acceptance, or signing.
6. Never store API keys, passwords, or personal access tokens in the repository.

## Planned architecture

Python research and scoring core; source adapters; SQLite for the initial local MVP with a migration path to PostgreSQL; Streamlit dashboard; n8n or scheduled jobs for orchestration; OpenAI API for supported summarization and drafting; GitHub Actions for tests and linting.

## Development status

Milestone 1: project charter and architecture specification. Ingestion connectors, scoring implementation, database, dashboard, and automated tests will be delivered and validated in subsequent milestones.
