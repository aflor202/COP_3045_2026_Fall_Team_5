from pathlib import Path
from datetime import datetime
import runpy

import matplotlib

# Generate graphs without opening windows.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
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

base_dir = Path(__file__).resolve().parent.parent
report_dir = base_dir / "reports"
report_dir.mkdir(exist_ok=True)

# Run the existing analysis and regenerate its graphs.
graph_script = Path(__file__).resolve().parent / "graphical_eda.py"

original_show = plt.show
try:
    plt.show = lambda *args, **kwargs: None
    results = runpy.run_path(str(graph_script))
finally:
    plt.show = original_show
    plt.close("all")

# Reuse the data and results calculated by the graph script.
df = results["df"]
salary_data = results["salary_data"]
complete = results["complete"]
correlation = results["correlation"]
league_summary = results["league_summary"]
team_summary = results["team_summary"]
top_players = results["top_players"]
latest_year = results["latest_year"]
graph_dir = results["output_dir"]

first_year = int(df["yearID"].min())
last_year = int(df["yearID"].max())

pdf_path = report_dir / "eda_report.pdf"

styles = getSampleStyleSheet()
styles["BodyText"].fontSize = 10
styles["BodyText"].leading = 14

story = []


def paragraph(text):
    story.append(Paragraph(text, styles["BodyText"]))
    story.append(Spacer(1, 10))


def heading(text):
    story.append(Paragraph(text, styles["Heading2"]))
    story.append(Spacer(1, 6))


def add_figure(title, filename, explanation):
    story.append(PageBreak())
    heading(title)

    image_path = graph_dir / filename
    width, height = ImageReader(str(image_path)).getSize()

    # Preserve proportions and keep the image within the page.
    scale = min(468 / width, 440 / height)
    story.append(
        Image(
            str(image_path),
            width=width * scale,
            height=height * scale,
        )
    )
    story.append(Spacer(1, 14))
    paragraph(explanation)


