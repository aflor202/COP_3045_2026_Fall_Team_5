"""Central pipeline facade and configuration for the baseball analysis workflow."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from time import perf_counter
from typing import Any, Self

import matplotlib

matplotlib.use("Agg")

import pandas as pd

from OOP_Workflow.Classes.baseball_database import BaseballDatabase
from OOP_Workflow.Classes.data_analyzer import DataAnalyzer
from OOP_Workflow.Classes.data_cleaner import DataCleaner
from OOP_Workflow.Classes.data_preparer import DataPreparer
from OOP_Workflow.Classes.pdf_report import PDFReport
from OOP_Workflow.Classes.preparation.collection import INPUT_FILENAMES

LOGGER = logging.getLogger(__name__)


def _validate_raw_data_dir(raw_data_dir: Path) -> Path:
    """Validate that raw_data_dir exists and contains all required raw CSVs."""
    resolved = Path(raw_data_dir).resolve()
    if not resolved.is_dir():
        raise FileNotFoundError(
            f"Raw data directory does not exist: {resolved}"
        )

    for filename in INPUT_FILENAMES:
        csv_path = resolved / filename
        if not csv_path.is_file():
            raise FileNotFoundError(
                f"Required raw data file not found: {csv_path}"
            )

    return resolved


def _validate_filename(filename: str, expected_suffix: str, label: str) -> str:
    """Ensure a configured output filename is non-empty and has the right suffix."""
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError(f"{label} must be a non-empty filename.")
    cleaned = filename.strip()
    if Path(cleaned).name != cleaned:
        raise ValueError(f"{label} must be a filename, not a path: {filename}")
    if Path(cleaned).suffix.lower() != expected_suffix:
        raise ValueError(
            f"{label} must end with '{expected_suffix}': {filename}"
        )
    return cleaned


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable configuration for an end-to-end baseball analysis run."""

    raw_data_dir: Path
    output_dir: Path
    db_filename: str = "merged_database.db"
    exported_csv_filename: str = "exported_data.csv"
    clean_csv_filename: str = "clean_data.csv"
    analysis_csv_filename: str = "analysis_results.csv"
    report_filename: str = "analysis_report.pdf"

    def __post_init__(self) -> None:
        """Validate paths and filenames at construction time."""
        validated_raw = _validate_raw_data_dir(self.raw_data_dir)
        resolved_output = Path(self.output_dir).resolve()
        if resolved_output.exists() and not resolved_output.is_dir():
            raise ValueError(
                f"Output path exists and is not a directory: {resolved_output}"
            )

        object.__setattr__(self, "raw_data_dir", validated_raw)
        object.__setattr__(self, "output_dir", resolved_output)
        object.__setattr__(
            self,
            "db_filename",
            _validate_filename(self.db_filename, ".db", "db_filename"),
        )
        object.__setattr__(
            self,
            "exported_csv_filename",
            _validate_filename(
                self.exported_csv_filename, ".csv", "exported_csv_filename"
            ),
        )
        object.__setattr__(
            self,
            "clean_csv_filename",
            _validate_filename(
                self.clean_csv_filename, ".csv", "clean_csv_filename"
            ),
        )
        object.__setattr__(
            self,
            "analysis_csv_filename",
            _validate_filename(
                self.analysis_csv_filename, ".csv", "analysis_csv_filename"
            ),
        )
        object.__setattr__(
            self,
            "report_filename",
            _validate_filename(self.report_filename, ".pdf", "report_filename"),
        )

    @property
    def db_path(self) -> Path:
        """Read-only SQLite database destination path."""
        return self.output_dir / self.db_filename

    @property
    def exported_csv_path(self) -> Path:
        """Read-only exported CSV destination path."""
        return self.output_dir / self.exported_csv_filename

    @property
    def clean_csv_path(self) -> Path:
        """Read-only cleaned CSV destination path."""
        return self.output_dir / self.clean_csv_filename

    @property
    def analysis_csv_path(self) -> Path:
        """Read-only EDA statistics CSV destination path."""
        return self.output_dir / self.analysis_csv_filename

    @property
    def report_path(self) -> Path:
        """Read-only PDF report destination path."""
        return self.output_dir / self.report_filename


