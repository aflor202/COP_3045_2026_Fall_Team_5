"""Unit, contract, integration, and CLI tests for the baseball analysis pipeline."""

from __future__ import annotations

from pathlib import Path
import sys

_START_DIR = (
    Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd().resolve()
)
for _candidate in (_START_DIR, *_START_DIR.parents):
    if (_candidate / "main.py").is_file() and (_candidate / "OOP_Workflow").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

import pandas as pd
import pytest

from main import main as cli_main
from OOP_Workflow.Classes.baseball_database import BaseballDatabase
from OOP_Workflow.Classes.data_cleaner import DataCleaner
from OOP_Workflow.pipeline import AnalysisPipeline, PipelineConfig, PipelineResult


def test_fail_fast_missing_raw_dir(tmp_path: Path) -> None:
    """Missing raw_data_dir raises FileNotFoundError immediately."""
    missing_dir = tmp_path / "does_not_exist"
    out_dir = tmp_path / "out"

    with pytest.raises(FileNotFoundError):
        PipelineConfig(raw_data_dir=missing_dir, output_dir=out_dir)


def test_fail_fast_missing_required_csv(
    synthetic_raw_data_dir: Path, tmp_path: Path
) -> None:
    """Missing Salaries.csv raises FileNotFoundError immediately."""
    (synthetic_raw_data_dir / "Salaries.csv").unlink()
    out_dir = tmp_path / "out"

    with pytest.raises(FileNotFoundError):
        PipelineConfig(raw_data_dir=synthetic_raw_data_dir, output_dir=out_dir)


def test_state_guards_before_prerequisite_stages(
    synthetic_raw_data_dir: Path, tmp_path: Path
) -> None:
    """Calling stages or reading outputs before prerequisites raises RuntimeError."""
    config = PipelineConfig(
        raw_data_dir=synthetic_raw_data_dir,
        output_dir=tmp_path / "out",
    )
    pipeline = AnalysisPipeline(config)

    with pytest.raises(RuntimeError):
        pipeline.clean_data()

    with pytest.raises(RuntimeError):
        pipeline.run_analysis()

    with pytest.raises(RuntimeError):
        pipeline.build_report()

    with pytest.raises(RuntimeError):
        _ = pipeline.clean_df


def test_encapsulation_clean_df_returns_defensive_copy(
    synthetic_raw_data_dir: Path, tmp_path: Path
) -> None:
    """Mutating pipeline.clean_df externally does not alter internal state."""
    config = PipelineConfig(
        raw_data_dir=synthetic_raw_data_dir,
        output_dir=tmp_path / "out",
    )
    pipeline = AnalysisPipeline(config).prepare_data().persist_and_export().clean_data()

    original_columns = list(pipeline.clean_df.columns)
    external_df = pipeline.clean_df
    del external_df["salary"]

    assert "salary" not in external_df.columns
    assert list(pipeline.clean_df.columns) == original_columns
    assert "salary" in pipeline.clean_df.columns


def test_data_cleaner_and_database_contract(
    synthetic_raw_data_dir: Path, tmp_path: Path
) -> None:
    """DataCleaner preserves 37 columns/numeric dtypes and BaseballDatabase exports cleanly."""
    config = PipelineConfig(
        raw_data_dir=synthetic_raw_data_dir,
        output_dir=tmp_path / "contract_out",
    )
    pipeline = AnalysisPipeline(config).prepare_data()
    prepared = pipeline.prepared_df

    assert prepared.shape[1] == 37
    assert (prepared["yearID"] >= 2000).all()

    db = BaseballDatabase(config.db_path)
    try:
        db.save(prepared)
        exported_path = db.export_csv(config.exported_csv_path)
    finally:
        db.close()

    assert exported_path.is_file()
    reloaded = pd.read_csv(exported_path)
    cleaned = DataCleaner().clean(reloaded)

    assert cleaned.shape[1] == 37
    assert pd.api.types.is_numeric_dtype(cleaned["salary"])
    assert pd.api.types.is_numeric_dtype(cleaned["AB"])
    assert set(DataCleaner().non_numeric_columns).issubset(cleaned.columns)


def test_end_to_end_pipeline_run(
    synthetic_raw_data_dir: Path, tmp_path: Path
) -> None:
    """AnalysisPipeline.run() generates DB, CSVs, graphs, and a valid PDF report."""
    out_dir = tmp_path / "out"
    config = PipelineConfig(
        raw_data_dir=synthetic_raw_data_dir,
        output_dir=out_dir,
    )
    result = AnalysisPipeline(config).run()

    assert isinstance(result, PipelineResult)
    assert result.raw_rows == 14  # 15 raw rows minus 1 pre-2000 row
    assert result.clean_rows == 14
    assert result.db_path.is_file() and result.db_path.stat().st_size > 0
    assert result.exported_csv_path.is_file() and result.exported_csv_path.stat().st_size > 0
    assert result.clean_csv_path.is_file() and result.clean_csv_path.stat().st_size > 0
    assert result.analysis_csv_path.is_file() and result.analysis_csv_path.stat().st_size > 0

    graph_files = list((out_dir / "graphs").glob("*.png"))
    assert result.graph_count >= 5
    assert len(graph_files) == result.graph_count
    assert all(path.is_file() and path.stat().st_size > 0 for path in result.graph_paths)

    assert result.report_path.is_file()
    assert result.report_path.stat().st_size > 1024
    with result.report_path.open("rb") as pdf_file:
        assert pdf_file.read(5) == b"%PDF-"


def test_cli_smoke_success_and_failure(
    synthetic_raw_data_dir: Path, tmp_path: Path
) -> None:
    """CLI main() returns 0 on valid args and 1 on missing raw_data_dir."""
    out_dir = tmp_path / "cli_out"
    exit_code = cli_main(
        [
            "--raw-data-dir",
            str(synthetic_raw_data_dir),
            "--output-dir",
            str(out_dir),
            "--log-level",
            "WARNING",
        ]
    )
    assert exit_code == 0
    assert (out_dir / "analysis_report.pdf").is_file()

    bad_exit_code = cli_main(
        [
            "--raw-data-dir",
            str(tmp_path / "nonexistent"),
            "--output-dir",
            str(tmp_path / "bad_out"),
        ]
    )
    assert bad_exit_code == 1
