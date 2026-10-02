New iteration for the Data Preparation stage
before planning any changes read the folder 'Attempt_#2'
keep changes simple and efficient
make sure to make comments before each section of code explaining that section of code

1. Update the Join Key to Prevent Merge Artifacts

The Issue: The dataset duplicated columns like stint, G (Games), SB (Stolen Bases), and CS (Caught Stealing) into _left and _right variants because they existed in both the Batting and Fielding tables but weren't fully accounted for in the merge logic.
The Fix: Add "stint" to the JOIN_COLUMNS tuple in Data_Collection_v2.py. This ensures that players who were traded mid-season (and thus have multiple "stints") are joined correctly, rather than creating a Cartesian product of their stats.   
PY+ 1

    Change: JOIN_COLUMNS: Final[tuple[str, str, str, str, str]] = ("playerID", "yearID", "teamID", "lgID", "stint")

2. Fix the Data Normalization Logic (Hidden Missing Values)

The Issue: Missing values in the raw CSVs were represented as empty strings ("" or " "). The normalize_dataframe function attempted to convert text to numeric using pd.to_numeric(..., errors="coerce"), but it included a strict validation check: if non_missing_count > 0 and numeric_count == non_missing_count:. Because errors="coerce" turned the empty strings into NaN, numeric_count became lower than non_missing_count, causing the check to fail and leaving the columns as object types.
The Fix: Explicitly replace empty strings with NaN before evaluating the column types.   
PY+ 1

    Change in normalize_dataframe:
    Python

    # Replace whitespace-only strings with actual NaNs first
    normalized = normalized.replace(r'^\s*$', pd.NA, regex=True)

3. Coalesce Overlapping Columns

The Issue: Even with "stint" added to the join keys, stats like Games (G), Stolen Bases (SB), and Caught Stealing (CS) exist in both tables.
The Fix: Add a post-merge cleanup function to combine these columns and drop the redundant suffixes.

    Addition:
    Python

    def resolve_merge_artifacts(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Combine overlapping left/right columns after merging."""
        left_cols = [c for c in dataframe.columns if c.endswith('_left')]
        for left_col in left_cols:
            base_col = left_col.replace('_left', '')
            right_col = base_col + '_right'
            if right_col in dataframe.columns:
                dataframe[base_col] = dataframe[left_col].fillna(dataframe[right_col])
                dataframe = dataframe.drop(columns=[left_col, right_col])
        return dataframe

4. Drop Constant and Empty Columns

The Issue: WP (Wild Pitches) and ZR (Zone Rating) were retained despite being entirely empty (or containing a single constant space character).
The Fix: Introduce a filter to drop columns that have zero variance prior to saving the output.

    Addition:
    Python

    def drop_empty_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Remove columns that contain only missing values or a single constant."""
        cols_to_drop = [col for col in dataframe.columns if dataframe[col].nunique(dropna=True) <= 1]
        LOGGER.info("Dropping constant/empty columns: %s", cols_to_drop)
        return dataframe.drop(columns=cols_to_drop)

Summary of the Executed File Cleanup:
The provided file (cleaned_consolidated_data.csv) has already had these fixes applied. I stripped the leading whitespace from all column headers, replaced empty strings with proper NaN values, cast all statistical columns to float64 (allowing for decimals and NaNs), coalesced the _left and _right merge artifacts, and dropped the empty WP and ZR columns. It is now properly formatted for EDA.