"""Command-line interface for LAFOREST BI."""

from __future__ import annotations

import argparse
import json
import sys

from laforest_bi.lead_scoring import score_opportunity


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score an engineering business opportunity from a JSON ratings file."
    )
    parser.add_argument("ratings_json", help="Path to JSON file containing criterion ratings.")
    args = parser.parse_args()

    try:
        with open(args.ratings_json, encoding="utf-8") as source:
            ratings = json.load(source)
        result = score_opportunity(ratings)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2) from error

    print(
        json.dumps(
            {
                "score": result.score,
                "priority": result.priority,
                "breakdown": result.breakdown,
                "interpretation": "Prioritization aid only; not a probability of winning.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
