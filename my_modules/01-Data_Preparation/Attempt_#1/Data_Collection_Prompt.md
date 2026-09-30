Write a complete, production-quality Python script using pandas to prepare and consolidate data from exactly 3 CSV files.

### Inputs

* read C:\Users\aflor\FIU\COP3045 - Python II\COP_3045_2026_Fall_Team_5\00-Raw_Data\Batting.csv , C:\Users\aflor\FIU\COP3045 - Python II\COP_3045_2026_Fall_Team_5\00-Raw_Data\Fielding.csv , and C:\Users\aflor\FIU\COP3045 - Python II\COP_3045_2026_Fall_Team_5\00-Raw_Data\Salaries.csv
* Use `pathlib.Path` to validate, resolve, and handle all file paths so the script is cross-platform compatible.
* Validate that each input path exists and is a file.
* The output file should be named `consolidated_data.csv` in the current working directory.

### Code Quality

* Use clear, descriptive variable and function names.
* Organize the script into appropriate functions rather than putting all logic in the global scope.
* Include clear inline comments for each major section and function explaining the purpose of that specific block.
* Include a `main()` function and the standard `if __name__ == "__main__":` entry point.
* Do not use `print()` anywhere in the script.

### Logging

* Configure Python's built-in `logging` module at `INFO` level.
* Use logging for all terminal/status output.
* Log which file is currently being processed.
* Use appropriate log levels such as `INFO` for normal processing messages and `ERROR` for failures.

### Processing Each CSV

Loop through all 3 CSV files and perform the following operations independently:

1. Read the CSV into a pandas DataFrame.

2. Identify the date column:

   * If a `date` column exists, use it.
   * Otherwise, if a `year` column exists, use it.
   * If neither column exists, log an error and stop processing with a clear exception.

3. Filter the DataFrame to retain only records from the year 2000 onwards.

   * For a `date` column, parse it using `pd.to_datetime(..., errors="coerce")` and retain rows where the resulting year is >= 2000.
   * For a `year` column, convert it to a numeric representation and retain rows where the year is >= 2000.
   * Handle invalid or unparseable date/year values explicitly and exclude them from the filtered dataset.
   * Log how many records were removed during filtering.

4. Log the dimensions of the filtered DataFrame as rows × columns.

5. Log the first 5 rows of the filtered DataFrame using the logging module rather than `print()`.

6. Log the total number of missing values for every column.

7. Log the total number of duplicate rows using `DataFrame.duplicated().sum()`.

8. Store each filtered DataFrame in a list for consolidation.

### Consolidation

* Combine the 3 filtered DataFrames row-wise into one DataFrame.
* Use `pd.concat()` with `axis=0`, `join="outer"`, and `ignore_index=True`.
* Preserve the union of all columns across the three input files.
* If a column exists in some files but not others, populate the missing values with `NaN`.
* Do not attempt to identify or infer a join key.
* Preserve the original column names and data unless transformation is explicitly required for date/year filtering.

### Output
after I approve the plan:
* Export the final consolidated DataFrame to:
  `consolidated_data.csv`
* Use `index=False`.
* Resolve the output path using `pathlib.Path`.
* Log the final output path and the dimensions of the consolidated DataFrame after writing the file.

### Error Handling

* Fail with a clear error message if an input file does not exist or cannot be read.
* Fail with a clear error message if a file contains neither a `date` nor a `year` column.
* Handle malformed date/year values without crashing during filtering.
* Ensure errors are logged using the `logging` module.

keep the implementation simple and clearly identify the steps with comments
Return only the complete Python script.
