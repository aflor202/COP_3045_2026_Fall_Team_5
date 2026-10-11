from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the cleaned data.
base_dir = Path(__file__).resolve().parent.parent
df = pd.read_csv(base_dir / "data" / "clean_data.csv")
df.columns = df.columns.str.strip()
# Remove spaces around categorical values.
for column in ["playerID", "teamID", "lgID", "POS"]:
    df[column] = df[column].str.strip().replace("", pd.NA)

# Use one salary per player/team/season.
# Keep this separate from the batting and fielding data.
keys = ["playerID", "yearID", "teamID"]

if df.groupby(keys)["salary"].nunique().gt(1).any():
    raise ValueError("Conflicting salaries found within player/team/season groups.")

salary_data = (
    df[keys + ["salary"]]
    .drop_duplicates(subset=keys)
    .dropna(subset=["salary"])
)

# Create the output folder.
output_dir = base_dir / "graphs"
output_dir.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")

# Display salaries in millions of dollars.
salary_millions = salary_data["salary"] / 1_000_000

fig, ax = plt.subplots(figsize=(10, 6))

sns.histplot(
    salary_millions,
    bins=40,
    color="steelblue",
    ax=ax,
)

ax.axvline(
    salary_millions.mean(),
    color="red",
    linestyle="--",
    label=f"Mean: ${salary_millions.mean():.2f} million",
)

ax.axvline(
    salary_millions.median(),
    color="green",
    linestyle="--",
    label=f"Median: ${salary_millions.median():.2f} million",
)

ax.set_title("Salary Distribution, 2000–2016")
ax.set_xlabel("Salary (millions of dollars, not inflation-adjusted)")
ax.set_ylabel("Number of player/team/season records")
ax.legend()

fig.tight_layout()

output_path = output_dir / "salary_distribution.png"
fig.savefig(output_path, dpi=300, bbox_inches="tight")

print("Player/team/season records:", len(salary_data))
print(f"Mean salary: ${salary_data['salary'].mean():,.2f}")
print(f"Median salary: ${salary_data['salary'].median():,.2f}")
print(f"Salary skewness: {salary_data['salary'].skew():.2f}")
print("Graph saved to:", output_path)


# Graph 2: Correlation between salary and batting statistics.

batting_columns = [
    "G_left", "AB", "R", "H", "2B", "3B",
    "HR", "RBI", "SB_left", "BB", "SO"
]

batting_keys = keys + ["stint_left"]

# Select batting information without the repeated fielding positions.
batting = (
    df[batting_keys + batting_columns]
    .dropna(subset=["stint_left"])
    .drop_duplicates()
)

# Stop if a single batting stint has conflicting statistics.
if batting.duplicated(subset=batting_keys).any():
    raise ValueError(
        "Conflicting batting records found. Check these before graphing."
    )

# Combine batting stints within each player/team/season.
batting_totals = (
    batting.groupby(keys)[batting_columns]
    .sum(min_count=1)
    .reset_index()
)

# Attach one salary per player/team/season.
analysis = batting_totals.merge(
    salary_data,
    on=keys,
    how="inner",
    validate="one_to_one",
)

# Use complete records so every correlation uses the same sample.
correlation_columns = ["salary"] + batting_columns
complete = analysis[correlation_columns].dropna()

correlation = complete.corr(method="pearson")

# Clearer labels for the graph.
correlation = correlation.rename(
    index={"salary": "Salary", "G_left": "G", "SB_left": "SB"},
    columns={"salary": "Salary", "G_left": "G", "SB_left": "SB"},
)

fig2, ax2 = plt.subplots(figsize=(12, 9))

sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    vmin=-1,
    vmax=1,
    center=0,
    square=True,
    ax=ax2,
)

ax2.set_title(
    "Salary and Batting Statistics: Pearson Correlations\n"
    f"2000–2016 | {len(complete):,} player/team/season records"
)

fig2.tight_layout()

heatmap_path = output_dir / "salary_batting_correlation.png"
fig2.savefig(heatmap_path, dpi=300, bbox_inches="tight")

print("\nRecords used for correlation:", len(complete))
print("Records excluded for missing values:", len(analysis) - len(complete))
print("\nCorrelations with salary:")
print(
    correlation["Salary"]
    .drop("Salary")
    .sort_values(ascending=False)
    .round(3)
)
print("\nHeatmap saved to:", heatmap_path)

# Graph 3: Compare salaries by league.

