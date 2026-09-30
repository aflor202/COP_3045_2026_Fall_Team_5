"""Prepare, validate, and merge the three baseball data files."""

import logging
from pathlib import Path
from typing import Final

import pandas as pd


LOGGER = logging.getLogger(__name__)
MINIMUM_YEAR: Final[int] = 2000
INPUT_FILENAMES: Final[tuple[str, str, str]] = (
    "Batting.csv",
    "Fielding.csv",
    "Salaries.csv",
)
OUTPUT_FILENAME: Final[str] = "consolidated_data_v2.csv"
JOIN_COLUMNS: Final[tuple[str, str, str, str]] = (
    "playerID",
    "yearID",
    "teamID",
    "lgID",
)
IDENTIFIER_COLUMNS: Final[set[str]] = {
    "playerID",
    "yearID",
    "stint",
    "teamID",
    "lgID",
}


def configure_logging() -> None:
    """Configure logging for status, validation, and diagnostic messages."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def get_input_paths() -> list[Path]:
    """Resolve and validate the three required raw-data file paths."""
    repository_root = Path(__file__).resolve().parents[2]
    input_directory = repository_root / "00-Raw_Data"
    input_paths = [
        (input_directory / filename).resolve()
        for filename in INPUT_FILENAMES
    ]

    for input_path in input_paths:
        if not input_path.exists():
            message = f"Input file does not exist: {input_path}"
            LOGGER.error(message)
            raise FileNotFoundError(message)
        if not input_path.is_file():
            message = f"Input path is not a file: {input_path}"
            LOGGER.error(message)
            raise ValueError(message)

    return input_paths


def normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize labels and values while preserving missing values."""
    normalized = dataframe.copy()
    normalized.columns = normalized.columns.astype(str).str.strip()

    text_columns = normalized.select_dtypes(include=["object", "string"]).columns
    for column_name in text_columns:
        normalized[column_name] = normalized[column_name].astype("string").str.strip()

    for column_name in normalized.columns:
        if column_name in IDENTIFIER_COLUMNS or column_name == "yearID":
            continue
        if not pd.api.types.is_object_dtype(normalized[column_name]):
            continue

        numeric_values = pd.to_numeric(normalized[column_name], errors="coerce")
        non_missing_count = normalized[column_name].notna().sum()
        numeric_count = numeric_values.notna().sum()
        if non_missing_count > 0 and numeric_count == non_missing_count:
            normalized[column_name] = numeric_values

    return normalized


def log_initial_summary(dataframe: pd.DataFrame, input_path: Path) -> None:
    """Log the first ten records and the columns available in one source."""
    LOGGER.info(
        "First 10 observations from %s:\n%s",
        input_path.name,
        dataframe.head(10).to_string(index=False),
    )
    LOGGER.info("Columns in %s: %s", input_path.name, list(dataframe.columns))


def filter_by_year(dataframe: pd.DataFrame, input_path: Path) -> pd.DataFrame:
    """Exclude invalid years and records earlier than the minimum year."""
    if "yearID" not in dataframe.columns:
        message = f"Required yearID column is missing from {input_path}"
        LOGGER.error(message)
        raise ValueError(message)

    parsed_years = pd.to_numeric(dataframe["yearID"], errors="coerce")
    valid_rows = parsed_years.ge(MINIMUM_YEAR).fillna(False)
    filtered = dataframe.loc[valid_rows].copy()
    filtered["yearID"] = parsed_years.loc[valid_rows].astype("Int64")

    removed_count = len(dataframe) - len(filtered)
    invalid_year_count = parsed_years.isna().sum()
    LOGGER.info(
        "Removed %d records from %s during year filtering (%d invalid/unparseable years).",
        removed_count,
        input_path.name,
        invalid_year_count,
    )
    return filtered


def remove_duplicate_rows(
    dataframe: pd.DataFrame,
    input_path: Path,
) -> pd.DataFrame:
    """Remove exact duplicate records and log how many were eliminated."""
    duplicate_count = int(dataframe.duplicated().sum())
    LOGGER.info("Duplicate rows before removal in %s: %d", input_path.name, duplicate_count)
    return dataframe.drop_duplicates().reset_index(drop=True)


def log_outliers(dataframe: pd.DataFrame, input_path: Path) -> None:
    """Detect numeric IQR outliers and log them without deleting records."""
    numeric_columns = dataframe.select_dtypes(include=["number"]).columns
    outlier_counts: dict[str, int] = {}

    for column_name in numeric_columns:
        if column_name in {"yearID", "stint"}:
            continue
        values = dataframe[column_name].dropna()
        if values.empty:
            continue
        first_quartile = values.quantile(0.25)
        third_quartile = values.quantile(0.75)
        interquartile_range = third_quartile - first_quartile
        if interquartile_range == 0:
            continue
        lower_bound = first_quartile - (1.5 * interquartile_range)
        upper_bound = third_quartile + (1.5 * interquartile_range)
        count = int(((values < lower_bound) | (values > upper_bound)).sum())
        if count:
            outlier_counts[column_name] = count

    LOGGER.info("IQR outliers detected in %s (retained): %s", input_path.name, outlier_counts or "none")


