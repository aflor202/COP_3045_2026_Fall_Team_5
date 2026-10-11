# Step 1: Read Data
from pathlib import Path

import pandas as pd

base_dir = Path(__file__).resolve().parent.parent
input_path = base_dir / "data" / "SQL_database.csv"

df = pd.read_csv(input_path)
df.columns = df.columns.str.strip()

# Step 2: Inspect Data
print("Missing values by column:")
print(df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())
print("\nData types:")
print(df.dtypes)

# Step 3: Clean and Prepare Data
# Remove exact duplicate rows.
df = df.drop_duplicates()

# Trim text values and treat blank strings as missing without filling missing values.
for column in df.columns:
    if df[column].dtype == "object":
        df[column] = df[column].str.strip().replace("", pd.NA)

# Convert numeric fields while preserving missing and invalid values as NaN.
non_numeric_columns = {"playerID", "teamID", "lgID", "POS"}
for column in df.columns:
    if column not in non_numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Step 4: Save Clean Data
output_path = base_dir / "data" / "clean_data.csv"
df.to_csv(output_path, index=False)

print("\nCleaned data saved to:", output_path)
