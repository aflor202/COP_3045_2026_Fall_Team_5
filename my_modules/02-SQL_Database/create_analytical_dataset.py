from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


# 1. Connect to Database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "project.db"
engine = create_engine(f"sqlite:///{db_path}")
connection = engine.connect()

# 2. Read Table
# Read the table from the SQLite database into a pandas DataFrame.
table_name = "consolidated_data_v2"
df = pd.read_sql_table(table_name, con=connection)

# 3. Create Analytical DataFrame
# Keep the final result in a single dataframe named df and save it as CSV.
output_path = base_dir / "consolidated_data_database.csv"
df.to_csv(output_path, index=False)

# 4. Close Connection
connection.close()
