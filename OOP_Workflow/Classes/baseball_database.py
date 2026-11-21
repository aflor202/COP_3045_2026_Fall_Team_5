# stores the prepared data into an SQLite dabase and exports the data to a CSV file.
# attributes to consider: path of the database file, path of the exported CSV file.
class BaseballDatabase:
    def __init__(self, db_path):
        self.db_path = db_path

    def save(self, data):
        # Save the prepared data into an SQLite database.
        pass

    def export_csv(self, output_path):
        # Export the data from the SQLite database to a CSV file.
        return output_path