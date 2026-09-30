Write a complete, production-quality Python script using pandas to prepare and consolidate data from exactly 3 CSV files.

### Inputs

* read C:\Users\aflor\FIU\COP3045 - Python II\COP_3045_2026_Fall_Team_5\00-Raw_Data\Batting.csv , C:\Users\aflor\FIU\COP3045 - Python II\COP_3045_2026_Fall_Team_5\00-Raw_Data\Fielding.csv , and C:\Users\aflor\FIU\COP3045 - Python II\COP_3045_2026_Fall_Team_5\00-Raw_Data\Salaries.csv
* Use `pathlib.Path` to validate, resolve, and handle all file paths so the script is cross-platform compatible.
* Validate that each input path exists and is a file.
* The output file should be named `consolidated_data.csv` in the current working directory.

### Code Quality

* Use clear, descriptive variable and function names.
* Organize the script into sections.
* Include clear inline comments for each major section and function explaining the purpose of that specific block.
* For visualization use line breaks and clear markings of different sections.
* explicitly state data types 

### Data Collection 

* understanding the structure, identify relationships, and assess intial completeness
* create a summary of the databases limit to the first 10 observations
* create a loop assesing which column to use for a merge

### Data Cleaning and Validation

* Remove errors: Eliminate duplicate rows, fix formatting inconsistencies, and standardize naming conventions.
* Manage gaps: Handle missing values and identify statistical outliers to ensure baseline accuracy.
* Filter the DataFrame to retain only records from the year 2000 onwards.
* Handle invalid or unparseable date/year values explicitly and exclude them from the filtered dataset.
* Log how many records were removed during filtering.
4. Log the dimensions of the filtered DataFrame as rows × columns.

5. Log the first 5 rows of the filtered DataFrame using the logging module rather than `print()`.

6. Log the total number of missing values for every column.

7. Log the total number of duplicate rows using `DataFrame.duplicated().sum()`.

8. Store each filtered DataFrame in a list for consolidation.

### Consolidation

* Combine the 3 filtered DataFrames row-wise into one DataFrame.
* Preserve the union of all columns across the three input files.
* If a column exists in some files but not others, populate the missing values with `NaN`.
* attempt to identify or infer a join key.

### Output

after I approve the plan:
* Export the final consolidated DataFrame to:
  `consolidated_data_v2.csv`
* Log the final output path and the dimensions of the consolidated DataFrame after writing the file.

keep the implementation simple and clearly identify the steps with comments
Return only the complete Python script.