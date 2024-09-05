# Automated Data Scientist

## Overview

The **Automated Data Scientist** is an intelligent, adaptive data analysis solution designed to streamline and automate the data science workflow. Leveraging advanced language models and external APIs, it dynamically plans, executes, and refines data analyses, making it ideal for environments where rapid, data-driven decision-making is crucial.

This application automatically handles everything from data preparation and initial analysis planning to code generation, execution, and result interpretation. By integrating AI-driven capabilities, it can adaptively update its analysis plan based on intermediate results, ensuring that the most relevant and insightful analyses are performed on the data.

```mermaid
flowchart TD
    A[Environment Setup] --> B[Data Initialization]
    B --> C[Initial Analysis Planning]
    C --> D[Analysis Execution]
    D --> E[Result Interpretation]
    E --> F[Adaptive Planning]
    F --> C
    E --> G[Jupyter Notebook Integration]
    G --> H[Completion and Logging]

    subgraph Setup
    A
    end

    subgraph Initialization
    B
    end

    subgraph Planning
    C
    end

    subgraph Execution
    D
    end

    subgraph Interpretation
    E
    end

    subgraph Adaptive_Planning
    F
    end

    subgraph Notebook
    G
    end

    subgraph Completion
    H
    end

'''

## Key Features

- **Automated Data Initialization**: Loads and prepares data using metadata from a data dictionary and a sample of the production data.
- **Dynamic Analysis Planning**: Uses language models via API calls to create an initial analysis plan based on the characteristics of the dataset.
- **Adaptive Analysis Execution**: Dynamically generates Python code for each analysis step, executes the code, and captures outputs, including results and visualizations.
- **Iterative Refinement**: Reviews the outputs and iteratively updates the analysis plan to refine insights or explore additional data characteristics.
- **Integrated Jupyter Notebook Support**: Automatically generates and updates a Jupyter Notebook during the analysis process for interactive exploration.
- **Enhanced API Client Handling**: Supports multiple API types (`openai`, `anthropic`) with error handling and retry logic for resilient API interactions.
- **Detailed Logging and Monitoring**: Configurable logging provides comprehensive insights into the execution process for debugging and monitoring.
- **Configurable Limits**: Allows configurable control over the maximum number of analyses to be performed, ensuring the process remains efficient and manageable.

## Benefits

- **Automation and Efficiency**: Reduces the need for manual intervention by automating repetitive tasks and adapting the analysis based on data characteristics.
- **Flexibility and Adaptability**: Dynamically adjusts the analysis process to explore the most relevant data insights, responding to new findings in real time.
- **Comprehensive Data Insights**: Provides in-depth, context-aware interpretations of results that are easy to understand, enabling faster decision-making.
- **Scalability**: Easily configurable to handle different datasets, from small exploratory studies to large-scale production data, with customizable limits on the scope of analysis.
- **Interactive Exploration**: The integration of Jupyter Notebook support enables users to interact with and refine the analysis process seamlessly.

## Getting Started

### 1. Clone the Repository

Download the project to your local environment:

```bash
git clone https://github.com/yourusername/automated-data-scientist.git
cd automated-data-scientist
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with your configuration details:

```bash
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
PRODUCTION_CSV_PATH=/path/to/your/production_data.csv
DATA_DICT_PATH=/path/to/your/data_dictionary.md
```

> **Note**: Ensure that your API keys are valid and have appropriate permissions. You can obtain these keys from [OpenAI](https://beta.openai.com/signup/) and [Anthropic](https://anthropic.com).

### 3. Create and Activate a Virtual Environment

Set up a Python virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 4. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### 5. Run the Application

Execute the main script to start the automated data science process:

```bash
python main.py
```

### 6. Review Outputs

Check the `output` directory for the generated reports, visualizations, and the Jupyter Notebook.

## Configuration

### Customizing the Analysis

The behavior of the Automated Data Scientist can be customized by editing the `config.py` file:

- **Data Handling**: Adjust parameters such as `MAX_SAMPLE_ROWS` to control the amount of data loaded for analysis.
- **API Usage**: Set the `DEFAULT_API_TYPE`, `MAX_API_RETRIES`, and `API_RETRY_DELAY` for API interactions.
- **Analysis Parameters**: Modify `MAX_ANALYSES` and `MIN_CONFIDENCE_THRESHOLD` to control the scope and depth of the analysis.
- **Code Execution**: Configure `CODE_EXECUTION_TIMEOUT` to manage the execution time of code blocks.
- **Logging**: Customize the `LOGGING_CONFIG` to suit your monitoring and debugging needs.

### Example `.env` File

Here’s a sample `.env` file for quick reference:

```plaintext
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
PRODUCTION_CSV_PATH=/path/to/your/production_data.csv
DATA_DICT_PATH=/path/to/your/data_dictionary.md
```

### Troubleshooting

- **Virtual Environment Issues**: If you encounter problems with the virtual environment, ensure that you are using Python 3.7 or higher and have correctly activated the environment.
- **API Authentication Errors**: Double-check that your API keys are correctly set in the `.env` file and that your network allows outbound connections to the API services.
- **Missing Dependencies**: Run `pip install -r requirements.txt` again to ensure all dependencies are installed.

## Usage Examples

### Example 1: Running a Basic Analysis

To run a standard analysis on a production dataset:

```bash
python main.py
```

### Example 2: Custom Analysis with Modified Settings

Adjust `config.py` to change the default API type and increase the number of analyses:

```python
DEFAULT_API_TYPE = 'anthropic'
MAX_ANALYSES = 15
```

Then, run the application again:

```bash
python main.py
```

## Contributing

We welcome contributions to enhance this project! To contribute:

1. **Fork the repository** and clone it to your local machine.
2. **Create a new branch** for your feature or bug fix.
3. **Make your changes** and ensure they are well-documented.
4. **Submit a pull request** with a clear description of your changes.

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) to create a welcoming environment for everyone.

## Versioning and Updates

This project uses [Semantic Versioning](https://semver.org/). Check the [Changelog](CHANGELOG.md) for details on updates and changes.

### Future Enhancements

- **Support for Complex Data Types**: Adding capabilities to handle time series, geospatial data, and more.
- **Integration with Additional Tools**: Extending support to include more data science platforms and libraries.
- **Domain-Specific Knowledge Models**: Enhancing interpretive capabilities by incorporating domain-specific models.

## Additional Resources

- [OpenAI API Documentation](https://beta.openai.com/docs/)
- [Anthropic API Documentation](https://anthropic.com/docs)
- [Python Virtual Environment Guide](https://docs.python.org/3/tutorial/venv.html)
- [Data Science Best Practices](https://towardsdatascience.com/)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
