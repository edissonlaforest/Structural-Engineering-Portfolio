# LAFOREST AI — Engineering Business Intelligence System (E-BIS)

A human-supervised business development and market intelligence workspace for structural engineering, bridge engineering, infrastructure consulting, BIM, inspections, and construction services.

## System modules (1–7)

1. **Global Lead Discovery** — import leads from approved public feeds, CSV files, and configured sources. Optional Brave Search API discovery stores unverified candidates with source URLs; repeated source URLs are deduplicated.
2. **Tender Intelligence** — monitor configured RSS/Atom procurement feeds and import tender notices from CSV. Track publication date, deadline, location, buyer, eligibility, source URL, and status; repeated source URLs are deduplicated.
3. **Company Research** — maintain evidence-backed company profiles, project references, service fit, source URLs, and research notes. Unverified facts must be marked as unverified.
4. **AI Qualification** — source-grounded AI suggestions for six 0–5 ratings, criterion rationales, confidence indicator and evidence gaps. A human must explicitly approve suggested ratings; the final 0–100 score is then calculated by the deterministic weighted rubric.
5. **CRM & Pipeline** — persist companies, leads, tenders, notes, and status changes in SQLite. PostgreSQL migration is planned for multi-user deployment.
6. **AI Proposal Generator** — create offline template drafts or OpenAI-assisted proposal prose from approved project inputs. Missing information must remain a visible placeholder; the model must not invent credentials, references, prices, engineering calculations, or commitments.
7. **Executive Dashboard** — Streamlit dashboard for pipeline, tender deadlines, lead priorities, and activity.

## Current implementation status

The MVP includes SQLite persistence and additive schema migration, CSV and RSS/Atom ingestion, an optional Brave Search API adapter, source-attributed company profiles, deterministic lead qualification, OpenAI Responses API web research with citation extraction, AI-assisted proposal drafting, an interactive Streamlit dashboard, a foreground recurring monitor, CLI commands, unit tests, and GitHub Actions CI.

**Still outside this MVP:** CRM synchronization, automatic email sending, bid submission, production authentication/multi-user access, PostgreSQL deployment, managed background scheduling, and production hosting. These require separate credentials, provider configuration, security review, and operational testing.

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
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -e ".[dev]"
# Copy .env.example to .env and add your own API credentials if using live search
pytest
laforest-bi init-db
laforest-bi dashboard
```

Or run the dashboard with `streamlit run src/laforest_bi/dashboard.py`.

Default database: `data/laforest_bi.sqlite3`. Set `DATABASE_PATH` to change it. Keep local database files and API credentials out of Git.

Copy `.env.example` to `.env`. Configure `OPENAI_API_KEY` for AI research and AI proposal drafting. The default model is `gpt-6-astra`; override it with `OPENAI_MODEL` if your API account uses a different supported model.

### Scheduled discovery monitor

The positioning, service lines, target markets and professional-practice guardrails are recorded in `config/business_profile.yaml`. Enable the approved RSS/Atom feeds in `config/sources.yaml` and the search terms in `config/search_queries.yaml` (they are disabled by default to avoid unexpected API charges). Add your Brave API key to `.env`, then run one cycle:

```bash
laforest-bi monitor --once
```

To keep monitoring every 24 hours in the foreground:

```bash
laforest-bi monitor --interval-hours 24
```

Keep the machine awake and the process running, or register the command with Windows Task Scheduler, cron, or another process manager. This monitor writes to the local SQLite database; it does not send emails or submit tenders. Duplicate source URLs are skipped.

### AI research and proposal drafting

The `research` command uses the OpenAI Responses API with the hosted `web_search` tool and saves a Markdown report with the citation URLs returned by the API:

```bash
laforest-bi research "bridge rehabilitation procurement opportunities Ontario Canada" --output reports/ontario-bridge-research.md
```

For AI-assisted proposal drafting, add `--ai` to the normal draft command. Without `--ai`, the deterministic offline template is used:

```bash
laforest-bi draft-proposal 1 --output reports/proposal-draft.md --project-title "Bridge assessment" --scope "Client-approved scope" --deliverables "Assessment report" --ai
```

AI research and proposal generation incur API usage and charges according to your OpenAI API account. Review every report and proposal before relying on or issuing it.

### Public lead search

The optional Brave Search API adapter requires a valid API subscription key. Set `BRAVE_SEARCH_API_KEY` in your local environment (never commit it). Search results are saved as **unverified candidates**, not confirmed companies. Verify company identity, relevance, contact details, source accuracy, and lawful basis before moving a candidate into the active pipeline. The search adapter uses the search API and does not scrape result pages.

## CLI examples

```bash
laforest-bi init-db
laforest-bi import-leads data/templates/leads.example.csv
laforest-bi import-tenders data/templates/tenders.example.csv
laforest-bi import-configured-feeds
laforest-bi import-companies data/templates/companies.example.csv
laforest-bi search-leads "bridge engineering consultants Canada" --count 10
laforest-bi research "bridge tenders in Ontario" --output reports/bridge-tenders.md
laforest-bi monitor --once
laforest-bi list-leads
laforest-bi ai-score-lead 1
# Or enter ratings manually:
laforest-bi rate-lead 1 '{"project_relevance":5,"financial_potential":4,"geographic_suitability":5,"outsourcing_likelihood":4,"technical_compatibility":5,"decision_maker_accessibility":3}'
laforest-bi score-lead 1
laforest-bi draft-proposal 1 --output reports/proposal-draft.md --project-title "Bridge assessment" --scope "Scope approved by client" --deliverables "Assessment report"
laforest-bi dashboard
```

CSV import templates and an example scoring JSON are provided under `data/templates/`. For production use, replace all example rows with verified source data. Company CSV columns: `company_name,website,country,sectors,project_references,service_fit,research_notes,source_urls,verification_status`.

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

Next milestones: official procurement portal connectors by target country; richer entity resolution beyond source-URL deduplication; PostgreSQL and role-based access; alert delivery and CRM integrations; deployment hardening, monitoring, backups, and security review.
