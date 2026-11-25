
"""Main entry point for the baseball data analysis application."""

from pathlib import Path

import pandas as pd

from OOP_Workflow.Classes.data_preparer import DataPreparer
from OOP_Workflow.Classes.baseball_database import BaseballDatabase
from OOP_Workflow.Classes.data_cleaner import DataCleaner
from OOP_Workflow.Classes.data_analyzer import DataAnalyzer
from OOP_Workflow.Classes.pdf_report import PDFReport


def main() -> None:
    """Execute the complete baseball data analysis workflow."""

    project_path = Path(__file__).resolve().parent.parent
    raw_data_path = project_path / "my_modules" / "00-Raw_Data"
    output_path = project_path / "OOP_Workflow" / "OOP-Outputs"

    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize the classes
    preparer = DataPreparer(raw_data_path)
    database = BaseballDatabase(output_path / "merged_database.db")
    cleaner = DataCleaner()
    analyzer = DataAnalyzer(output_path / "analysis_results.csv")
    report = PDFReport(output_path / "analysis_report.pdf")

    # Prepare the data
    prepared_data = preparer.prepare()

    # Store and export the data
    try:
        database.save(prepared_data)
        exported_data_path = database.export_csv(
            output_path / "exported_data.csv"
        )
    finally:
        database.close()

    exported_data = pd.read_csv(exported_data_path)

    # Clean the data
    cleaned_data = cleaner.clean(exported_data)

    cleaned_data.to_csv(
        output_path / "clean_data.csv",
        index=False,
    )

    # Analyze the data
    non_graphical_results = analyzer.calculate_statistics(cleaned_data)
    graph_paths = analyzer.generate_graphs(cleaned_data)

    # Generate the PDF report
    report_path = report.generate(
        non_graphical_results,
        graph_paths,
    )

    print(f"Analysis report generated at: {report_path}")


if __name__ == "__main__":
    main()