# Verify each player/team/season belongs to one league.
if df.groupby(keys)["lgID"].nunique().gt(1).any():
    raise ValueError("Multiple leagues found for a player/team/season.")

league_data = (
    df[keys + ["lgID", "salary"]]
    .drop_duplicates(subset=keys)
    .dropna(subset=["lgID", "salary"])
)

# Calculate statistics using one salary per player/team/season.
league_summary = (
    league_data.groupby("lgID")["salary"]
    .agg(["count", "mean", "median"])
    .reindex(["AL", "NL"])
)

print("\nSalary summary by league:")
print(league_summary.round(2).to_string())

# Convert salaries to millions for the graph.
plot_data = league_summary[["mean", "median"]] / 1_000_000
plot_data.columns = ["Mean", "Median"]
plot_data.index = ["American League (AL)", "National League (NL)"]

fig3, ax3 = plt.subplots(figsize=(9, 6))

plot_data.plot(
    kind="bar",
    ax=ax3,
    color=["steelblue", "seagreen"],
    rot=0,
)

# Label each bar with its value.
for container in ax3.containers:
    ax3.bar_label(container, fmt="%.2f", padding=3)

ax3.set_title("Mean and Median Salaries by League, 2000–2016")
ax3.set_xlabel("League")
ax3.set_ylabel("Salary (millions of dollars, not inflation-adjusted)")
ax3.set_ylim(0, plot_data.max().max() * 1.2)
ax3.legend(title="Statistic")

fig3.tight_layout()

league_path = output_dir / "salary_by_league.png"
fig3.savefig(league_path, dpi=300, bbox_inches="tight")

print("\nLeague graph saved to:", league_path)

# Graph 4: Median salary by team in the latest season.

latest_year = int(salary_data["yearID"].max())

team_data = salary_data[
    salary_data["yearID"] == latest_year
]

team_summary = (
    team_data.groupby("teamID")["salary"]
    .agg(["count", "mean", "median"])
    .sort_values("median", ascending=True)
)

fig4, ax4 = plt.subplots(figsize=(10, 11))

bars = ax4.barh(
    team_summary.index,
    team_summary["median"] / 1_000_000,
    color="steelblue",
)

ax4.bar_label(bars, fmt="%.2f", padding=4)

ax4.set_title(f"Median Player Salary by Team, {latest_year}")
ax4.set_xlabel("Median salary (millions of dollars)")
ax4.set_ylabel("Team ID")
ax4.set_xlim(
    0,
    (team_summary["median"].max() / 1_000_000) * 1.2,
)

fig4.tight_layout()

team_path = output_dir / f"median_salary_by_team_{latest_year}.png"
fig4.savefig(team_path, dpi=300, bbox_inches="tight")

print(f"\nTeam salary summary for {latest_year}:")
print(
    team_summary.sort_values("median", ascending=False)
    .round(2)
    .to_string()
)
print("\nTeam graph saved to:", team_path)

# Graph 5: Highest recorded salaries by player in 2016.

latest_year = int(salary_data["yearID"].max())

players_this_year = salary_data[
    salary_data["yearID"] == latest_year
]

# If a player has multiple teams, use their highest recorded salary.
# Do not sum these salaries without checking how they were recorded.
player_salaries = (
    players_this_year.groupby("playerID")["salary"]
    .max()
)

# Include any players tied at the tenth-highest salary.
top_players = (
    player_salaries.nlargest(10, keep="all")
    .sort_values()
)

fig5, ax5 = plt.subplots(figsize=(10, 8))

bars = ax5.barh(
    top_players.index,
    top_players / 1_000_000,
    color="seagreen",
)

ax5.bar_label(bars, fmt="%.2f", padding=4)

ax5.set_title(
    f"Highest Recorded Player Salaries, {latest_year}\n"
    "Top 10, including ties"
)
ax5.set_xlabel("Highest recorded salary per player (millions of dollars)")
ax5.set_ylabel("Player ID")
ax5.set_xlim(0, (top_players.max() / 1_000_000) * 1.15)

fig5.tight_layout()

player_path = output_dir / f"highest_paid_players_{latest_year}.png"
fig5.savefig(player_path, dpi=300, bbox_inches="tight")

print(f"\nHighest recorded player salaries in {latest_year}:")
print(top_players.sort_values(ascending=False).to_string())
print("\nPlayer graph saved to:", player_path)
plt.show()

