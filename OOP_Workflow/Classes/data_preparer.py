
"""Object-oriented interface for baseball data preparation."""

from pathlib import Path

import pandas as pd

from .preparation.collection import (
    INPUT_FILENAMES,
    process_input_file,
    identify_join_columns,
    merge_dataframes,
    filter_missing_salary,
)


class DataPreparer:
    """Load, validate, and combine raw baseball datasets."""

    def __init__(self, raw_data_path: str | Path) -> None:
        """Initialize the directory containing the raw datasets."""
        self._raw_data_path = Path(raw_data_path).resolve()

        if not self._raw_data_path.is_dir():
            raise NotADirectoryError(
                f"Invalid raw data directory: {self._raw_data_path}"
            )

    @property
    def raw_data_path(self) -> Path:
        """Return the raw data directory."""
        return self._raw_data_path

    def _get_input_paths(self) -> list[Path]:
        """Locate and validate the required CSV files."""
        input_paths = [
            self._raw_data_path / filename
            for filename in INPUT_FILENAMES
        ]

        for path in input_paths:
            if not path.is_file():
                raise FileNotFoundError(
                    f"Required CSV file not found: {path}"
                )

        return input_paths

    def prepare(self) -> pd.DataFrame:
        """Load, process, and merge the baseball datasets."""
        input_paths = self._get_input_paths()

        dataframes = [
            process_input_file(path)
            for path in input_paths
        ]

        join_columns = identify_join_columns(dataframes)

        merged_data = merge_dataframes(
            dataframes,
            input_paths,
            join_columns,
        )

        prepared_data = filter_missing_salary(merged_data)

        if prepared_data.empty:
            raise ValueError(
                "No valid observations remain after data preparation."
            )

        return prepared_data
