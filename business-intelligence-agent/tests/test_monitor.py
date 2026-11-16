from laforest_bi.monitor import load_search_queries


def test_load_search_queries_returns_only_enabled_entries(tmp_path):
    config = tmp_path / "searches.yaml"
    config.write_text(
        "searches:\n"
        "  - query: bridge design opportunities Canada\n"
        "    count: 8\n"
        "    enabled: true\n"
        "  - query: disabled query\n"
        "    enabled: false\n",
        encoding="utf-8",
    )
    assert load_search_queries(config) == [{
        "query": "bridge design opportunities Canada",
        "count": 8,
    }]


def test_load_search_queries_rejects_invalid_count(tmp_path):
    config = tmp_path / "searches.yaml"
    config.write_text(
        "searches:\n  - query: bridge tenders\n    count: 30\n    enabled: true\n",
        encoding="utf-8",
    )
    import pytest
    with pytest.raises(ValueError, match="between 1 and 20"):
        load_search_queries(config)
