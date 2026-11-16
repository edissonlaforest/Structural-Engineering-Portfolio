"""Interactive Streamlit workspace for LAFOREST AI."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from laforest_bi.ai_assistant import (
    write_research_report, draft_proposal_with_ai, suggest_lead_ratings,
)
from laforest_bi.database import initialize_database
from laforest_bi.discovery import import_leads_csv, import_tenders_csv, import_companies_csv
from laforest_bi.repository import (
    dashboard_metrics, list_leads, list_tenders, list_companies,
    update_lead_status, get_lead, save_lead_ratings,
)
from laforest_bi.qualification import qualify_lead

st.set_page_config(page_title="LAFOREST AI | E-BIS", layout="wide")
initialize_database()
st.title("LAFOREST AI")
st.caption("Engineering Business Intelligence System — research, qualification and CRM")

with st.sidebar:
    st.header("Data import")
    upload_options = [
        ("Lead CSV", "leads"),
        ("Tender CSV", "tenders"),
        ("Company CSV", "companies"),
    ]
    for label, kind in upload_options:
        uploaded = st.file_uploader(label, type=["csv"], key=f"upload_{kind}")
        if uploaded and st.button(f"Import {kind}", key=f"import_{kind}"):
            suffix = ".csv"
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
                    temp.write(uploaded.getvalue())
                    temp_path = temp.name
                importer = {
                    "leads": import_leads_csv,
                    "tenders": import_tenders_csv,
                    "companies": import_companies_csv,
                }[kind]
                count = importer(temp_path)
                st.success(f"Imported {count} {kind}.")
                st.rerun()
            except Exception as exc:
                st.error(f"Import failed: {exc}")
            finally:
                if temp_path and Path(temp_path).exists():
                    Path(temp_path).unlink()

    st.divider()
    st.header("Public lead discovery")
    search_query = st.text_input("Search query", placeholder="Bridge engineering consultants Canada")
    if st.button("Search public web", disabled=not search_query.strip()):
        try:
            from laforest_bi.search_provider import discover_brave_leads
            with st.spinner("Searching public web sources..."):
                count = discover_brave_leads(search_query)
            st.success(f"Added {count} unverified candidates. Review them before qualification.")
            st.rerun()
        except Exception as exc:
            st.error(f"Search failed: {exc}")

    st.divider()
    st.header("AI research")
    research_query = st.text_area(
        "Company, project or tender to research",
        placeholder="Research bridge rehabilitation tenders in Ontario, Canada",
    )
    if st.button("Generate sourced research report", disabled=not research_query.strip()):
        try:
            with st.spinner("Researching public sources..."):
                result = write_research_report(
                    "reports/latest-research.md", research_query
                )
            st.success(
                f"Report saved. {len(result['sources'])} cited source(s) returned."
            )
            st.session_state["latest_research_report"] = Path(
                result["output_path"]
            ).read_text(encoding="utf-8")
        except Exception as exc:
            st.error(f"AI research failed: {exc}")

metrics = dashboard_metrics()
columns = st.columns(4)
for column, label, value in zip(
    columns, ["Total leads", "Open tenders", "Active pipeline", "Won leads"],
    [metrics["total_leads"], metrics["open_tenders"],
     metrics["active_pipeline"], metrics["won_leads"]],
):
    column.metric(label, value)

if st.session_state.get("latest_research_report"):
    with st.expander("Latest AI research report", expanded=True):
        st.markdown(st.session_state["latest_research_report"])

st.subheader("Lead pipeline")
leads = list_leads()
if leads:
    st.dataframe([{
        "ID": item["id"], "Company": item["company_name"], "Country": item["country"],
        "Service fit": item["service_fit"], "Status": item["status"],
        "Score": item["score"], "Priority": item["priority"],
        "Source": item["source_name"], "Source URL": item["source_url"],
    } for item in leads], use_container_width=True, hide_index=True)

    st.markdown("#### Update pipeline status")
    lead_ids = {f"{item['id']} — {item['company_name']}": item["id"] for item in leads}
    selected_label = st.selectbox("Select lead", list(lead_ids))
    selected_id = lead_ids[selected_label]
    current = get_lead(selected_id)
    statuses = ["new", "qualified", "contacted", "meeting", "proposal", "won", "lost", "on_hold"]
    chosen_status = st.selectbox(
        "New status", statuses,
        index=statuses.index(current["status"]) if current["status"] in statuses else 0,
    )
    if st.button("Save status"):
        update_lead_status(selected_id, chosen_status)
        st.success("Pipeline status updated.")
        st.rerun()

    if st.button("Generate AI qualification suggestion"):
        try:
            with st.spinner("Researching public evidence and assessing this lead..."):
                st.session_state["ai_lead_assessment"] = suggest_lead_ratings(current)
                st.session_state["ai_lead_assessment_id"] = selected_id
        except Exception as exc:
            st.error(f"AI qualification failed: {exc}")

    if st.session_state.get("ai_lead_assessment_id") == selected_id:
        assessment = st.session_state.get("ai_lead_assessment")
        if assessment:
            st.markdown("#### AI qualification suggestion — review before approval")
            st.metric("Suggested score", f"{assessment['score']}/100")
            st.write(f"Suggested priority: **{assessment['priority']}**")
            st.write(f"Confidence indicator: {assessment['confidence']}/100")
            st.json({
                "ratings": assessment["ratings"],
                "criterion_rationales": assessment["criterion_rationales"],
                "evidence_gaps": assessment["evidence_gaps"],
                "sources": assessment["sources"],
            })
            if st.button("Approve and save these suggested ratings"):
                save_lead_ratings(selected_id, assessment["ratings"])
                qualify_lead(selected_id)
                st.session_state.pop("ai_lead_assessment", None)
                st.session_state.pop("ai_lead_assessment_id", None)
                st.success("Ratings approved, saved and scored using the transparent weighted rubric.")
                st.rerun()

    with st.expander("Create an AI-assisted proposal draft"):
        project_title = st.text_input("Project title")
        scope = st.text_area("Approved scope of services")
        deliverables = st.text_area("Deliverables")
        assumptions = st.text_area("Assumptions")
        exclusions = st.text_area("Exclusions")
        schedule = st.text_input("Schedule (or leave blank)")
        fee_basis = st.text_input("Fee basis (or leave blank)")
        if st.button("Generate proposal draft with AI"):
            try:
                fields = {
                    "client_name": current["company_name"],
                    "project_title": project_title,
                    "scope": scope,
                    "deliverables": deliverables,
                    "assumptions": assumptions,
                    "exclusions": exclusions,
                    "schedule": schedule,
                    "fee_basis": fee_basis,
                }
                draft = draft_proposal_with_ai(fields)
                destination = Path("reports") / f"proposal-lead-{selected_id}.md"
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(draft, encoding="utf-8")
                st.success(f"Draft saved to {destination}")
                st.markdown(draft)
            except Exception as exc:
                st.error(f"Proposal generation failed: {exc}")
else:
    st.info("No leads yet. Import a CSV file or use public lead discovery in the sidebar.")

st.subheader("Tender watchlist")
tenders = list_tenders()
if tenders:
    st.dataframe([{
        "ID": item["id"], "Tender": item["title"], "Buyer": item["buyer"],
        "Country": item["country"], "Deadline": item["deadline"],
        "Status": item["status"], "Source URL": item["source_url"],
    } for item in tenders], use_container_width=True, hide_index=True)
else:
    st.info("No tenders yet. Import tender notices from CSV or configured public feeds.")

st.subheader("Company research directory")
companies = list_companies()
if companies:
    st.dataframe([{
        "Company": item["company_name"], "Country": item["country"],
        "Sectors": item["sectors"], "Service fit": item["service_fit"],
        "Verification": item["verification_status"], "Sources": item["source_urls"],
    } for item in companies], use_container_width=True, hide_index=True)
else:
    st.info("No company profiles yet. Import a company research CSV to populate this directory.")

st.warning(
    "AI research, qualification and proposal drafting are decision-support tools. "
    "Verify sources, eligibility, deadlines, engineering assumptions and commercial terms. "
    "No outreach, bid submission, payment, signature or contract acceptance is automated."
)
