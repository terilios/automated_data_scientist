# Automated Data Scientist

### Overview

This project, **Automated Data Scientist**, is an intelligent, adaptive data analysis solution designed to streamline and automate the data science workflow. Leveraging advanced language models and external APIs, it dynamically plans, executes, and refines data analyses, making it ideal for environments where rapid, data-driven decision-making is crucial.

The application automatically handles everything from data preparation and initial analysis planning to code generation, execution, and result interpretation. By integrating AI-driven capabilities, it can adaptively update its analysis plan based on intermediate results, ensuring that the most relevant and insightful analyses are performed on the data.

### Key Features

- **Automated Data Initialization**: Loads and prepares data using metadata from a data dictionary and a sample of the production data.
- **Dynamic Analysis Planning**: Uses language models via API calls to create an initial analysis plan based on the characteristics of the dataset.
- **Adaptive Analysis Execution**: Dynamically generates Python code for each analysis step, executes the code, and captures outputs, including results and visualizations.
- **Iterative Refinement**: Reviews the outputs and iteratively updates the analysis plan to refine insights or explore additional data characteristics.
- **Configurable Limits**: Allows configurable control over the maximum number of analyses to be performed, ensuring the process remains efficient and manageable.

### How It Works

1. **Environment Setup**: The application initializes by loading environment variables and setting up the logging configuration. This is managed by the `main.py` script, which serves as the entry point.

2. **Data Initialization**: The `DataHandler` class loads the data dictionary (metadata) and a sample of the production data, ensuring the analysis process has the necessary context and data.

3. **Initial Analysis Planning**: 
   - The `AnalysisPlanner` generates an initial analysis plan by sending a prompt to an external language model API (e.g., OpenAI GPT or Azure GPT) via the `APIClient`. 
   - The API response is parsed into a list of steps that describe various data cleaning, exploratory data analysis (EDA), hypothesis testing, and modeling tasks based on the dataset's characteristics.

4. **Analysis Execution**: 
   - The `CodeGenerator` dynamically creates Python code for each analysis step using another API call, turning high-level analytical tasks into executable scripts.
   - The `CodeExecutor` runs these scripts, capturing all outputs, including results, standard output, and any generated visualizations.

5. **Result Interpretation**: The `ResultInterpreter` reviews the results of each analysis step, providing context-aware interpretations and insights that help identify patterns, anomalies, or other significant findings.

6. **Adaptive Planning and Execution**:
   - After each analysis step, the application assesses the results and, if needed, adapts the analysis plan.
   - The `AnalysisPlanner` calls the `review_and_update_plan` method to reflect on completed analyses and intermediate findings, using API-based suggestions to add or refine further analysis steps.

7. **Configurable Control**: The application allows users to set a maximum number of analyses to be planned and executed, providing flexibility to balance thoroughness and efficiency.

8. **Completion and Logging**: Once all analysis steps are completed or the maximum limit is reached, the application logs the results and outputs to the designated directories, providing a clear trail of all activities and findings.

### Benefits

- **Automation and Efficiency**: Reduces the need for manual intervention by automating repetitive tasks and adapting the analysis based on data characteristics.
- **Flexibility and Adaptability**: Dynamically adjusts the analysis process to explore the most relevant data insights, responding to new findings in real-time.
- **Comprehensive Data Insights**: Provides in-depth, context-aware interpretations of results that are easy to understand, enabling faster decision-making.
- **Scalability**: Easily configurable to handle different datasets, from small exploratory studies to large-scale production data, with customizable limits on the scope of analysis.

### Getting Started

1. **Clone the Repository**: Download the project to your local environment.
2. **Set Up Environment Variables**: Configure environment variables such as API keys in a `.env` file.
3. **Install Dependencies**: Use the `requirements.txt` to install all necessary Python libraries.
4. **Run the Application**: Execute `main.py` to start the automated data science process.

### Requirements

- Python 3.7 or higher
- API access for external language models (e.g., OpenAI GPT or Azure GPT)
- Python libraries: pandas, numpy, matplotlib, seaborn, sklearn, scipy, etc.

### Future Enhancements

- Adding support for more complex data types and advanced analytics techniques.
- Extending integration with other data science tools and platforms.
- Enhancing the interpretive capabilities with domain-specific knowledge models.

This project represents a step toward a more intelligent, efficient, and adaptive approach to data analysis, leveraging state-of-the-art AI and automation techniques.
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
