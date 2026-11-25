"""Shared validation helpers for reusable EDA functions."""

from pathlib import Path

import pandas as pd


def validate_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """Return a usable DataFrame or raise a clear exception.

    Args:
        data: A table of cleaned baseball records.

    Raises:
        TypeError: ``data`` is not a pandas DataFrame.
        ValueError: The table lacks records/columns or has duplicate column names.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"EDA expects a pandas DataFrame; received {type(data).__name__}."
        )
    if data.shape[0] == 0:
        raise ValueError("EDA cannot analyze a DataFrame with zero rows.")
    if data.shape[1] == 0:
        raise ValueError("EDA cannot analyze a DataFrame with zero columns.")
    if not data.columns.is_unique:
        raise ValueError("EDA requires unique column names; duplicates were found.")
    return data


def ensure_directory(folder: str | Path) -> Path:
    """Create an output folder if necessary and return its Path.

    Raises:
        TypeError: The folder argument is not a string or Path.
        ValueError: The folder is an empty string.
        OSError: The folder cannot be created or is actually a file.
    """
    if not isinstance(folder, (str, Path)):
        raise TypeError("Output folder must be a string or pathlib.Path.")
    if isinstance(folder, str) and not folder.strip():
        raise ValueError("Output folder cannot be blank.")
    path = Path(folder)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Cannot create output folder '{path}': {exc}") from exc
    if not path.is_dir():
        raise OSError(f"Output folder path '{path}' is not a directory.")
    return path


def validate_csv_destination(output_path: str | Path) -> Path:
    """Validate an EDA CSV destination and ensure its parent folder exists."""
    if not isinstance(output_path, (str, Path)):
        raise TypeError("CSV output path must be a string or pathlib.Path.")
    if isinstance(output_path, str) and not output_path.strip():
        raise ValueError("CSV output path cannot be blank.")
    path = Path(output_path)
    if path.suffix.lower() != ".csv":
        raise ValueError(f"EDA statistics output must be a .csv file: '{path}'.")
    ensure_directory(path.parent)
    if path.exists() and path.is_dir():
        raise ValueError(f"CSV output path '{path}' points to a directory.")
    return path
