# Step 1: Read Data
from pathlib import Path

import pandas as pd

base_dir = Path(__file__).resolve().parent.parent
input_path = base_dir / "data" / "clean_data.csv"

df = pd.read_csv(input_path)
df.columns = df.columns.str.strip()

# Trim categorical text values without filling or removing missing values.
for column in df.select_dtypes(include="object").columns:
    df[column] = df[column].str.strip().replace("", pd.NA)

# Step 2: Numerical Variables
print("Dataset dimensions:", df.shape)
print("\nMissing values by column:")
missing_summary = pd.DataFrame(
    {
        "missing_count": df.isna().sum(),
        "missing_percent": (df.isna().mean() * 100).round(2),
    }
)
print(missing_summary)

numeric_columns = df.select_dtypes(include="number").columns
print("\nNumerical summary statistics:")
print(df[numeric_columns].describe().T)

# Step 3: Categorical Variables
print("\nCategorical summaries:")
for column in ("teamID", "lgID", "POS"):
    if column in df.columns:
        values = df[column].dropna()
        print(f"\n{column}: {values.nunique()} unique values")
        print(
            pd.DataFrame(
                {
                    "count": values.value_counts(),
                    "proportion": values.value_counts(normalize=True).round(4),
                }
            )
        )

if "playerID" in df.columns:
    print("\nUnique players:", df["playerID"].nunique())
    print("Most frequent player IDs (top 10 rows):")
    print(df["playerID"].value_counts().head(10))

# Step 4: Summary Tables
if "yearID" in df.columns:
    season_summary = df.groupby("yearID").agg(
        record_count=("playerID", "size"),
        distinct_player_count=("playerID", "nunique"),
    )
    if "salary" in df.columns:
        season_summary["mean_salary_per_record"] = df.groupby("yearID")["salary"].mean()
        season_summary["median_salary_per_record"] = df.groupby("yearID")["salary"].median()
    print("\nSummary by season (records may be position-level):")
    print(season_summary)

for column in ("teamID", "lgID", "POS"):
    if column in df.columns:
        category_summary = df.groupby(column).agg(
            record_count=("playerID", "size"),
            distinct_player_count=("playerID", "nunique"),
        )
        print(f"\nSummary by {column}:")
        print(category_summary.sort_values("record_count", ascending=False))