@dataclass(frozen=True)
class PipelineResult:
    """Immutable summary of generated artifacts and row/graph counts."""

    db_path: Path
    exported_csv_path: Path
    clean_csv_path: Path
    analysis_csv_path: Path
    graph_paths: tuple[Path, ...]
    report_path: Path
    raw_rows: int
    clean_rows: int
    graph_count: int


class AnalysisPipeline:
    """Facade orchestrating data preparation, storage, cleaning, EDA, and PDF reporting."""

    def __init__(self, config: PipelineConfig) -> None:
        """Validate configuration, create output directory, and initialize stage state."""
        if not isinstance(config, PipelineConfig):
            raise TypeError("config must be a PipelineConfig instance.")

        _validate_raw_data_dir(config.raw_data_dir)
        config.output_dir.mkdir(parents=True, exist_ok=True)

        self._config = config
        self._prepared_df: pd.DataFrame | None = None
        self._exported_csv_path: Path | None = None
        self._clean_df: pd.DataFrame | None = None
        self._analysis_results: dict[str, dict[str, Any]] | None = None
        self._graph_paths: list[str] = []
        self._report_path: Path | None = None

    @property
    def config(self) -> PipelineConfig:
        """Return the immutable pipeline configuration."""
        return self._config

    @property
    def prepared_df(self) -> pd.DataFrame:
        """Return a copy of the merged DataFrame from Stage 1."""
        if self._prepared_df is None:
            raise RuntimeError(
                "Prepared data is unavailable; call prepare_data() first."
            )
        return self._prepared_df.copy()

    @property
    def clean_df(self) -> pd.DataFrame:
        """Return a copy of the cleaned DataFrame."""
        if self._clean_df is None:
            raise RuntimeError(
                "Clean data is unavailable; call clean_data() first."
            )
        return self._clean_df.copy()

    @property
    def analysis_results(self) -> dict[str, dict[str, Any]]:
        """Return a shallow copy of the computed EDA results dictionary."""
        if self._analysis_results is None:
            raise RuntimeError(
                "Analysis results are unavailable; call run_analysis() first."
            )
        return dict(self._analysis_results)

    @property
    def graph_paths(self) -> tuple[Path, ...]:
        """Return immutable Paths to all generated visualization PNGs."""
        if not self._graph_paths:
            raise RuntimeError(
                "Graph paths are unavailable; call run_analysis() first."
            )
        return tuple(Path(path) for path in self._graph_paths)

    @property
    def report_path(self) -> Path:
        """Return the generated PDF report path."""
        if self._report_path is None:
            raise RuntimeError(
                "Report path is unavailable; call build_report() first."
            )
        return self._report_path

    def prepare_data(self) -> Self:
        """Stage 1: Load, filter, and merge raw baseball CSV files."""
        start = perf_counter()
        LOGGER.info("Starting data preparation from %s", self._config.raw_data_dir)
        preparer = DataPreparer(self._config.raw_data_dir)
        self._prepared_df = preparer.prepare()
        LOGGER.info(
            "Data preparation completed in %.2fs (%d rows, %d columns).",
            perf_counter() - start,
            self._prepared_df.shape[0],
            self._prepared_df.shape[1],
        )
        return self

    def persist_and_export(self) -> Self:
        """Stage 2: Persist prepared data to SQLite and export to CSV."""
        if self._prepared_df is None:
            raise RuntimeError(
                "Cannot persist data before prepare_data() has been executed."
            )

        start = perf_counter()
        LOGGER.info("Persisting prepared data to SQLite at %s", self._config.db_path)
        database = BaseballDatabase(self._config.db_path)
        try:
            database.save(self._prepared_df)
            self._exported_csv_path = database.export_csv(
                self._config.exported_csv_path
            )
        finally:
            database.close()

        LOGGER.info(
            "Database save and CSV export completed in %.2fs -> %s",
            perf_counter() - start,
            self._exported_csv_path,
        )
        return self

    def clean_data(self) -> Self:
        """Stage 3: Clean exported (or prepared) data and write clean CSV."""
        if self._prepared_df is None:
            raise RuntimeError(
                "Cannot clean data before prepare_data() has been executed."
            )

        start = perf_counter()
        if self._exported_csv_path is not None and self._exported_csv_path.is_file():
            LOGGER.info("Loading exported CSV for cleaning: %s", self._exported_csv_path)
            source_df = pd.read_csv(self._exported_csv_path, low_memory=False)
        else:
            LOGGER.info("Cleaning in-memory prepared DataFrame.")
            source_df = self._prepared_df.copy()

        cleaner = DataCleaner()
        cleaned = cleaner.clean(source_df)
        cleaned.to_csv(self._config.clean_csv_path, index=False)
        self._clean_df = cleaned

        LOGGER.info(
            "Data cleaning completed in %.2fs (%d rows, %d columns) -> %s",
            perf_counter() - start,
            self._clean_df.shape[0],
            self._clean_df.shape[1],
            self._config.clean_csv_path,
        )
        return self

    def run_analysis(self) -> Self:
        """Stage 4: Run non-graphical statistics and generate visualizations."""
        if self._clean_df is None:
            raise RuntimeError(
                "Cannot run analysis before clean_data() has been executed."
            )

        start = perf_counter()
        LOGGER.info(
            "Running exploratory data analysis -> %s",
            self._config.analysis_csv_path,
        )
        analyzer = DataAnalyzer(self._config.analysis_csv_path)
        self._analysis_results = analyzer.calculate_statistics(self._clean_df)
        self._graph_paths = analyzer.generate_graphs(self._clean_df)

        LOGGER.info(
            "EDA completed in %.2fs (%d graphs generated).",
            perf_counter() - start,
            len(self._graph_paths),
        )
        return self

    def build_report(self) -> Path:
        """Stage 5: Render the final PDF report from EDA results and charts."""
        if self._analysis_results is None or not self._graph_paths:
            raise RuntimeError(
                "Cannot build PDF report before run_analysis() has been executed."
            )

        start = perf_counter()
        LOGGER.info("Generating PDF report at %s", self._config.report_path)
        report = PDFReport(self._config.report_path)
        self._report_path = report.generate(
            self._analysis_results,
            self._graph_paths,
        )
        LOGGER.info(
            "PDF report completed in %.2fs -> %s",
            perf_counter() - start,
            self._report_path,
        )
        return self._report_path

    def run(self) -> PipelineResult:
        """Execute all pipeline stages sequentially and return artifact summary."""
        pipeline_start = perf_counter()
        LOGGER.info("Starting end-to-end baseball analysis pipeline.")

        self.prepare_data()
        self.persist_and_export()
        self.clean_data()
        self.run_analysis()
        report_path = self.build_report()

        assert self._prepared_df is not None
        assert self._clean_df is not None
        assert self._exported_csv_path is not None

        result = PipelineResult(
            db_path=self._config.db_path,
            exported_csv_path=self._exported_csv_path,
            clean_csv_path=self._config.clean_csv_path,
            analysis_csv_path=self._config.analysis_csv_path,
            graph_paths=tuple(Path(path) for path in self._graph_paths),
            report_path=report_path,
            raw_rows=int(len(self._prepared_df)),
            clean_rows=int(len(self._clean_df)),
            graph_count=len(self._graph_paths),
        )

        LOGGER.info(
            "Pipeline finished successfully in %.2fs (report=%s, graphs=%d).",
            perf_counter() - pipeline_start,
            result.report_path,
            result.graph_count,
        )
        return result
