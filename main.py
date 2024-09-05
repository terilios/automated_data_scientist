import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import config
from automated_data_scientist import AutomatedDataScientist
from code_generation import CodeGenerator
from api_client import APIClient

# Apply logging configuration
logging.config.dictConfig(config.LOGGING_CONFIG)

def main():
    # Initialize APIClient
    api_client = APIClient(api_type=config.DEFAULT_API_TYPE)

    # Initialize CodeGenerator
    code_generator = CodeGenerator(api_client)

    # Initialize Jupyter Notebook
    code_generator.initialize_notebook()

    # Initialize AutomatedDataScientist
    ads = AutomatedDataScientist(
        production_csv_path=config.PRODUCTION_CSV_PATH,
        output_path=config.DEFAULT_OUTPUT_DIR,
        data_dict_path=config.DATA_DICT_PATH,
        api_type=config.DEFAULT_API_TYPE,
        code_generator=code_generator
    )

    # Run the automated data science process
    ads.run()

    logging.info("Automated data science process completed. Check the output directory for results and the Jupyter Notebook.")

if __name__ == "__main__":
    main()