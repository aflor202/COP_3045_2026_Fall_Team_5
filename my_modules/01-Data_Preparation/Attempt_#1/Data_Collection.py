"""Prepare and consolidate the baseball CSV data files."""

import logging
from pathlib import Path

import pandas as pd


LOGGER = logging.getLogger(__name__)
MINIMUM_YEAR = 2000
INPUT_FILENAMES = ("Batting.csv", "Fielding.csv", "Salaries.csv")
OUTPUT_FILENAME = "consolidated_data.csv"


def configure_logging() -> None:
	"""Configure application logging for normal status and error messages."""
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(levelname)s - %(message)s",
	)


def get_input_paths() -> list[Path]:
	"""Build and validate the three required input paths."""
	repository_root = Path(__file__).resolve().parents[1]
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


def identify_year_column(dataframe: pd.DataFrame, input_path: Path) -> str:
	"""Select the date or year field used to filter one input DataFrame."""
	for column_name in ("date", "year", "yearID"):
		if column_name in dataframe.columns:
			return column_name

	message = (
		f"File contains neither a date, year, nor yearID column: {input_path}"
	)
	LOGGER.error(message)
	raise ValueError(message)


def filter_by_year(dataframe: pd.DataFrame, year_column: str) -> pd.DataFrame:
	"""Return rows from the minimum year onward, excluding invalid values."""
	if year_column == "date":
		parsed_dates = pd.to_datetime(dataframe[year_column], errors="coerce")
		years = parsed_dates.dt.year
	else:
		years = pd.to_numeric(dataframe[year_column], errors="coerce")

	valid_rows = years.ge(MINIMUM_YEAR).fillna(False)
	return dataframe.loc[valid_rows].copy()


def process_input_file(input_path: Path) -> pd.DataFrame:
	"""Read, filter, and report diagnostics for one CSV file."""
	LOGGER.info("Processing file: %s", input_path)

	try:
		dataframe = pd.read_csv(input_path)
	except Exception as error:
		message = f"Unable to read input file {input_path}: {error}"
		LOGGER.error(message)
		raise OSError(message) from error

	year_column = identify_year_column(dataframe, input_path)
	filtered_dataframe = filter_by_year(dataframe, year_column)
	removed_count = len(dataframe) - len(filtered_dataframe)

	LOGGER.info(
		"Removed %d records from %s during year filtering.",
		removed_count,
		input_path.name,
	)
	LOGGER.info(
		"Filtered dimensions for %s: %d rows x %d columns.",
		input_path.name,
		filtered_dataframe.shape[0],
		filtered_dataframe.shape[1],
	)
	LOGGER.info(
		"First 5 rows from %s:\n%s",
		input_path.name,
		filtered_dataframe.head(5).to_string(index=False),
	)
	LOGGER.info(
		"Missing values by column for %s:\n%s",
		input_path.name,
		filtered_dataframe.isna().sum().to_string(),
	)
	LOGGER.info(
		"Duplicate rows in %s: %d",
		input_path.name,
		filtered_dataframe.duplicated().sum(),
	)

	return filtered_dataframe


def consolidate_data(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
	"""Combine filtered DataFrames while preserving the union of columns."""
	return pd.concat(
		dataframes,
		axis=0,
		join="outer",
		ignore_index=True,
	)


def write_output(dataframe: pd.DataFrame) -> Path:
	"""Write the consolidated DataFrame to the current working directory."""
	output_path = (Path.cwd() / OUTPUT_FILENAME).resolve()
	dataframe.to_csv(output_path, index=False)
	LOGGER.info("Wrote consolidated data to: %s", output_path)
	LOGGER.info(
		"Consolidated dimensions: %d rows x %d columns.",
		dataframe.shape[0],
		dataframe.shape[1],
	)
	return output_path


def main() -> None:
	"""Process all required inputs, consolidate them, and write the output."""
	configure_logging()

	try:
		input_paths = get_input_paths()
		filtered_dataframes = [
			process_input_file(input_path) for input_path in input_paths
		]
		consolidated_dataframe = consolidate_data(filtered_dataframes)
		write_output(consolidated_dataframe)
	except Exception:
		LOGGER.exception("Data collection failed.")
		raise


if __name__ == "__main__":
	main()