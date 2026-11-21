# Reads and combined the three raw files
# attributes to consider: path of the raw data files, file names, minimum year, columns to join.

class DataPreparer:
    def __init__(self, raw_data_path):
        self.raw_data_path = raw_data_path

    def prepare(self):
        # Read the three raw files and combine them into a single DataFrame. return the combined DataFrame called merged_database.db.
        # This will be recieved by the BaseballDatabase instance.
        
        # may be split into multiple methods for better organization and readability.
        return merged_df