from types import SimpleNamespace

import pytest

from laforest_bi import ai_assistant


class FakeResponses:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


class FakeClient:
    def __init__(self, response):
        self.responses = FakeResponses(response)


def test_research_uses_web_search_and_extracts_citations(monkeypatch):
    annotation = SimpleNamespace(
        type="url_citation",
        url="https://example.org/tender",
        title="Official Tender Notice",
    )
    content = SimpleNamespace(annotations=[annotation])
    message = SimpleNamespace(type="message", content=[content])
    response = SimpleNamespace(
        output_text="Tender summary [source].",
        output=[message],
        id="resp_test",
        model="test-model",
    )
    fake = FakeClient(response)
    monkeypatch.setattr(ai_assistant, "_client", lambda: fake)

    result = ai_assistant.research_with_web("bridge tender Canada")

    assert result["text"] == "Tender summary [source]."
    assert result["sources"] == [{
        "title": "Official Tender Notice",
        "url": "https://example.org/tender",
    }]
    assert fake.responses.kwargs["tool_choice"] == "required"
    assert fake.responses.kwargs["tools"][0]["type"] == "web_search"


def test_research_rejects_empty_query():
    with pytest.raises(ValueError, match="cannot be empty"):
        ai_assistant.research_with_web("  ")


def test_ai_proposal_requires_core_project_inputs():
    with pytest.raises(ValueError, match="project_title"):
        ai_assistant.draft_proposal_with_ai({
            "client_name": "Client",
            "project_title": "",
            "scope": "Scope",
            "deliverables": "Report",
        })


def test_ai_proposal_marks_output_as_draft(monkeypatch):
    response = SimpleNamespace(output_text="# Proposal draft")
    fake = FakeClient(response)
    monkeypatch.setattr(ai_assistant, "_client", lambda: fake)

    draft = ai_assistant.draft_proposal_with_ai({
        "client_name": "Client",
        "project_title": "Bridge assessment",
        "scope": "Visual inspection only",
        "deliverables": "Assessment report",
    })

    assert "DRAFT" in fake.responses.kwargs["instructions"]
    assert "NOT FOR ISSUE" in draft
