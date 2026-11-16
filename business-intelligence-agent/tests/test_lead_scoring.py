import pytest

from laforest_bi.lead_scoring import DEFAULT_WEIGHTS, score_opportunity


def full_ratings(value: int = 5) -> dict[str, int]:
    return {criterion: value for criterion in DEFAULT_WEIGHTS}


def test_maximum_score_is_high_priority() -> None:
    result = score_opportunity(full_ratings(5))
    assert result.score == 100.0
    assert result.priority == "high_priority"


def test_zero_score_is_low_priority() -> None:
    result = score_opportunity(full_ratings(0))
    assert result.score == 0.0
    assert result.priority == "low_priority"


def test_weighted_score_and_priority_band() -> None:
    ratings = full_ratings(3)
    result = score_opportunity(ratings)
    assert result.score == 60.0
    assert result.priority == "qualified"


def test_rejects_rating_outside_scale() -> None:
    ratings = full_ratings()
    ratings["project_relevance"] = 6
    with pytest.raises(ValueError, match="between 0 and 5"):
        score_opportunity(ratings)


def test_rejects_missing_criterion() -> None:
    ratings = full_ratings()
    ratings.pop("project_relevance")
    with pytest.raises(ValueError, match="criteria mismatch"):
        score_opportunity(ratings)


def test_rejects_zero_total_weight() -> None:
    ratings = full_ratings()
    weights = {criterion: 0 for criterion in DEFAULT_WEIGHTS}
    with pytest.raises(ValueError, match="greater than zero"):
        score_opportunity(ratings, weights)
