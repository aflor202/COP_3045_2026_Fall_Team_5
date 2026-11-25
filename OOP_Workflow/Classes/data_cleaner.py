
"""Object-oriented interface for baseball data cleaning."""

import pandas as pd


class DataCleaner:
    """Clean and prepare baseball data for exploratory analysis."""

    def __init__(self) -> None:
        """Initialize the columns excluded from numeric conversion."""
        self._non_numeric_columns = {
            "playerID",
            "teamID",
            "lgID",
            "POS",
        }

    @property
    def non_numeric_columns(self) -> frozenset[str]:
        """Return the protected non-numeric column names."""
        return frozenset(self._non_numeric_columns)

    def _validate_data(self, data: pd.DataFrame) -> None:
        """Validate the input DataFrame."""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        if data.empty:
            raise ValueError("Cannot clean an empty DataFrame.")

        if data.columns.has_duplicates:
            raise ValueError("DataFrame contains duplicate column names.")

    def _remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicate records."""
        return data.drop_duplicates()

    def _clean_text(self, data: pd.DataFrame) -> pd.DataFrame:
        """Trim text values and replace blank strings with missing values."""
        for column in data.select_dtypes(
            include=["object", "string"]
        ).columns:
            data[column] = data[column].str.strip().replace("", pd.NA)

        return data

    def _convert_numeric_columns(
        self, data: pd.DataFrame
    ) -> pd.DataFrame:
        """Convert numerical columns while preserving missing values."""
        for column in data.columns:
            if column not in self._non_numeric_columns:
                data[column] = pd.to_numeric(
                    data[column],
                    errors="coerce",
                )

        return data

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """Execute the complete data cleaning workflow."""
        self._validate_data(data)

        cleaned_data = data.copy()
        cleaned_data.columns = cleaned_data.columns.str.strip()

        self._validate_data(cleaned_data)

        print("Missing values by column:")
        print(cleaned_data.isna().sum())

        print("\nDuplicate rows:", cleaned_data.duplicated().sum())

        print("\nData types:")
        print(cleaned_data.dtypes)

        cleaned_data = self._remove_duplicates(cleaned_data)
        cleaned_data = self._clean_text(cleaned_data)
        cleaned_data = self._convert_numeric_columns(cleaned_data)

        return cleaned_data.reset_index(drop=True)
