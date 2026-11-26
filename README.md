# Baseball Salaries and Performance Analysis Pipeline

**COP 3045 — Python II (Fall 2026, Team 5)**

An object-oriented Python data analysis and automated PDF reporting pipeline for Lahman-style MLB batting, fielding, and salary datasets (`yearID >= 2000`). The pipeline consolidates raw CSV files, executes a SQLite persistence roundtrip, cleans and validates records, computes generic and baseball-specific exploratory data analysis (EDA) metrics, renders matplotlib/seaborn figures headlessly, and builds a formatted multi-page ReportLab PDF report.

---

## Architecture & Team Structure

The refactored application follows a **Central Pipeline Facade** pattern with strict one-way dependencies:

```text
OOP_Workflow/main.py  (CLI / argparse / logging / Agg backend)
   │
   ▼
OOP_Workflow/pipeline.py  (PipelineConfig, PipelineResult, AnalysisPipeline)
   │
   ▼
OOP_Workflow/Classes/*  (Domain & stage components)
   ├── DataPreparer + preparation/collection.py
   ├── BaseballDatabase
   ├── DataCleaner
   ├── DataAnalyzer + eda/*
   └── PDFReport
```

| Responsibility Area | Stage / Scope | Implementation Files |
| :--- | :--- | :--- |
| **Data Preparation, Storage & Cleaning** | Load & outer-merge raw CSVs (`yearID >= 2000`), SQLite roundtrip, deduplication, whitespace trimming, numeric coercion | `OOP_Workflow/Classes/data_preparer.py`, `OOP_Workflow/Classes/preparation/collection.py`, `OOP_Workflow/Classes/baseball_database.py`, `OOP_Workflow/Classes/data_cleaner.py` |
| **Exploratory Data Analysis** | Input validation, descriptive statistics, missingness, batting-salary Pearson correlations, league/team/top-player summaries | `OOP_Workflow/Classes/data_analyzer.py`, `OOP_Workflow/Classes/eda/validation.py`, `OOP_Workflow/Classes/eda/non_graphical.py`, `OOP_Workflow/Classes/eda/salary_analysis.py` |
| **Visualizations & PDF Reporting** | Headless PNG generation (generic EDA + 5 baseball salary charts) and ReportLab PDF compilation | `OOP_Workflow/Classes/eda/graphical.py`, `OOP_Workflow/Classes/eda/salary_graphs.py`, `OOP_Workflow/Classes/pdf_report.py` |
| **OOP Orchestration, CLI, Env & QA** | `PipelineConfig` / `AnalysisPipeline` facade, `argparse` CLI, reproducible `environment.yml`, and `pytest` suite | `OOP_Workflow/pipeline.py`, `OOP_Workflow/main.py`, `environment.yml`, `pytest.ini`, `tests/conftest.py`, `tests/test_pipeline.py` |

---

## Repository Layout

```text
COP_3045_2026_Fall_Team_5/
├── environment.yml                      # Reproducible Conda environment (COP3045)
├── pytest.ini                           # Pytest discovery & pythonpath configuration
├── README.md
├── OOP_Workflow/
│   ├── __init__.py
│   ├── main.py                          # CLI entry point
│   ├── pipeline.py                      # PipelineConfig, PipelineResult, AnalysisPipeline
│   └── Classes/
│       ├── __init__.py
│       ├── data_preparer.py
│       ├── baseball_database.py
│       ├── data_cleaner.py
│       ├── data_analyzer.py
│       ├── pdf_report.py
│       ├── preparation/                 # Reusable CSV loading & merge helpers
│       └── eda/                         # Validation, non-graphical/graphical EDA, salary modules
├── tests/
│   ├── conftest.py                      # Headless Agg setup & synthetic_raw_data_dir fixture
│   └── test_pipeline.py                 # Unit, contract, integration, and CLI tests
└── my_modules/
    ├── 00-Raw_Data/                     # Default input CSVs (Batting.csv, Fielding.csv, Salaries.csv)
    ├── 01-Data_Preparation/             # Legacy preparation scripts & notes
    ├── 02-SQL_Database/                 # Legacy SQLite scripts
    ├── 03-Data cleaning/                # Legacy cleaning script
    └── 04-EDA/                          # Legacy procedural EDA & PDF scripts
```

---

## Environment Setup (Conda)

Create and activate the Conda environment from `environment.yml` (`conda-forge` + `nodefaults`, Python 3.14):

```bash
conda env create -f environment.yml
conda activate COP3045
```

To update an existing `COP3045` environment cleanly:

```bash
conda env update -n COP3045 -f environment.yml --prune
```

---

## Usage (CLI & Module Entry Point)

Run the full pipeline from inside `OOP_Workflow/`, from the repository root, or as a Python module:

```bash
cd OOP_Workflow
python main.py
# or from the repository root:
python OOP_Workflow/main.py
python -m OOP_Workflow.main
```

### CLI Options

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--raw-data-dir` | `my_modules/00-Raw_Data` | Directory containing `Batting.csv`, `Fielding.csv`, and `Salaries.csv` |
| `--output-dir` | `OOP_Workflow/OOP-Outputs` | Output directory for the SQLite DB, CSVs, PNG charts, and PDF report |
| `--report-filename` | `analysis_report.pdf` | Filename for the generated PDF inside `--output-dir` |
| `--log-level` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

Example with custom paths and logging:

```bash
python OOP_Workflow/main.py --raw-data-dir my_modules/00-Raw_Data --output-dir OOP_Workflow/OOP-Outputs --report-filename baseball_report.pdf --log-level DEBUG
```

### Generated Output Artifacts

All generated artifacts are written into `--output-dir` (default `OOP_Workflow/OOP-Outputs/`):

- `merged_database.db` — SQLite database containing table `consolidated_data_v2`
- `exported_data.csv` — Raw table export from SQLite
- `clean_data.csv` — Deduplicated, trimmed, and type-coerced dataset (37 columns)
- `analysis_results.csv` — Flattened generic EDA statistics table
- `graphs/*.png` — Generic EDA charts (`histogram_*.png`, `missing_values.png`, `correlation_heatmap.png`) plus 5 baseball salary visualizations (`salary_distribution.png`, `salary_batting_correlation.png`, `salary_by_league.png`, `median_salary_by_team_<year>.png`, `highest_paid_players_<year>.png`)
- `analysis_report.pdf` (or custom `--report-filename`) — Formatted multi-page PDF report

---

## Testing & Validation

Run the full automated `pytest` suite:

```bash
python -m pytest -v
```

What the suite verifies (`tests/test_pipeline.py`):
- **Fail-fast config validation:** Missing `--raw-data-dir` or missing required raw CSV files raise `FileNotFoundError` at initialization.
- **Stage-order state guards:** Calling `clean_data()`, `run_analysis()`, or `build_report()`, or accessing `clean_df` before prerequisite stages raises `RuntimeError`.
- **Encapsulation:** Mutating the DataFrame returned by `pipeline.clean_df` does not alter internal pipeline state.
- **Stage contracts:** `DataCleaner` preserves the expected 37-column schema and numeric dtypes, and `BaseballDatabase` persists, exports, and closes cleanly.
- **Headless end-to-end integration:** `AnalysisPipeline.run()` produces non-empty SQLite/CSV artifacts, `>= 5` PNG graphs, and a valid `%PDF-` report (`> 1024` bytes) under `Agg` backend.
- **CLI exit codes:** `main()` returns `0` on valid inputs and `1` on missing input paths.
