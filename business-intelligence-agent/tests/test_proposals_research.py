import pytest

from laforest_bi.proposals import generate_proposal_draft
from laforest_bi.company_research import save_company_research


def test_proposal_draft_uses_supplied_facts_and_marks_draft():
    text = generate_proposal_draft(
        client_name="Client A", project_title="Bridge assessment",
        scope="Visual and document-based structural assessment.",
        deliverables="Inspection report and recommendations.",
        assumptions="Access provided by client.", exclusions="Detailed redesign.",
        schedule="Three weeks after mobilization.", fee_basis="Fee to be agreed.",
    )
    assert "DRAFT" in text
    assert "Bridge assessment" in text
    assert "Visual and document-based structural assessment." in text


def test_proposal_requires_core_fields():
    with pytest.raises(ValueError, match="project_title"):
        generate_proposal_draft(
            client_name="Client A", project_title="", scope="Scope",
            deliverables="Report", assumptions="", exclusions="", schedule="", fee_basis=""
        )


def test_verified_company_requires_sources(tmp_path):
    db = str(tmp_path / "test.sqlite3")
    with pytest.raises(ValueError, match="source URLs"):
        save_company_research("Example Ltd", verification_status="verified", db_path=db)