def page_number(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(558, 28, f"Page {document.page}")
    canvas.restoreState()


# Introduction and methods.
story.append(
    Paragraph(
        f"Baseball Salaries and Performance, {first_year}–{last_year}",
        styles["Title"],
    )
)
paragraph("Exploratory Data Analysis | COP 3045 | Team 5")
paragraph(f"Generated automatically: {datetime.now():%B %d, %Y}")

heading("1. Purpose and dataset")
paragraph(
    "This report examines salary distributions, relationships between "
    "salary and batting statistics, differences between leagues and teams, "
    "and the highest recorded player salaries."
)
paragraph(
    f"The cleaned dataset contains {len(df):,} rows, "
    f"{len(df.columns)} columns, and "
    f"{df['playerID'].nunique():,} unique players across "
    f"{first_year}–{last_year}. All analyses use data/clean_data.csv."
)

heading("2. Data preparation")
paragraph(
    "The cleaning script removes exact duplicate rows and converts "
    "numerical fields to numbers. Invalid numerical entries become "
    "missing values rather than being replaced with averages. The "
    "graphical analysis also trims whitespace from categorical values."
)
paragraph(
    f"Because salaries repeat across position rows, salary analyses use "
    f"one record per player, team, and season, giving "
    f"{len(salary_data):,} salary records. Batting analyses remove repeated "
    "copies of batting stints and sum separate stints within each "
    "player/team/season before joining salary."
)

heading("3. Missing data")
missing_percent = df.isna().mean() * 100
missing_lines = [
    f"{column}: {df[column].isna().sum():,} "
    f"({missing_percent[column]:.2f}%)"
    for column in ["salary", "AB", "POS", "PB", "WP", "ZR"]
]
paragraph("<br/>".join(missing_lines))
paragraph(
    f"The correlation analysis uses {len(complete):,} complete "
    "player/team/season records with the selected batting variables. "
    "Missingness varies substantially by column; retaining missing "
    "values does not guarantee unbiased results."
)

# Figure 1.
mean_salary = salary_data["salary"].mean()
median_salary = salary_data["salary"].median()
skewness = salary_data["salary"].skew()

add_figure(
    "Figure 1. Salary distribution",
    "salary_distribution.png",
    f"The mean salary is ${mean_salary:,.2f}, compared with a median "
    f"of ${median_salary:,.2f}. Salary skewness is {skewness:.2f}. "
    "The positive skew and higher mean indicate that a relatively small "
    "number of high salaries pull the average upward. The median is "
    "less affected by these extreme values. Salaries are pooled across "
    "seasons and are not inflation-adjusted.",
)

# Figure 2.
salary_correlations = correlation["Salary"].drop("Salary")
strongest = salary_correlations.abs().idxmax()
strongest_r = salary_correlations[strongest]

add_figure(
    "Figure 2. Salary and batting correlations",
    "salary_batting_correlation.png",
    f"Among the selected batting statistics, {strongest} has the largest "
    f"absolute Pearson correlation with salary (r = {strongest_r:.3f}). "
    "These correlations describe linear associations, not causation. "
    "The analysis pools seasons and includes pitchers with batting "
    "records, without adjusting for position, playing time, or season. "
    "G = games; AB = at-bats; R = runs; H = hits; 2B = doubles; "
    "3B = triples; HR = home runs; RBI = runs batted in; "
    "SB = stolen bases; BB = walks; SO = strikeouts.",
)

# Figure 3.
league_text = []
for league in ["AL", "NL"]:
    row = league_summary.loc[league]
    league_text.append(
        f"{league}: mean ${row['mean']:,.2f}; "
        f"median ${row['median']:,.2f}; "
        f"{int(row['count']):,} player/team/season records."
    )

add_figure(
    "Figure 3. Salary comparison by league",
    "salary_by_league.png",
    " ".join(league_text)
    + " The median describes typical salaries, while the mean is more "
    "affected by high earners. This pooled comparison does not adjust "
    "for season or player composition.",
)

# Figure 4.
highest_team = team_summary["median"].idxmax()
lowest_team = team_summary["median"].idxmin()

add_figure(
    f"Figure 4. Median salary by team, {latest_year}",
    f"median_salary_by_team_{latest_year}.png",
    f"{highest_team} has the highest median in this dataset at "
    f"${team_summary.loc[highest_team, 'median']:,.2f}, while "
    f"{lowest_team} has the lowest at "
    f"${team_summary.loc[lowest_team, 'median']:,.2f}. "
    "The comparison uses a single season and measures typical player "
    "salary, not total team payroll. Team labels are dataset identifiers.",
)

# Figure 5.
highest_player = top_players.idxmax()

add_figure(
    f"Figure 5. Highest recorded player salaries, {latest_year}",
    f"highest_paid_players_{latest_year}.png",
    f"Player {highest_player} has the highest recorded salary in the "
    f"ranking at ${top_players.max():,.2f}. "
    "The chart includes ties at the tenth-highest salary. For players "
    "with records for multiple teams, the highest recorded salary is "
    "used rather than adding potentially overlapping amounts. These "
    "values are not career earnings. Labels are player IDs.",
)

story.append(PageBreak())
heading("4. Limitations")
paragraph(
    "Results describe the supplied dataset and may not represent every "
    "player or every component of compensation. Missing performance "
    "records may affect the correlation sample. Position-specific "
    "statistics should not be treated as universally applicable."
)
paragraph(
    "Repeated observations of the same player across seasons remain "
    "in the pooled analyses. Salaries are not adjusted for inflation. "
    "The analysis does not control for experience, contract terms, "
    "position, or other potential influences on pay. No causal or "
    "statistical-significance claims are made."
)

heading("5. Conclusion")
paragraph(
    f"The salary distribution has a mean of ${mean_salary:,.0f} and "
    f"a median of ${median_salary:,.0f}, illustrating the influence "
    "of high earners on the average. League and team comparisons "
    "describe differences in salary levels. The batting correlations "
    "provide an initial view of performance associations, but should "
    "be interpreted alongside the study's limitations."
)

heading("Reproducibility")
paragraph(
    "Run 04-EDA/generate_report.py after data/clean_data.csv has been "
    "created. The report script runs graphical_eda.py, regenerates all "
    "five figures, calculates the report values, and writes this PDF "
    "without manual image insertion."
)

document = SimpleDocTemplate(
    str(pdf_path),
    pagesize=(612, 792),
    rightMargin=54,
    leftMargin=54,
    topMargin=48,
    bottomMargin=48,
)

document.build(
    story,
    onFirstPage=page_number,
    onLaterPages=page_number,
)

print("\nPDF report created:", pdf_path)
