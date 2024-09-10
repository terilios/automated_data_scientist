import os
from pathlib import Path
from typing import List, Dict, Any

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Data Handling Configuration
MAX_SAMPLE_ROWS = 20000  # Maximum number of rows to load from the production CSV for analysis
DATA_ENCODING = 'utf-8'  # Encoding to use when reading CSV files
MISSING_VALUE_THRESHOLD = 0.2  # Maximum proportion of missing values allowed in a column

# API Configuration
DEFAULT_API_TYPE = 'openai'  # Default API to use ('openai' or 'anthropic')
MAX_API_RETRIES = 3  # Maximum number of times to retry a failed API call
API_RETRY_DELAY = 1  # Delay (in seconds) between API call retries
MAX_TOKENS = 4000  # Maximum number of tokens for API requests

# Analysis Configuration
MAX_ANALYSES = 3  # Maximum number of analyses to perform in a single run
MIN_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence level required for an insight to be included 

# Code Execution Configuration
CODE_EXECUTION_TIMEOUT = 300  # Maximum time (in seconds) allowed for a single code execution 
MAX_FIGURE_SIZE = (12, 8)  # Default maximum figure size for plots 
DPI = 300  # Dots per inch for saved figures 

# Output Configuration
OUTPUT_FORMAT = 'markdown'  # Format for output reports ('markdown' or 'html') 
MAX_REPORT_LENGTH = 100000  # Maximum length (in words) for the final report 

# File Paths
DEFAULT_OUTPUT_DIR = BASE_DIR / 'output' 
DEFAULT_FIGURE_DIR = DEFAULT_OUTPUT_DIR / 'figures' 
LOGS_DIR = BASE_DIR / 'logs' 

# Ensure output directories exist
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True) 
DEFAULT_FIGURE_DIR.mkdir(parents=True, exist_ok=True) 
LOGS_DIR.mkdir(parents=True, exist_ok=True) 

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
NOTEBOOK_PATH = DEFAULT_OUTPUT_DIR / 'analysis_notebook.ipynb' 

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
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'automated_data_scientist.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
} 

# List of allowed libraries for dynamic import in code execution
ALLOWED_LIBRARIES: List[str] = [
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy', 'sklearn', 'statsmodels',
    'plotly', 'altair', 'bokeh', 'dask', 'pyjanitor', 'xgboost', 'lightgbm',
    'catboost', 'tensorflow', 'keras', 'pytorch', 'holoviews', 'geopandas',
    'folium', 'dash', 'nltk', 'spacy', 'transformers', 'pyarrow', 'openpyxl',
    'xlrd', 'pydantic', 'great_expectations', 'tsfresh', 'prophet', 'networkx',
    'cvxpy', 'sympy', 'joblib', 'numba', 'h5py', 'zarr'
] 

# Visualization settings
VISUALIZATION_SETTINGS: Dict[str, Any] = {
    'style': 'seaborn',
    'context': 'paper',
    'palette': 'deep',
    'font_scale': 1.2,
} 

# Data preprocessing settings
PREPROCESSING_SETTINGS: Dict[str, Any] = {
    'remove_duplicates': True,
    'handle_missing_values': True,
    'outlier_detection_method': 'IQR',  # 'IQR' or 'Z-score'
    'outlier_threshold': 1.5,  # for IQR method
    'z_score_threshold': 3,  # for Z-score method
} 

# Model evaluation metrics
EVALUATION_METRICS: Dict[str, List[str]] = {
    'regression': ['mean_squared_error', 'mean_absolute_error', 'r2_score'],
    'classification': ['accuracy', 'precision', 'recall', 'f1_score'],
    'clustering': ['silhouette_score', 'calinski_harabasz_score', 'davies_bouldin_score'],
} 

def get_config() -> Dict[str, Any]:
    """
    Returns a dictionary containing all configuration settings.
    This can be useful for passing configuration to other parts of the application.
    """
    return {key: value for key, value in globals().items() if not key.startswith('__') and key.isupper()} 

if __name__ == "__main__":
    import json
    
    print("Current configuration:")
    print(json.dumps(get_config(), indent=2, default=str)) 
