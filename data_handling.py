import logging
import json
from pathlib import Path
import pandas as pd
import numpy as np
import re
from typing import Dict, Any, Optional
import traceback

class DataHandler:
    def __init__(self, data_dict_path: Path, production_csv_path: Path):
        self.data_dict_path = data_dict_path
        self.production_csv_path = production_csv_path
        self.data_dict: Dict[str, Dict[str, str]] = {}
        self.data_dict_content: str = ""
        self.production_data_sample: Optional[pd.DataFrame] = None
        self.logger = logging.getLogger(__name__)

    def initialize_data(self):
        """Initialize by loading the data dictionary and production data sample."""
        try:
            self.read_data_dictionary()
            self.load_production_data_sample()
        except Exception as e:
            self.logger.error(f"Error initializing data: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def read_data_dictionary(self) -> Dict[str, Dict[str, str]]:
        """
        Reads the data dictionary from the specified Markdown file and stores it in the data_dict attribute.
        Also stores the full content of the markdown file in the data_dict_content attribute.
        
        Returns:
        Dict[str, Dict[str, str]]: A dictionary containing the parsed data dictionary.
        
        Raises:
        FileNotFoundError: If the data dictionary file is not found.
        Exception: For any other error during file reading or parsing.
        """
        self.logger.info(f"Reading data dictionary from {self.data_dict_path}")
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
            
            self.logger.info("Data dictionary loaded successfully")
            return self.data_dict
        except FileNotFoundError:
            self.logger.error(f"Data dictionary file not found at {self.data_dict_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading data dictionary: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def load_production_data_sample(self, sample_size: int = 10):
        """
        Load a sample of the production data.
        
        Args:
        sample_size (int): Number of rows to load as a sample. Default is 10.
        """
        self.logger.info(f"Loading production data sample from {self.production_csv_path}")
        try:
            self.production_data_sample = pd.read_csv(self.production_csv_path, nrows=sample_size)
            self.logger.info(f"Loaded {len(self.production_data_sample)} rows as a sample")
            self._validate_data()
            self._clean_text_data()
            self._handle_missing_data()
        except FileNotFoundError:
            self.logger.error(f"Production data file not found at {self.production_csv_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading production data sample: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _validate_data(self):
        """Validate the loaded data against the data dictionary, enforcing data types and identifying missing values."""
        if self.production_data_sample is None:
            self.logger.error("Production data sample is None. Cannot validate.")
            return

        for column in self.production_data_sample.columns:
            if column not in self.data_dict:
                self.logger.warning(f"Column '{column}' not found in data dictionary.")
            else:
                expected_type = self.data_dict[column].get('Type', '').lower()
                actual_type = str(self.production_data_sample[column].dtype)
                try:
                    # Attempt type conversion if there's a mismatch
                    if expected_type == 'int64':
                        self.production_data_sample[column] = pd.to_numeric(self.production_data_sample[column], errors='coerce').astype('Int64')
                    elif expected_type == 'float64':
                        self.production_data_sample[column] = pd.to_numeric(self.production_data_sample[column], errors='coerce')
                    elif expected_type == 'object':
                        self.production_data_sample[column] = self.production_data_sample[column].astype('object')

                    if actual_type != str(self.production_data_sample[column].dtype):
                        self.logger.info(f"Column '{column}' type converted from {actual_type} to {self.production_data_sample[column].dtype}")

                except Exception as e:
                    self.logger.error(f"Could not convert column '{column}' to {expected_type}: {str(e)}")

    def _clean_text_data(self):
        """Clean up text data fields in the production data sample to remove unwanted characters."""
        if self.production_data_sample is None:
            self.logger.error("Production data sample is None. Cannot clean text data.")
            return

        text_columns = self.production_data_sample.select_dtypes(include=['object']).columns
        for column in text_columns:
            try:
                self.production_data_sample[column] = (
                    self.production_data_sample[column]
                    .fillna('')  # Replace NaN with empty string to avoid errors
                    .str.replace('\n', ' ', regex=False)  # Remove newlines
                    .str.replace(r'\s+', ' ', regex=True)  # Remove excessive whitespace
                    .str.strip()  # Remove leading/trailing whitespace
                )
                self.logger.info(f"Cleaned text data in column: {column}")
            except Exception as e:
                self.logger.error(f"Error cleaning text data in column '{column}': {str(e)}")

    def _handle_missing_data(self):
        """Handle missing data by imputing or removing based on rules."""
        if self.production_data_sample is None:
            self.logger.error("Production data sample is None. Cannot handle missing data.")
            return

        for column in self.production_data_sample.columns:
            missing_count = self.production_data_sample[column].isnull().sum()
            if missing_count > 0:
                self.logger.info(f"Column '{column}' has {missing_count} missing values")
                if pd.api.types.is_numeric_dtype(self.production_data_sample[column]):
                    # Impute numeric columns with the median
                    median_value = self.production_data_sample[column].median()
                    self.production_data_sample[column].fillna(median_value, inplace=True)
                    self.logger.info(f"Imputed missing values in '{column}' with median: {median_value}")
                else:
                    # Impute categorical/text columns with 'Unknown'
                    self.production_data_sample[column].fillna('Unknown', inplace=True)
                    self.logger.info(f"Imputed missing values in '{column}' with 'Unknown'")

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the production data sample.
        
        Returns:
        Dict[str, Any]: A dictionary containing summary statistics of the data.
        """
        if self.production_data_sample is None:
            self.logger.error("Production data sample is None. Cannot generate summary.")
            return {}
        
        try:
            summary = {
                "num_rows": len(self.production_data_sample),
                "num_columns": len(self.production_data_sample.columns),
                "column_types": self.production_data_sample.dtypes.astype(str).to_dict(),
                "missing_values": self.production_data_sample.isnull().sum().to_dict(),
                "numeric_summary": self.production_data_sample.describe().to_dict(),
                "categorical_summary": {
                    col: self.production_data_sample[col].value_counts().to_dict()
                    for col in self.production_data_sample.select_dtypes(include=['object', 'category']).columns
                }
            }
            
            self.logger.info("Generated data summary successfully")
            return summary
        except Exception as e:
            self.logger.error(f"Error generating data summary: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {}

    def save_processed_data(self, output_path: Path):
        """Save the processed data sample to a CSV file."""
        if self.production_data_sample is None:
            self.logger.error("Production data sample is None. Cannot save processed data.")
            return

        try:
            output_file = output_path / "processed_data_sample.csv"
            self.production_data_sample.to_csv(output_file, index=False)
            self.logger.info(f"Saved processed data sample to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving processed data: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='data_handling.log')

    # This block is for testing purposes
    data_dict_path = Path("data/data_dictionary.md")
    production_csv_path = Path("data/production_data.csv")
    
    try:
        data_handler = DataHandler(data_dict_path, production_csv_path)
        data_handler.initialize_data()
        
        # Test data summary
        summary = data_handler.get_data_summary()
        print(json.dumps(summary, indent=2))
        
        # Test saving processed data
        output_path = Path("test_output")
        output_path.mkdir(exist_ok=True)
        data_handler.save_processed_data(output_path)
        
    except Exception as e:
        logging.error(f"Error in data handling test: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
