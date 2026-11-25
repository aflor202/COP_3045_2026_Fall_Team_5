"""CLI entry point for the baseball data analysis and PDF reporting pipeline."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from OOP_Workflow.pipeline import AnalysisPipeline, PipelineConfig

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Run the end-to-end baseball salary and performance analysis pipeline."
        )
    )
    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=PROJECT_ROOT / "my_modules" / "00-Raw_Data",
        help="Directory containing Batting.csv, Fielding.csv, and Salaries.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "OOP_Workflow" / "OOP-Outputs",
        help="Directory where database, CSVs, graphs, and PDF report are saved.",
    )
    parser.add_argument(
        "--report-filename",
        type=str,
        default="analysis_report.pdf",
        help="Filename for the generated PDF report inside --output-dir.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity level.",
    )
    return parser


def configure_logging(log_level: str) -> None:
    """Configure centralized application logging."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments, run the pipeline, and return an exit status code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.log_level)

    try:
        config = PipelineConfig(
            raw_data_dir=args.raw_data_dir,
            output_dir=args.output_dir,
            report_filename=args.report_filename,
        )
        result = AnalysisPipeline(config).run()
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as exc:
        LOGGER.error("Pipeline failed: %s", exc)
        return 1

    LOGGER.info(
        "Analysis complete: %d prepared rows, %d clean rows, %d graphs. Report: %s",
        result.raw_rows,
        result.clean_rows,
        result.graph_count,
        result.report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
