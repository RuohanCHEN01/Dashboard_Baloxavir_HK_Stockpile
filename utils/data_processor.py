import pandas as pd


class DataProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None

    def load_data(self):
        try:
            self.data = pd.read_csv(self.filepath)
            print('Data loaded successfully.')
        except FileNotFoundError as e:
            print(f'Error: {e}')
        except Exception as e:
            print(f'An error occurred: {e}')

    def process_data(self):
        if self.data is None:
            print('No data to process. Load data first.')
            return
        # Example processing: handle missing values
        self.data.ffill(inplace=True)
        print('Data processed successfully.')

    def save_data(self, output_filepath):
        if self.data is None:
            print('No data to save. Load and process data first.')
            return
        self.data.to_csv(output_filepath, index=False)
        print(f'Data saved to {output_filepath} successfully.')