def process_input_file(input_path: Path) -> pd.DataFrame:
    """Read, clean, filter, and diagnose one input file."""
    LOGGER.info("Processing file: %s", input_path)
    try:
        dataframe = pd.read_csv(input_path, low_memory=False)
    except (OSError, pd.errors.ParserError) as error:
        message = f"Unable to read input file {input_path}: {error}"
        LOGGER.error(message)
        raise OSError(message) from error

    dataframe = normalize_dataframe(dataframe)
    log_initial_summary(dataframe, input_path)
    filtered_dataframe = filter_by_year(dataframe, input_path)
    filtered_dataframe = remove_duplicate_rows(filtered_dataframe, input_path)
    log_outliers(filtered_dataframe, input_path)

    LOGGER.info(
        "Filtered dimensions for %s: %d rows x %d columns.",
        input_path.name,
        filtered_dataframe.shape[0],
        filtered_dataframe.shape[1],
    )
    LOGGER.info(
        "First 5 filtered rows from %s:\n%s",
        input_path.name,
        filtered_dataframe.head(5).to_string(index=False),
    )
    LOGGER.info(
        "Missing values by column for %s:\n%s",
        input_path.name,
        filtered_dataframe.isna().sum().to_string(),
    )
    return filtered_dataframe


def identify_join_columns(dataframes: list[pd.DataFrame]) -> list[str]:
    """Infer and validate the shared composite key for the three sources."""
    shared_columns = set(dataframes[0].columns)
    for dataframe in dataframes[1:]:
        shared_columns.intersection_update(dataframe.columns)
    LOGGER.info("Columns shared by all input files: %s", sorted(shared_columns))

    missing_join_columns = [
        column_name
        for column_name in JOIN_COLUMNS
        if column_name not in shared_columns
    ]
    if missing_join_columns:
        message = f"Cannot infer the required composite key; missing: {missing_join_columns}"
        LOGGER.error(message)
        raise ValueError(message)

    LOGGER.info("Using composite join key: %s", list(JOIN_COLUMNS))
    return list(JOIN_COLUMNS)


def log_duplicate_keys(dataframe: pd.DataFrame, key_columns: list[str], label: str) -> None:
    """Report repeated composite keys that may expand merge results."""
    duplicate_key_count = int(dataframe.duplicated(subset=key_columns).sum())
    LOGGER.info("Duplicate composite-key rows in %s: %d", label, duplicate_key_count)


def merge_dataframes(
    dataframes: list[pd.DataFrame],
    input_paths: list[Path],
    key_columns: list[str],
) -> pd.DataFrame:
    """Full-outer merge all filtered sources and report unmatched records."""
    merged_dataframe = dataframes[0]
    log_duplicate_keys(merged_dataframe, key_columns, input_paths[0].name)

    for dataframe, input_path in zip(dataframes[1:], input_paths[1:]):
        log_duplicate_keys(dataframe, key_columns, input_path.name)
        merge_indicator = "_merge_status"
        merged_dataframe = merged_dataframe.merge(
            dataframe,
            how="outer",
            on=key_columns,
            suffixes=("_left", "_right"),
            indicator=merge_indicator,
            validate="many_to_many",
        )
        LOGGER.info(
            "Merge with %s produced %d rows x %d columns; unmatched records: %s",
            input_path.name,
            merged_dataframe.shape[0],
            merged_dataframe.shape[1] - 1,
            merged_dataframe[merge_indicator].value_counts().to_dict(),
        )
        merged_dataframe = merged_dataframe.drop(columns=merge_indicator)

    return merged_dataframe


def write_output(dataframe: pd.DataFrame) -> Path:
    """Write the merged data to the current working directory."""
    output_path = (Path.cwd() / OUTPUT_FILENAME).resolve()
    dataframe.to_csv(output_path, index=False)
    LOGGER.info("Final output path: %s", output_path)
    LOGGER.info(
        "Final consolidated dimensions: %d rows x %d columns.",
        dataframe.shape[0],
        dataframe.shape[1],
    )
    return output_path


def filter_missing_salary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove observations without salary data."""
    if "salary" not in dataframe.columns:
        raise ValueError("Merged DataFrame is missing the salary column.")

    valid_salary = dataframe["salary"].notna()
    removed_count = int((~valid_salary).sum())

    LOGGER.info(
        "Removed %d observations without salary data.",
        removed_count,
    )

    return dataframe.loc[valid_salary].copy()


def main() -> None:
    """Run validation, filtering, merging, and output generation."""
    configure_logging()
    try:
        input_paths = get_input_paths()
        filtered_dataframes = [
            process_input_file(input_path) for input_path in input_paths
        ]
        join_columns = identify_join_columns(filtered_dataframes)
        consolidated_dataframe = merge_dataframes(
            filtered_dataframes,
            input_paths,
            join_columns,
        )
        consolidated_dataframe = filter_missing_salary(consolidated_dataframe)
        write_output(consolidated_dataframe)
    except Exception:
        LOGGER.exception("Data collection failed.")
        raise


if __name__ == "__main__":
    main()
