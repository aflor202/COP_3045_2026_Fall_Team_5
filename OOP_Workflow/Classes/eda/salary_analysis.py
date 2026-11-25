
"""Baseball-specific salary and performance analysis."""

from typing import Any

import pandas as pd


KEY_COLUMNS = ["playerID", "yearID", "teamID"]

BATTING_COLUMNS = [
    "G_left", "AB", "R", "H", "2B", "3B",
    "HR", "RBI", "SB_left", "BB", "SO",
]


def prepare_salary_data(data: pd.DataFrame) -> pd.DataFrame:
    """Return one salary record per player, team, and season."""
    required = KEY_COLUMNS + ["salary"]

    missing = set(required) - set(data.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if data.groupby(KEY_COLUMNS)["salary"].nunique().gt(1).any():
        raise ValueError(
            "Conflicting salaries within player/team/season groups."
        )

    salary_data = (
        data[required]
        .drop_duplicates(subset=KEY_COLUMNS)
        .dropna(subset=["salary"])
    )

    if salary_data.empty:
        raise ValueError("No valid salary records found.")

    return salary_data


def calculate_batting_correlations(
    data: pd.DataFrame,
    salary_data: pd.DataFrame,
) -> tuple[pd.DataFrame, int, int]:
    """Calculate Pearson correlations using complete batting records."""
    batting_keys = KEY_COLUMNS + ["stint_left"]

    batting = (
        data[batting_keys + BATTING_COLUMNS]
        .dropna(subset=["stint_left"])
        .drop_duplicates()
    )

    if batting.duplicated(subset=batting_keys).any():
        raise ValueError("Conflicting batting records found.")

    batting_totals = (
        batting.groupby(KEY_COLUMNS)[BATTING_COLUMNS]
        .sum(min_count=1)
        .reset_index()
    )

    analysis = batting_totals.merge(
        salary_data,
        on=KEY_COLUMNS,
        how="inner",
        validate="one_to_one",
    )

    complete = analysis[["salary"] + BATTING_COLUMNS].dropna()

    correlation = complete.corr(method="pearson")

    labels = {
        "salary": "Salary",
        "G_left": "G",
        "SB_left": "SB",
    }

    correlation = correlation.rename(
        index=labels,
        columns=labels,
    )

    return correlation, len(complete), len(analysis) - len(complete)


def calculate_league_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate salary statistics by league."""
    if data.groupby(KEY_COLUMNS)["lgID"].nunique().gt(1).any():
        raise ValueError(
            "Multiple leagues found within player/team/season groups."
        )

    league_data = (
        data[KEY_COLUMNS + ["lgID", "salary"]]
        .drop_duplicates(subset=KEY_COLUMNS)
        .dropna(subset=["lgID", "salary"])
    )

    return (
        league_data.groupby("lgID")["salary"]
        .agg(["count", "mean", "median"])
        .reindex(["AL", "NL"])
    )


def calculate_team_summary(
    salary_data: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """Calculate team salary statistics for a selected season."""
    team_data = salary_data[salary_data["yearID"] == year]

    return (
        team_data.groupby("teamID")["salary"]
        .agg(["count", "mean", "median"])
        .sort_values("median")
    )


def calculate_top_players(
    salary_data: pd.DataFrame,
    year: int,
) -> pd.Series:
    """Identify the ten highest recorded player salaries, including ties."""
    player_data = salary_data[salary_data["yearID"] == year]

    return (
        player_data.groupby("playerID")["salary"]
        .max()
        .nlargest(10, keep="all")
        .sort_values()
    )


def calculate_salary_analysis(
    data: pd.DataFrame,
) -> dict[str, Any]:
    """Coordinate all baseball-specific analytical calculations."""
    salary_data = prepare_salary_data(data)

    correlation, complete_count, excluded_count = (
        calculate_batting_correlations(data, salary_data)
    )

    latest_year = int(salary_data["yearID"].max())

    return {
        "salary_data": salary_data,
        "salary_records": len(salary_data),
        "mean_salary": float(salary_data["salary"].mean()),
        "median_salary": float(salary_data["salary"].median()),
        "salary_skewness": float(salary_data["salary"].skew()),
        "correlation": correlation,
        "complete_count": complete_count,
        "excluded_count": excluded_count,
        "league_summary": calculate_league_summary(data),
        "team_summary": calculate_team_summary(
            salary_data, latest_year
        ),
        "top_players": calculate_top_players(
            salary_data, latest_year
        ),
        "first_year": int(data["yearID"].min()),
        "latest_year": latest_year,
    }
