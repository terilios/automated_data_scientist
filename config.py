import os
from pathlib import Path

# Data Handling Configuration
MAX_SAMPLE_ROWS = 10  # Maximum number of rows to load from the production CSV for analysis
DATA_ENCODING = 'utf-8'  # Encoding to use when reading CSV files

# API Configuration
DEFAULT_API_TYPE = 'openai'  # Default API to use ('openai' or 'anthropic')
MAX_API_RETRIES = 3  # Maximum number of times to retry a failed API call
API_RETRY_DELAY = 1  # Delay (in seconds) between API call retries

# Analysis Configuration
MAX_ANALYSES = 10  # Maximum number of analyses to perform in a single run
MIN_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence level required for an insight to be included

# Code Execution Configuration
CODE_EXECUTION_TIMEOUT = 300  # Maximum time (in seconds) allowed for a single code execution
MAX_FIGURE_SIZE = (12, 8)  # Default maximum figure size for plots

# Output Configuration
OUTPUT_FORMAT = 'markdown'  # Format for output reports ('markdown' or 'html')
MAX_REPORT_LENGTH = 100000  # Maximum length (in words) for the final report

# File Paths
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = BASE_DIR / 'output'
DEFAULT_FIGURE_DIR = DEFAULT_OUTPUT_DIR / 'figures'

# Ensure output directories exist
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Environment variable names
ENV_OPENAI_API_KEY = 'OPENAI_API_KEY'
ENV_ANTHROPIC_API_KEY = 'ANTHROPIC_API_KEY'
ENV_PRODUCTION_CSV_PATH = 'PRODUCTION_CSV_PATH'
ENV_DATA_DICT_PATH = 'DATA_DICT_PATH'

# Function to get environment variables with default values
def get_env_variable(var_name: str, default: str = None) -> str:
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(
            f"Environment variable {var_name} is not set and no default provided.\n"
            f"Please set the {var_name} environment variable before running the script.\n"
            f"You can do this by running the following command in your terminal:\n"
            f"export {var_name}=your_api_key_here\n"
            f"Or by adding the following line to your .env file:\n"
            f"{var_name}=your_api_key_here"
        )
    return value

# API Keys (to be set in environment variables)
OPENAI_API_KEY = get_env_variable(ENV_OPENAI_API_KEY)
ANTHROPIC_API_KEY = get_env_variable(ENV_ANTHROPIC_API_KEY)

# File Paths (can be overridden by environment variables)
PRODUCTION_CSV_PATH = Path(get_env_variable(ENV_PRODUCTION_CSV_PATH, str(BASE_DIR / 'data' / 'production_data.csv')))
DATA_DICT_PATH = Path(get_env_variable(ENV_DATA_DICT_PATH, str(BASE_DIR / 'data' / 'data_dictionary.md')))

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': str(DEFAULT_OUTPUT_DIR / 'automated_data_scientist.log'),
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# List of allowed libraries for dynamic import in code execution
ALLOWED_LIBRARIES = [
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy', 'sklearn', 'statsmodels', 'plotly', 'altair', 'bokeh', 'dask', 'pyjanitor', 'xgboost', 'lightgbm', 'catboost', 'tensorflow', 'keras', 'pytorch', 'holoviews', 'geopandas', 'folium', 'dash', 'nltk', 'spacy', 'transformers', 'pyarrow', 'openpyxl', 'xlrd', 'pydantic', 'great_expectations', 'tsfresh', 'prophet', 'networkx', 'cvxpy', 'sympy', 'joblib', 'numba', 'h5py', 'zarr'
]
