"""Reusable non-graphical exploratory data analysis (EDA) functions.

Each function accepts a pandas DataFrame. Results are standard dictionaries,
which can be passed to the PDF reporter or tested independently.
"""

from typing import Any

import pandas as pd

from .validation import validate_dataframe


def dataset_overview(data: pd.DataFrame) -> dict[str, int]:
    """Summarize rows, columns and fully duplicated records."""
    data = validate_dataframe(data)
    return {
        "total_rows": int(len(data)),
        "total_columns": int(len(data.columns)),
        "duplicate_rows": int(data.duplicated().sum()),
    }


def missing_value_counts(data: pd.DataFrame) -> dict[str, int]:
    """Count null values in each column."""
    data = validate_dataframe(data)
    return {str(name): int(count) for name, count in data.isna().sum().items()}


def numeric_statistics(data: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    """Calculate descriptive statistics for available numeric columns."""
    data = validate_dataframe(data)
    numeric_data = data.select_dtypes(include="number")
    if len(numeric_data.columns) == 0:
        return {}

    description = numeric_data.describe().transpose()
    results: dict[str, dict[str, float | None]] = {}
    for column, row in description.iterrows():
        results[str(column)] = {
            str(metric): None if pd.isna(value) else round(float(value), 3)
            for metric, value in row.items()
        }
    return results


def categorical_statistics(data: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Summarize unique values and modes of non-numeric columns."""
    data = validate_dataframe(data)
    categorical_data = data.select_dtypes(exclude="number")
    results: dict[str, dict[str, Any]] = {}
    for column in categorical_data.columns:
        series = categorical_data[column]
        counts = series.value_counts(dropna=True)
        results[str(column)] = {
            "unique_values": int(series.nunique(dropna=True)),
            "most_common": str(counts.index[0]) if not counts.empty else None,
            "most_common_count": int(counts.iloc[0]) if not counts.empty else 0,
        }
    return results


def correlation_statistics(data: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    """Return Pearson correlations between numeric columns when possible."""
    data = validate_dataframe(data)
    numeric_data = data.select_dtypes(include="number")
    if len(numeric_data.columns) < 2:
        return {}

    correlations = numeric_data.corr()
    return {
        str(column): {
            str(other): None if pd.isna(value) else round(float(value), 3)
            for other, value in correlations[column].items()
        }
        for column in correlations.columns
    }


def calculate_eda_statistics(data: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Combine independent summary functions into a report-friendly result."""
    validate_dataframe(data)
    return {
        "overview": dataset_overview(data),
        "missing_values": missing_value_counts(data),
        "numeric_statistics": numeric_statistics(data),
        "categorical_statistics": categorical_statistics(data),
        "correlations": correlation_statistics(data),
    }
