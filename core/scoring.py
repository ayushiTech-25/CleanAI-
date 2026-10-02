from __future__ import annotations

from typing import Any

import pandas as pd


def calculate_quality_scores(df: pd.DataFrame, reports: dict[str, Any]) -> tuple[int, int]:
    """Calculate the shared health and ML readiness scores for a dataset."""
    total_cells = len(df) * len(df.columns)
    null_percent = (
        float(df.isnull().sum().sum() / total_cells * 100)
        if total_cells
        else 0.0
    )
    duplicate_percent = (
        float(df.duplicated().sum() / len(df) * 100)
        if len(df)
        else 0.0
    )

    def count(statistics_key: str, detector: str) -> int:
        statistics = reports.get(detector, {}).get("statistics", {})
        return len(statistics.get(statistics_key, {}))

    outlier_cols = count("outliers_by_column", "OutliersDetector")
    wrong_type_cols = count("columns_to_cast", "DataTypeDetector")
    constant_cols = count("constant_columns", "ConstantColumnsDetector")
    empty_cols = count("empty_columns", "EmptyColumnsDetector")
    cardinality_cols = count("high_cardinality_columns", "HighCardinalityDetector")
    mixed_cols = count("mixed_columns", "MixedTextDetector")
    space_cols = count("space_anomalies", "ExtraSpacesDetector")
    date_cols = count("invalid_date_columns", "InvalidDateDetector")

    health_penalty = (
        null_percent * 1.2
        + duplicate_percent
        + outlier_cols * 4.0
        + wrong_type_cols * 5.0
        + constant_cols * 10.0
        + empty_cols * 15.0
        + cardinality_cols * 4.0
        + mixed_cols * 4.0
        + space_cols * 2.0
        + date_cols * 8.0
    )
    readiness_penalty = (
        null_percent * 2.2
        + duplicate_percent * 0.5
        + outlier_cols * 8.0
        + wrong_type_cols * 6.0
        + constant_cols * 12.0
        + empty_cols * 20.0
        + cardinality_cols * 5.0
        + mixed_cols * 4.0
        + space_cols
        + date_cols * 10.0
    )

    health_score = max(0, min(100, int(100 - health_penalty)))
    readiness_score = max(0, min(100, int(100 - readiness_penalty)))
    return health_score, readiness_score