"""Command-line interface for LAFOREST AI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from laforest_bi.database import initialize_database
from laforest_bi.discovery import (
    import_leads_csv, import_tenders_csv, import_feed_tenders, import_companies_csv,
)
from laforest_bi.qualification import qualify_lead
from laforest_bi.repository import list_leads, update_lead_status
from laforest_bi.proposals import write_proposal_draft
from laforest_bi.database import connect


def main() -> None:
    parser = argparse.ArgumentParser(description="LAFOREST AI Engineering Business Intelligence")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-db", help="Initialize the local SQLite database")
    leads_import = commands.add_parser("import-leads", help="Import leads from CSV")
    leads_import.add_argument("file")
    tenders_import = commands.add_parser("import-tenders", help="Import tenders from CSV")
    tenders_import.add_argument("file")
    companies_import = commands.add_parser("import-companies", help="Import research profiles from CSV")
    companies_import.add_argument("file")
    feed_import = commands.add_parser("import-feed", help="Import a configured RSS/Atom tender feed")
    feed_import.add_argument("url")
    feed_import.add_argument("--source-name", required=True)
    leads_list = commands.add_parser("list-leads", help="List CRM leads")
    leads_list.add_argument("--status")
    rate = commands.add_parser("rate-lead", help="Save 0-5 ratings for a lead as JSON")
    rate.add_argument("lead_id", type=int)
    rate.add_argument("ratings_json", help="JSON object with all six scoring criteria")
    score = commands.add_parser("score-lead", help="Qualify a lead using its stored ratings")
    score.add_argument("lead_id", type=int)
    status = commands.add_parser("set-status", help="Update a lead pipeline status")
    status.add_argument("lead_id", type=int)
    status.add_argument("status")
    proposal = commands.add_parser("draft-proposal", help="Create an editable proposal draft")
    proposal.add_argument("lead_id", type=int)
    proposal.add_argument("--output", required=True)
    proposal.add_argument("--project-title", required=True)
    proposal.add_argument("--scope", required=True)
    proposal.add_argument("--deliverables", required=True)
    proposal.add_argument("--assumptions", default="")
    proposal.add_argument("--exclusions", default="")
    proposal.add_argument("--schedule", default="")
    proposal.add_argument("--fee-basis", default="")
    commands.add_parser("dashboard", help="Launch the Streamlit dashboard")

    args = parser.parse_args()
    initialize_database()
    try:
        if args.command == "init-db":
            print("Database initialized.")
        elif args.command == "import-leads":
            print(f"Imported {import_leads_csv(args.file)} leads.")
        elif args.command == "import-tenders":
            print(f"Imported {import_tenders_csv(args.file)} tenders.")
        elif args.command == "import-companies":
            print(f"Imported {import_companies_csv(args.file)} company profiles.")
        elif args.command == "import-feed":
            print(f"Imported {import_feed_tenders(args.url, args.source_name)} tenders.")
        elif args.command == "list-leads":
            print(json.dumps(list_leads(status=args.status), indent=2, ensure_ascii=False))
        elif args.command == "rate-lead":
            from laforest_bi.lead_scoring import score_opportunity
            from laforest_bi.repository import get_lead
            ratings = json.loads(args.ratings_json)
            score_opportunity(ratings)  # Validate completeness and 0–5 scale before saving.
            if get_lead(args.lead_id) is None:
                raise ValueError(f"Lead {args.lead_id} was not found")
            with connect() as db:
                db.execute(
                    "UPDATE leads SET ratings_json=?, score=NULL, priority='', "
                    "updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (json.dumps(ratings), args.lead_id),
                )
            print("Lead ratings saved.")
        elif args.command == "score-lead":
            print(json.dumps(qualify_lead(args.lead_id), indent=2, ensure_ascii=False))
        elif args.command == "set-status":
            if not update_lead_status(args.lead_id, args.status):
                raise ValueError(f"Lead {args.lead_id} was not found")
            print("Lead status updated.")
        elif args.command == "draft-proposal":
            from laforest_bi.repository import get_lead
            lead = get_lead(args.lead_id)
            if lead is None:
                raise ValueError(f"Lead {args.lead_id} was not found")
            output = write_proposal_draft(
                args.output, client_name=lead["company_name"],
                project_title=args.project_title, scope=args.scope,
                deliverables=args.deliverables, assumptions=args.assumptions,
                exclusions=args.exclusions, schedule=args.schedule, fee_basis=args.fee_basis,
            )
            print(f"Draft written to {output}")
        elif args.command == "dashboard":
            subprocess.run([sys.executable, "-m", "streamlit", "run",
                            "src/laforest_bi/dashboard.py"], check=False)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
