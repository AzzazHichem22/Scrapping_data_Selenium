import pandas as pd

class DataStorage:
    def __init__(self):
        self.df = pd.DataFrame()

    def create_dataframe(self, data,columns):
        self.df = pd.DataFrame(data, columns=columns)

    def add_data(self, data):
        # Convert data to a DataFrame if it's not already
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data, columns=self.df.columns)

        # Append the data to the existing DataFrame
        self.df = pd.concat([self.df, data], ignore_index=True, axis=0)

    def remove_data(self, index):
        self.df = self.df.drop(index=index).reset_index(drop=True)

    def update_data(self, index, column, value):
        self.df.at[index, column] = value

    def import_from_csv(self, filename):
        self.df = pd.read_csv(filename)

    def export_to_csv(self, filename):
        self.df.to_csv(filename, index=False)