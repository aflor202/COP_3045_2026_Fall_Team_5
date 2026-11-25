"""Reusable functions for rendering EDA visualizations to PNG files."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .validation import ensure_directory, validate_dataframe


def _save_figure(fig: plt.Figure, path: Path) -> str:
    """Save a figure, always close it, and report filesystem failures."""
    try:
        fig.savefig(path, dpi=150, bbox_inches="tight")
    except OSError as exc:
        raise OSError(f"Unable to save graph to '{path}': {exc}") from exc
    finally:
        plt.close(fig)
    return str(path)


def plot_numeric_distributions(
    data: pd.DataFrame, graph_folder: str | Path, max_columns: int = 4
) -> list[str]:
    """Save a histogram for each of the first max_columns numeric variables."""
    data = validate_dataframe(data)
    if isinstance(max_columns, bool) or not isinstance(max_columns, int) or max_columns < 1:
        raise ValueError("max_columns must be a positive integer.")
    folder = ensure_directory(graph_folder)
    numeric_data = data.select_dtypes(include="number")
    paths: list[str] = []

    for index, column in enumerate(numeric_data.columns[:max_columns], start=1):
        values = numeric_data[column].dropna()
        if values.empty:
            continue
        fig, ax = plt.subplots(figsize=(7, 4))
        try:
            ax.hist(values.to_numpy(dtype=float), bins=20, edgecolor="black")
            ax.set(title=f"Distribution of {column}", xlabel=str(column), ylabel="Count")
            fig.tight_layout()
        except Exception:
            plt.close(fig)
            raise
        paths.append(_save_figure(fig, folder / f"histogram_{index}.png"))
    return paths


def plot_missing_values(data: pd.DataFrame, graph_folder: str | Path) -> str | None:
    """Save a missing-values bar chart, or return None when none are missing."""
    data = validate_dataframe(data)
    missing = data.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        return None

    folder = ensure_directory(graph_folder)
    fig, ax = plt.subplots(figsize=(max(7, len(missing) * 0.6), 4))
    try:
        ax.bar(missing.index.astype(str), missing.values)
        ax.set(title="Missing Values by Column", xlabel="Column", ylabel="Missing rows")
        ax.tick_params(axis="x", labelrotation=45)
        fig.tight_layout()
    except Exception:
        plt.close(fig)
        raise
    return _save_figure(fig, folder / "missing_values.png")


def plot_correlation_heatmap(data: pd.DataFrame, graph_folder: str | Path) -> str | None:
    """Save a Pearson correlation heatmap when valid correlations exist."""
    data = validate_dataframe(data)
    numeric_data = data.select_dtypes(include="number")
    if len(numeric_data.columns) < 2:
        return None
    correlations = numeric_data.corr()
    if correlations.isna().all().all():
        return None

    folder = ensure_directory(graph_folder)
    size = min(max(6, len(correlations.columns) * 0.65), 14)
    fig, ax = plt.subplots(figsize=(size, size))
    try:
        heatmap = ax.imshow(correlations, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(correlations.columns)))
        ax.set_yticks(range(len(correlations.columns)))
        ax.set_xticklabels(correlations.columns, rotation=45, ha="right")
        ax.set_yticklabels(correlations.columns)
        ax.set_title("Correlation Between Numeric Columns")
        fig.colorbar(heatmap, ax=ax, label="Correlation")
        fig.tight_layout()
    except Exception:
        plt.close(fig)
        raise
    return _save_figure(fig, folder / "correlation_heatmap.png")


def generate_eda_graphs(data: pd.DataFrame, graph_folder: str | Path) -> list[str]:
    """Generate all available EDA charts and return their image paths."""
    validate_dataframe(data)
    folder = ensure_directory(graph_folder)
    paths = plot_numeric_distributions(data, folder)
    missing_path = plot_missing_values(data, folder)
    correlation_path = plot_correlation_heatmap(data, folder)
    if missing_path is not None:
        paths.append(missing_path)
    if correlation_path is not None:
        paths.append(correlation_path)
    return paths
