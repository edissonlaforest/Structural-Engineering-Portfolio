"""Streamlit executive dashboard for LAFOREST AI."""

import streamlit as st

from laforest_bi.database import initialize_database
from laforest_bi.repository import dashboard_metrics, list_leads, list_tenders, list_companies

st.set_page_config(page_title="LAFOREST AI | E-BIS", layout="wide")
initialize_database()
st.title("LAFOREST AI")
st.caption("Engineering Business Intelligence System — human-supervised decision support")

metrics = dashboard_metrics()
columns = st.columns(4)
for column, label, value in zip(
    columns, ["Total leads", "Open tenders", "Active pipeline", "Won leads"],
    [metrics["total_leads"], metrics["open_tenders"],
     metrics["active_pipeline"], metrics["won_leads"]],
):
    column.metric(label, value)

st.subheader("Lead pipeline")
leads = list_leads()
if leads:
    st.dataframe([{
        "ID": item["id"], "Company": item["company_name"], "Country": item["country"],
        "Service fit": item["service_fit"], "Status": item["status"],
        "Score": item["score"], "Priority": item["priority"],
        "Source": item["source_name"], "Source URL": item["source_url"],
    } for item in leads], use_container_width=True, hide_index=True)
else:
    st.info("No leads yet. Import a CSV file using the CLI to populate the CRM.")

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

st.warning(
    "Verify source information, eligibility, deadlines, and technical/commercial requirements "
    "before acting. This system does not send messages or submit bids."
)


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
