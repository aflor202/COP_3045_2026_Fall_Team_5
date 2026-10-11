from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


# 1. Instantiate Database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "project.db"
engine = create_engine(f"sqlite:///{db_path}")
connection = engine.connect()

# 2. Read Data
csv_path = Path(__file__).resolve().parents[1] / "data" / "consolidated_data_v2.csv"
df = pd.read_csv(csv_path)

# 3. Create Tables
df.to_sql("consolidated_data_v2", con=connection, if_exists="replace", index=False)

# 4. Close Connection
connection.close()
