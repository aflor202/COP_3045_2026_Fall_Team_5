
"""Object-oriented PDF report generator for baseball analysis."""

from datetime import datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
)


class PDFReport:
    """Generate a formatted PDF report of baseball EDA results."""

    def __init__(self, output_path: str | Path) -> None:
        """Initialize the report destination and formatting styles."""
        self._output_path = Path(output_path).resolve()

        if self._output_path.suffix.lower() != ".pdf":
            raise ValueError("Report destination must be a PDF file.")

        self._output_path.parent.mkdir(
            parents=True, exist_ok=True
        )

        self._styles = getSampleStyleSheet()
        self._styles["BodyText"].fontSize = 10
        self._styles["BodyText"].leading = 14

        self._story = []

    @property
    def output_path(self) -> Path:
        """Return the report destination."""
        return self._output_path

    def _add_paragraph(self, text: str) -> None:
        """Add a formatted paragraph to the report."""
        self._story.append(
            Paragraph(escape(text), self._styles["BodyText"])
        )
        self._story.append(Spacer(1, 10))

    def _add_heading(self, text: str) -> None:
        """Add a section heading to the report."""
        self._story.append(
            Paragraph(escape(text), self._styles["Heading2"])
        )
        self._story.append(Spacer(1, 6))

    def _build_intro(
        self, results: dict[str, Any]
    ) -> None:
        """Build the report introduction and dataset overview."""
        salary = results["salary_analysis"]
        overview = results["overview"]

        first_year = salary["first_year"]
        latest_year = salary["latest_year"]

        self._story.append(
            Paragraph(
                f"Baseball Salaries and Performance, "
                f"{first_year}-{latest_year}",
                self._styles["Title"],
            )
        )

        self._add_paragraph(
            "Exploratory Data Analysis | COP 3045 | Team 5"
        )

        self._add_paragraph(
            f"Generated automatically: "
            f"{datetime.now():%B %d, %Y}"
        )

        self._add_heading("1. Purpose and Dataset")

        self._add_paragraph(
            "This report examines baseball salary distributions, "
            "relationships between salary and batting performance, "
            "salary differences between leagues and teams, "
            "and the highest recorded player salaries."
        )

        self._add_paragraph(
            f"The cleaned dataset contains "
            f"{overview['total_rows']:,} rows and "
            f"{overview['total_columns']} columns, with "
            f"{overview['duplicate_rows']} duplicate rows."
        )

        self._add_heading("2. Data Preparation")

        self._add_paragraph(
            "Data is loaded, merged, stored in SQLite, exported, "
            "and cleaned through reusable application classes. "
            "Missing numerical values are retained rather than "
            "replaced with estimated values."
        )

        self._add_paragraph(
            f"Salary analysis uses one observation per player, "
            f"team, and season, resulting in "
            f"{salary['salary_records']:,} salary records. "
            f"Repeated batting stints are removed before "
            f"combining batting statistics."
        )

        self._add_heading("3. Missing Data")

        missing = results["missing_values"]

        for column in ["salary", "AB", "POS", "PB", "WP", "ZR"]:
            if column in missing:
                count = missing[column]
                percent = count / overview["total_rows"] * 100

                self._add_paragraph(
                    f"{column}: {count:,} missing "
                    f"observations ({percent:.2f}%)."
                )

    def _build_summary(
        self, salary: dict[str, Any]
    ) -> dict[str, str]:
        """Create explanations for the five original salary graphs."""

        correlations = (
            salary["correlation"]["Salary"]
            .drop("Salary")
            .dropna()
        )

        if correlations.empty:
            correlation_text = (
                "No valid batting correlations were available."
            )
        else:
            strongest = correlations.abs().idxmax()
            strongest_r = correlations[strongest]

            correlation_text = (
                f"The strongest absolute Pearson correlation "
                f"with salary is {strongest} "
                f"(r = {strongest_r:.3f}). "
                f"The analysis uses "
                f"{salary['complete_count']:,} complete records. "
                f"Correlation does not establish causation."
            )

        league_text = []

        for league, row in salary["league_summary"].iterrows():
            league_text.append(
                f"{league}: mean ${row['mean']:,.2f}, "
                f"median ${row['median']:,.2f}."
            )

        teams = salary["team_summary"]["median"]
        players = salary["top_players"]
        year = salary["latest_year"]

        return {
            "salary_distribution.png": (
                f"The mean salary is "
                f"${salary['mean_salary']:,.2f}, while the "
                f"median is ${salary['median_salary']:,.2f}. "
                f"Salary skewness is "
                f"{salary['salary_skewness']:.2f}. "
                f"High earners influence the mean salary."
            ),

            "salary_batting_correlation.png": correlation_text,

            "salary_by_league.png": (
                " ".join(league_text)
                + " These comparisons do not adjust for "
                "season or player composition."
            ),

            f"median_salary_by_team_{year}.png": (
                f"{teams.idxmax()} has the highest median "
                f"salary at ${teams.max():,.2f}, while "
                f"{teams.idxmin()} has the lowest median "
                f"salary at ${teams.min():,.2f}. "
                f"This measures typical player salaries, "
                f"not total team payroll."
            ),

            f"highest_paid_players_{year}.png": (
                f"Player {players.idxmax()} has the highest "
                f"recorded salary at ${players.max():,.2f}. "
                f"The ranking includes ties at tenth place."
            ),
        }

    def _build_graphs(
        self,
        graph_paths: list[str],
        explanations: dict[str, str],
    ) -> None:
        """Insert generated visualizations and their explanations."""

        for index, graph_path in enumerate(graph_paths, start=1):
            path = Path(graph_path)

            if not path.is_file():
                raise FileNotFoundError(
                    f"Graph file not found: {path}"
                )

            self._story.append(PageBreak())

            title = path.stem.replace("_", " ").title()

            self._add_heading(
                f"Figure {index}. {title}"
            )

            width, height = ImageReader(str(path)).getSize()

            scale = min(468 / width, 440 / height)

            self._story.append(
                Image(
                    str(path),
                    width=width * scale,
                    height=height * scale,
                )
            )

            self._story.append(Spacer(1, 14))

            explanation = explanations.get(
                path.name,
                "Additional exploratory visualization of "
                "the cleaned baseball dataset.",
            )

            self._add_paragraph(explanation)

    def _build_conclusion(
        self, salary: dict[str, Any]
    ) -> None:
        """Build the limitations and conclusion sections."""

        self._story.append(PageBreak())

        self._add_heading("4. Limitations")

        self._add_paragraph(
            "The analysis describes the supplied dataset and "
            "may not represent every player or component "
            "of compensation. Missing performance records "
            "may influence the correlation results."
        )

        self._add_paragraph(
            "Salaries are not adjusted for inflation. "
            "The analysis does not control for experience, "
            "position, contract terms, or other influences "
            "on compensation. No causal claims are made."
        )

        self._add_heading("5. Conclusion")

        self._add_paragraph(
            f"The mean salary of "
            f"${salary['mean_salary']:,.2f} and median salary "
            f"of ${salary['median_salary']:,.2f} demonstrate "
            f"the influence of high earners on average salaries. "
            f"League comparisons, team comparisons, and batting "
            f"correlations provide additional insight into "
            f"baseball compensation."
        )

        self._add_heading("6. Reproducibility")

        self._add_paragraph(
            "Run python -m OOP_Workflow.main from the repository "
            "root to execute the complete object-oriented "
            "application and automatically regenerate this report."
        )

    @staticmethod
    def _page_number(canvas: Any, document: Any) -> None:
        """Add page numbers to the PDF."""
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            558, 28, f"Page {document.page}"
        )
        canvas.restoreState()

    def generate(
        self,
        non_graphical_results: dict[str, Any],
        graph_paths: list[str],
    ) -> Path:
        """Generate and save the complete PDF report."""

        if not isinstance(non_graphical_results, dict):
            raise TypeError("Analysis results must be a dictionary.")

        required = {
            "overview",
            "missing_values",
            "salary_analysis",
        }

        missing = required - non_graphical_results.keys()

        if missing:
            raise ValueError(
                f"Missing required analysis sections: {sorted(missing)}"
            )

        if not graph_paths:
            raise ValueError(
                "At least one visualization is required."
            )

        self._story = []

        salary = non_graphical_results["salary_analysis"]

        self._build_intro(non_graphical_results)

        explanations = self._build_summary(salary)

        self._build_graphs(graph_paths, explanations)

        self._build_conclusion(salary)

        try:
            document = SimpleDocTemplate(
                str(self._output_path),
                pagesize=(612, 792),
                rightMargin=54,
                leftMargin=54,
                topMargin=48,
                bottomMargin=48,
            )

            document.build(
                self._story,
                onFirstPage=self._page_number,
                onLaterPages=self._page_number,
            )

        except OSError as exc:
            raise OSError(
                f"Unable to generate PDF report: {exc}"
            ) from exc

        return self._output_path
