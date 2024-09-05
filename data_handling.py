import logging
import json
from pathlib import Path
import pandas as pd
import re
from typing import Dict, Any

class DataHandler:
    def __init__(self, data_dict_path: Path, production_csv_path: Path):
        self.data_dict_path = data_dict_path
        self.production_csv_path = production_csv_path
        self.data_dict = {}
        self.data_dict_content = ""
        self.production_data_sample = None

    def initialize_data(self):
        """Initialize by loading the data dictionary and production data sample."""
        self.read_data_dictionary()
        self.load_production_data_sample()

    def read_data_dictionary(self) -> Dict:
        """
        Reads the data dictionary from the specified Markdown file and stores it in the data_dict attribute.
        Also stores the full content of the markdown file in the data_dict_content attribute.
        
        Returns:
        Dict: A dictionary containing the parsed data dictionary.
        
        Raises:
        FileNotFoundError: If the data dictionary file is not found.
        Exception: For any other error during file reading or parsing.
        """
        logging.info(f"Reading data dictionary from {self.data_dict_path}")
        try:
            with open(self.data_dict_path, 'r') as file:
                self.data_dict_content = file.read()
            
            # Parse the Markdown table content
            table_pattern = r'\|(.+?)\|(.+?)\|(.+?)\|'
            for match in re.finditer(table_pattern, self.data_dict_content, re.MULTILINE):
                column_name = match.group(1).strip()
                data_type = match.group(2).strip()
                description = match.group(3).strip()
                if column_name != "Column Name" and column_name != "---":  # Skip header and separator rows
                    self.data_dict[column_name] = {
                        "Type": data_type,
                        "Description": description
                    }
            
            logging.info("Data dictionary loaded successfully")
            return self.data_dict
        except FileNotFoundError:
            logging.error(f"Data dictionary file not found at {self.data_dict_path}")
            raise
        except Exception as e:
            logging.error(f"Error reading data dictionary: {str(e)}")
            raise

    def load_production_data_sample(self, sample_size: int = 10):
        """
        Load a sample of the production data.
        
        Args:
        sample_size (int): Number of rows to load as a sample. Default is 1000.
        """
        logging.info(f"Loading production data sample from {self.production_csv_path}")
        try:
            self.production_data_sample = pd.read_csv(self.production_csv_path, nrows=sample_size)
            logging.info(f"Loaded {len(self.production_data_sample)} rows as a sample")
            self._validate_data()
        except Exception as e:
            logging.error(f"Error loading production data sample: {str(e)}")
            raise

    def _validate_data(self):
        """Validate the loaded data against the data dictionary."""
        for column in self.production_data_sample.columns:
            if column not in self.data_dict:
                logging.warning(f"Column '{column}' not found in data dictionary.")
            else:
                expected_type = self.data_dict[column].get('Type', '').lower()
                if expected_type == 'int64' and not pd.api.types.is_integer_dtype(self.production_data_sample[column]):
                    logging.warning(f"Column '{column}' expected to be int64 but is {self.production_data_sample[column].dtype}")
                elif expected_type == 'object' and not pd.api.types.is_object_dtype(self.production_data_sample[column]):
                    logging.warning(f"Column '{column}' expected to be object but is {self.production_data_sample[column].dtype}")

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the production data sample.
        
        Returns:
        Dict[str, Any]: A dictionary containing summary statistics of the data.
        """
        if self.production_data_sample is None:
            raise ValueError("Production data sample has not been loaded.")
        
        summary = {
            "num_rows": len(self.production_data_sample),
            "num_columns": len(self.production_data_sample.columns),
            "column_types": self.production_data_sample.dtypes.to_dict(),
            "missing_values": self.production_data_sample.isnull().sum().to_dict(),
            "numeric_summary": self.production_data_sample.describe().to_dict(),
            "categorical_summary": {
                col: self.production_data_sample[col].value_counts().to_dict()
                for col in self.production_data_sample.select_dtypes(include=['object', 'category']).columns
            }
        }
        
        return summary

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    pass