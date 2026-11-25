"""Object-oriented EDA adapter used by the team's existing main.py.

This class delegates analysis to small reusable functions in the eda package.
It maintains the DataAnalyzer interface used by OOP_Workflow/main.py.
"""

from pathlib import Path
from typing import Any

import pandas as pd

from .eda import calculate_eda_statistics, generate_eda_graphs
from .eda.validation import validate_csv_destination, validate_dataframe


class DataAnalyzer:
    """Analyze a prepared baseball DataFrame and save its results."""

    def __init__(self, output_path: str | Path) -> None:
        """Set a CSV output path and accompanying graph folder."""
        self._output_path = validate_csv_destination(output_path)
        self._graph_folder = self._output_path.parent / "graphs"

    @property
    def output_path(self) -> Path:
        """Read-only location of the statistical summary CSV."""
        return self._output_path

    @property
    def graph_folder(self) -> Path:
        """Read-only location for generated PNG files."""
        return self._graph_folder

    def calculate_statistics(self, data: pd.DataFrame) -> dict[str, dict[str, Any]]:
        """Return nested EDA statistics and export a flattened CSV table.

        Args:
            data: Cleaned baseball data.

        Raises:
            TypeError: Input is not a pandas DataFrame.
            ValueError: Input is empty or has duplicate column names.
            OSError: Output CSV cannot be written.
        """
        validate_dataframe(data)
        results = calculate_eda_statistics(data)

        rows: list[dict[str, Any]] = []
        for section, section_data in results.items():
            for key, value in section_data.items():
                if isinstance(value, dict):
                    for metric, measurement in value.items():
                        rows.append({
                            "section": section,
                            "column": key,
                            "metric": metric,
                            "value": measurement,
                        })
                else:
                    rows.append({
                        "section": section,
                        "column": "",
                        "metric": key,
                        "value": value,
                    })
        try:
            pd.DataFrame(
                rows, columns=["section", "column", "metric", "value"]
            ).to_csv(self._output_path, index=False)
        except OSError as exc:
            raise OSError(
                f"Could not save EDA statistics to '{self._output_path}': {exc}"
            ) from exc
        return results

    def generate_graphs(self, data: pd.DataFrame) -> list[str]:
        """Save graphical EDA images and return paths for the PDF reporter."""
        validate_dataframe(data)
        return generate_eda_graphs(data, self._graph_folder)
