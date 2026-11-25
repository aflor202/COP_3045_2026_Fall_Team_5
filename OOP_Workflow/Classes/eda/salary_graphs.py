
"""Generate baseball salary and performance visualizations."""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import seaborn as sns


def save_graph(fig: plt.Figure, path: Path) -> str:
    """Save a graph and release its resources."""
    try:
        fig.savefig(path, dpi=300, bbox_inches="tight")
    finally:
        plt.close(fig)

    return str(path)


def plot_salary_distribution(
    results: dict[str, Any], folder: Path
) -> str:
    """Plot the distribution of player salaries."""
    salaries = results["salary_data"]["salary"] / 1_000_000

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.histplot(
        salaries, bins=40, color="steelblue", ax=ax
    )

    ax.axvline(
        salaries.mean(),
        color="red",
        linestyle="--",
        label=f"Mean: ${salaries.mean():.2f} million",
    )

    ax.axvline(
        salaries.median(),
        color="green",
        linestyle="--",
        label=f"Median: ${salaries.median():.2f} million",
    )

    ax.set_title(
        f"Salary Distribution, {results['first_year']}"
        f"-{results['latest_year']}"
    )
    ax.set_xlabel("Salary (millions of dollars)")
    ax.set_ylabel("Player/team/season records")
    ax.legend()

    fig.tight_layout()

    return save_graph(
        fig, folder / "salary_distribution.png"
    )


def plot_batting_correlations(
    results: dict[str, Any], folder: Path
) -> str:
    """Plot Pearson correlations between salary and batting."""
    fig, ax = plt.subplots(figsize=(12, 9))

    sns.heatmap(
        results["correlation"],
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        ax=ax,
    )

    ax.set_title(
        "Salary and Batting Statistics: Pearson Correlations\n"
        f"{results['complete_count']:,} complete records"
    )

    fig.tight_layout()

    return save_graph(
        fig, folder / "salary_batting_correlation.png"
    )


def plot_league_salaries(
    results: dict[str, Any], folder: Path
) -> str:
    """Compare mean and median salaries between leagues."""
    plot_data = (
        results["league_summary"][["mean", "median"]]
        / 1_000_000
    )

    plot_data.columns = ["Mean", "Median"]
    plot_data.index = ["American League", "National League"]

    fig, ax = plt.subplots(figsize=(9, 6))

    plot_data.plot(
        kind="bar",
        ax=ax,
        color=["steelblue", "seagreen"],
        rot=0,
    )

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3)

    ax.set_title("Mean and Median Salaries by League")
    ax.set_xlabel("League")
    ax.set_ylabel("Salary (millions of dollars)")
    ax.set_ylim(0, plot_data.max().max() * 1.2)
    ax.legend()

    fig.tight_layout()

    return save_graph(
        fig, folder / "salary_by_league.png"
    )


def plot_team_salaries(
    results: dict[str, Any], folder: Path
) -> str:
    """Plot median salaries by team in the latest season."""
    summary = results["team_summary"]
    year = results["latest_year"]

    fig, ax = plt.subplots(figsize=(10, 11))

    bars = ax.barh(
        summary.index,
        summary["median"] / 1_000_000,
        color="steelblue",
    )

    ax.bar_label(bars, fmt="%.2f", padding=4)

    ax.set_title(f"Median Player Salary by Team, {year}")
    ax.set_xlabel("Median salary (millions of dollars)")
    ax.set_ylabel("Team ID")
    ax.set_xlim(
        0, summary["median"].max() / 1_000_000 * 1.2
    )

    fig.tight_layout()

    return save_graph(
        fig, folder / f"median_salary_by_team_{year}.png"
    )


def plot_top_players(
    results: dict[str, Any], folder: Path
) -> str:
    """Plot the highest-paid players, including ties."""
    players = results["top_players"]
    year = results["latest_year"]

    fig, ax = plt.subplots(figsize=(10, 8))

    bars = ax.barh(
        players.index,
        players / 1_000_000,
        color="seagreen",
    )

    ax.bar_label(bars, fmt="%.2f", padding=4)

    ax.set_title(
        f"Highest Recorded Player Salaries, {year}\n"
        "Top 10, including ties"
    )

    ax.set_xlabel("Salary (millions of dollars)")
    ax.set_ylabel("Player ID")
    ax.set_xlim(0, players.max() / 1_000_000 * 1.15)

    fig.tight_layout()

    return save_graph(
        fig, folder / f"highest_paid_players_{year}.png"
    )


def generate_salary_graphs(
    results: dict[str, Any],
    graph_folder: str | Path,
) -> list[str]:
    """Generate all five original baseball visualizations."""
    folder = Path(graph_folder)
    folder.mkdir(parents=True, exist_ok=True)

    with sns.axes_style("whitegrid"):
        return [
            plot_salary_distribution(results, folder),
            plot_batting_correlations(results, folder),
            plot_league_salaries(results, folder),
            plot_team_salaries(results, folder),
            plot_top_players(results, folder),
        ]
