"""Transparent weighted scoring for engineering business opportunities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import math


DEFAULT_WEIGHTS: dict[str, int] = {
    "project_relevance": 25,
    "financial_potential": 20,
    "geographic_suitability": 15,
    "outsourcing_likelihood": 15,
    "technical_compatibility": 15,
    "decision_maker_accessibility": 10,
}


@dataclass(frozen=True)
class ScoreResult:
    score: float
    priority: str
    breakdown: dict[str, float]


def score_opportunity(
    ratings: Mapping[str, int | float],
    weights: Mapping[str, int | float] | None = None,
) -> ScoreResult:
    """Score an opportunity from 0 to 100 using ratings from 0 to 5.

    Every criterion must be supplied. Weights must be non-negative and have
    a positive total. The result is a prioritization aid, not a win probability.
    """
    selected_weights = dict(weights or DEFAULT_WEIGHTS)

    if set(ratings) != set(selected_weights):
        missing = sorted(set(selected_weights) - set(ratings))
        extra = sorted(set(ratings) - set(selected_weights))
        raise ValueError(f"Rating criteria mismatch; missing={missing}, extra={extra}")

    for criterion, weight in selected_weights.items():
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError(f"Weight for {criterion} must be numeric.")
        if not math.isfinite(float(weight)) or weight < 0:
            raise ValueError("Weights must be finite and non-negative.")

    total_weight = float(sum(selected_weights.values()))
    if total_weight <= 0:
        raise ValueError("The sum of weights must be greater than zero.")

    breakdown: dict[str, float] = {}
    for criterion, weight in selected_weights.items():
        rating = ratings[criterion]
        if isinstance(rating, bool) or not isinstance(rating, (int, float)):
            raise ValueError(f"Rating for {criterion} must be numeric.")
        if not math.isfinite(float(rating)) or not 0 <= rating <= 5:
            raise ValueError(f"Rating for {criterion} must be finite and between 0 and 5.")
        breakdown[criterion] = (float(rating) / 5.0) * float(weight)

    score = round(sum(breakdown.values()) / total_weight * 100.0, 2)

    if score >= 80:
        priority = "high_priority"
    elif score >= 60:
        priority = "qualified"
    elif score >= 40:
        priority = "monitor"
    else:
        priority = "low_priority"

    return ScoreResult(score=score, priority=priority, breakdown=breakdown)
