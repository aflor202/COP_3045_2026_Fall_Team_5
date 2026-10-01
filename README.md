# COP_3045_2026_Fall_Team_5
Repo for FIU Fall 2026 Python II course; Team 5



## Part 1: Data Preparation

This section prepares and consolidates baseball batting, fielding, and salary data.

The implementation is located at:

`01-Data_Preparation/Attempt_#2/Data_Collection_v2.py`

The script:

- Reads `Batting.csv`, `Fielding.csv`, and `Salaries.csv`.
- Validates input paths using `pathlib`.
- Normalizes column names and text values.
- Filters records to `yearID >= 2000`.
- Removes invalid years and duplicate rows.
- Reports missing values and potential numeric outliers.
- Uses `playerID`, `yearID`, `teamID`, and `lgID` as the composite join key.
- Performs full outer merges to preserve records from all datasets.
- Removes observations without salary data.
- Writes `consolidated_data_v2.csv`.
- Logs processing details, dimensions, filtering results, and merge diagnostics.

AI Assistance Disclosure
GitHub Copilot was used to assist with drafting, structuring, and refining portions of the data-preparation script and this documentation.

The project author, Andres Flores, reviewed the generated content, selected the data-cleaning and merging approach, verified the project requirements, and remains responsible for the final implementation and results.

## Input Data

Required files:

```text
00-Raw_Data/
├── Batting.csv
├── Fielding.csv
└── Salaries.csv

