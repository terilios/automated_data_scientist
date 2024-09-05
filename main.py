import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import config
from automated_data_scientist import AutomatedDataScientist

# Apply logging configuration
logging.config.dictConfig(config.LOGGING_CONFIG)

def main():
    # Initialize AutomatedDataScientist
    ads = AutomatedDataScientist(
        production_csv_path=config.PRODUCTION_CSV_PATH,
        output_path=config.DEFAULT_OUTPUT_DIR,
        data_dict_path=config.DATA_DICT_PATH,
        api_type=config.DEFAULT_API_TYPE
    )

    # Run the automated data science process
    ads.run()

    logging.info("Automated data science process completed. Check the output directory for results.")

if __name__ == "__main__":
    main()