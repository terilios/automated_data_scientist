import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv
import traceback
import sys

# Load environment variables from .env file
load_dotenv()

import config
from automated_data_scientist import AutomatedDataScientist
from code_generation import CodeGenerator
from api_client import APIClient
from notebook_manager import NotebookManager
from data_handling import DataHandler

# Apply logging configuration
logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Automated Data Scientist application")
    print("Starting Automated Data Scientist application")

    try:
        # Initialize APIClient
        api_client = APIClient(api_type=config.DEFAULT_API_TYPE)
        logger.info(f"Initialized APIClient with {config.DEFAULT_API_TYPE} API")
        print("Initialized APIClient")

        # Initialize CodeGenerator
        code_generator = CodeGenerator(api_client)
        logger.info("Initialized CodeGenerator")
        print("Initialized CodeGenerator")

        # Initialize NotebookManager
        notebook_manager = NotebookManager(config.NOTEBOOK_PATH)
        logger.info(f"Initialized NotebookManager with notebook path: {config.NOTEBOOK_PATH}")
        print("Initialized NotebookManager")

        # Initialize DataHandler
        data_handler = DataHandler(config.DATA_DICT_PATH, config.PRODUCTION_CSV_PATH)
        logger.info("Initialized DataHandler")
        print("Initialized DataHandler")

        # Initialize AutomatedDataScientist
        ads = AutomatedDataScientist(
            production_csv_path=config.PRODUCTION_CSV_PATH,
            output_path=config.DEFAULT_OUTPUT_DIR,
            data_dict_path=config.DATA_DICT_PATH,
            api_type=config.DEFAULT_API_TYPE,
            code_generator=code_generator,
            notebook_manager=notebook_manager,
            data_handler=data_handler
        )
        logger.info("Initialized AutomatedDataScientist")
        print("Initialized AutomatedDataScientist")

        # Run the automated data science process
        print("Running automated data science process")
        ads.run()

        logger.info("Automated data science process completed successfully")
        print("Automated data science process completed successfully")

        logger.info(f"Check the output directory for results: {config.DEFAULT_OUTPUT_DIR}")
        logger.info(f"Jupyter Notebook saved at: {config.NOTEBOOK_PATH}")

    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"An error occurred: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

def setup_directories():
    """Ensure all necessary directories exist."""
    directories = [
        config.DEFAULT_OUTPUT_DIR,
        config.DEFAULT_FIGURE_DIR,
        config.LOGS_DIR
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

if __name__ == "__main__":
    try:
        setup_directories()
        main()
    except Exception as e:
        logger.critical(f"Critical error in main execution: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        print(f"Critical error: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)