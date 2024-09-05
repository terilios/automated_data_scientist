# Automated Data Scientist

This project implements an automated data science pipeline that can analyze datasets, generate insights, and produce reports.

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/automated-data-scientist.git
   cd automated-data-scientist
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables. Create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   PRODUCTION_CSV_PATH=/path/to/your/production_data.csv
   DATA_DICT_PATH=/path/to/your/data_dictionary.md
   ```

5. Place your production CSV data and data dictionary Markdown file in the appropriate locations (or update the paths in the `.env` file).

## Running the Automated Data Scientist

To run the automated data science process:

```
python main.py
```

Check the `output` directory for the generated report and visualizations.

## Configuration

You can modify the behavior of the Automated Data Scientist by editing the `config.py` file. This includes settings for data handling, API usage, analysis limits, and output formatting.

## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.