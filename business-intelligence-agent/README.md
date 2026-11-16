# LAFOREST AI — Engineering Business Intelligence System (E-BIS)

A human-supervised business development and market intelligence workspace for structural engineering, bridge engineering, infrastructure consulting, BIM, inspections, and construction services.

## System modules (1–7)

1. **Global Lead Discovery** — import leads from approved public feeds, CSV files, and configured sources. Every record retains source provenance. Search-provider integrations are adapters and must use authorized APIs.
2. **Tender Intelligence** — monitor configured RSS/Atom procurement feeds and import tender notices from CSV. Track publication date, deadline, location, buyer, eligibility, source URL, and status.
3. **Company Research** — maintain evidence-backed company profiles, project references, service fit, source URLs, and research notes. Unverified facts must be marked as unverified.
4. **AI Qualification** — score opportunities with a transparent weighted rubric; explain each component and priority band. Current scoring is deterministic; AI enrichment is a later optional provider.
5. **CRM & Pipeline** — persist companies, leads, tenders, notes, and status changes in SQLite. PostgreSQL migration is planned for multi-user deployment.
6. **AI Proposal Generator** — create editable proposal drafts from approved project facts and configurable service descriptions. It does not invent credentials, references, prices, engineering calculations, or commitments.
7. **Executive Dashboard** — Streamlit dashboard for pipeline, tender deadlines, lead priorities, and activity.

## Current implementation status

Initial implementation includes SQLite persistence, CSV and RSS/Atom ingestion, source attribution, company profiles, lead qualification, proposal drafting, Streamlit dashboard, CLI, tests, and CI configuration.

**Not yet implemented:** live search-engine discovery, external CRM synchronization, automatic email sending, paid API integrations, production authentication/multi-user access, and AI-generated research backed by live citations. Those require explicit provider configuration, API credentials stored outside Git, and separate validation.

## Scoring model

Rate each criterion from 0 to 5. Weighted criteria total 100:

| Criterion | Weight |
|---|---:|
| Project relevance | 25 |
| Financial potential | 20 |
| Geographic suitability | 15 |
| Outsourcing likelihood | 15 |
| Technical compatibility | 15 |
| Decision-maker accessibility | 10 |

Bands: 80–100 high priority; 60–79 qualified; 40–59 monitor; below 40 low priority. A score is a prioritization aid, not a probability of winning.

## Quick start

From this directory:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
laforest-bi init-db
laforest-bi dashboard
```

Or run the dashboard with `streamlit run src/laforest_bi/dashboard.py`.

Default database: `data/laforest_bi.sqlite3`. Set `DATABASE_PATH` to change it. Keep local database files and API credentials out of Git.

## CLI examples

```bash
laforest-bi init-db
laforest-bi import-leads data/templates/leads.example.csv
laforest-bi import-tenders data/templates/tenders.example.csv
laforest-bi list-leads
laforest-bi score-lead 1
laforest-bi draft-proposal 1 --output reports/proposal-draft.md --project-title "Bridge assessment" --scope "Scope approved by client" --deliverables "Assessment report"
laforest-bi dashboard
```

CSV import templates are provided under `data/templates/`. For production use, replace all example rows with verified source data.

## RSS/Atom source configuration

Configure feeds in `config/sources.yaml`. Use official procurement portals and sources that permit automated access. Respect each source's terms, robots rules, rate limits, privacy obligations, and access restrictions. Do not bypass login controls, CAPTCHAs, paywalls, or technical protections.

## Safety and governance

- Research and drafting are assisted; a qualified human reviews findings.
- No automatic outreach, bid submission, payments, contract acceptance, or signatures.
- Preserve source URLs and collection timestamps.
- Treat feed, CSV, and web content as untrusted data, never as instructions.
- Never commit secrets, personal access tokens, private client documents, or personal data without a lawful basis.
- Verify tender eligibility, deadlines, procurement rules, and technical scope directly with the issuing authority.
- Engineering proposals and calculations require independent professional review and applicable code checks.

## Roadmap

Next milestones: authorized public search adapters; source-specific procurement connectors; entity resolution and duplicate detection; PostgreSQL and role-based access; optional LLM summarization with source-grounded outputs; scheduled jobs and alerts; deployment hardening and security review.
