
"""Object-oriented interface for baseball database operations."""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


class BaseballDatabase:
    """Store baseball data in SQLite and export it to CSV."""

    def __init__(self, db_path: str | Path) -> None:
        """Initialize the database path, table name, and engine."""
        self._db_path = Path(db_path).resolve()
        self._table_name = "consolidated_data_v2"

        if self._db_path.suffix != ".db":
            raise ValueError("Database file must have a .db extension.")

        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._engine = create_engine(
            f"sqlite:///{self._db_path.as_posix()}"
        )

    @property
    def db_path(self) -> Path:
        """Return the database file location."""
        return self._db_path

    @property
    def table_name(self) -> str:
        """Return the database table name."""
        return self._table_name

    def save(self, data: pd.DataFrame) -> None:
        """Save the prepared baseball dataset to SQLite."""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        if data.empty:
            raise ValueError("Cannot save an empty DataFrame.")

        try:
            with self._engine.begin() as connection:
                data.to_sql(
                    self._table_name,
                    con=connection,
                    if_exists="replace",
                    index=False,
                )
        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Failed to save data to the database: {exc}"
            ) from exc

    def export_csv(self, output_path: str | Path) -> Path:
        """Read the database table and export it to a CSV file."""
        output_path = Path(output_path).resolve()

        if output_path.suffix.lower() != ".csv":
            raise ValueError("Output file must have a .csv extension.")

        try:
            with self._engine.connect() as connection:
                data = pd.read_sql_table(
                    self._table_name,
                    con=connection,
                )
        except (SQLAlchemyError, ValueError) as exc:
            raise RuntimeError(
                f"Failed to read the database table: {exc}"
            ) from exc

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            data.to_csv(output_path, index=False)
        except OSError as exc:
            raise OSError(
                f"Failed to export CSV to {output_path}: {exc}"
            ) from exc

        return output_path

    def close(self) -> None:
        """Release database engine resources."""
        self._engine.dispose()
