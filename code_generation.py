import logging
from typing import Dict, Any, List
from api_client import APIClient
import config
from config import ALLOWED_LIBRARIES
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

class CodeGenerator:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.notebook = new_notebook()
        self.notebook_path = 'output/analysis_notebook.ipynb'

    def generate_code(self, analysis: Dict[str, Any], data_dict: Dict[str, Any], analysis_plan: List[Dict[str, Any]], data_dict_content: str) -> str:
        """
        Generates Python code for a given analysis step and adds it to the Jupyter Notebook.

        Args:
        analysis (Dict[str, Any]): The analysis step details.
        data_dict (Dict[str, Any]): The data dictionary describing the dataset.
        analysis_plan (List[Dict[str, Any]]): The complete analysis plan.
        data_dict_content (str): The full content of the data dictionary markdown file.

        Returns:
        str: Generated Python code for the analysis.
        """
        logging.info(f"Generating code for analysis: {analysis['name']}")

        prompt = f"""
        Generate Python code for the following analysis:

        Current Analysis Step:
        {analysis}

        Complete Analysis Plan:
        {analysis_plan}

        Data Dictionary:
        {data_dict}

        Full Data Dictionary Content:
        {data_dict_content}

        Please follow these guidelines:
        1. The main DataFrame should be loaded from '{config.PRODUCTION_CSV_PATH}' and named 'df'
        2. Use pandas, numpy, and matplotlib for data manipulation and visualization
        3. Save any visualizations to files in the '{config.DEFAULT_FIGURE_DIR}' directory instead of displaying them
        4. Include comments to explain key steps
        5. Handle potential errors or edge cases
        6. Store the main result or insight in a variable named 'result'
        7. Use seaborn for more advanced visualizations if needed
        8. Ensure the code is efficient and follows best practices
        9. Use the following code to load the data:
           import pandas as pd
           df = pd.read_csv('{config.PRODUCTION_CSV_PATH}')
        10. Consider the complete analysis plan when generating code for this step
        11. You may only use the following libraries in your code:
            {', '.join(ALLOWED_LIBRARIES)}

        Provide only the Python code, without any explanations or markdown formatting.
        """

        code = self.api_client.call_api(prompt)
        logging.info(f"Code generated for analysis: {analysis['name']}")
        
        # Add the generated code to the Jupyter Notebook
        self.add_to_notebook(analysis['name'], code)
        
        return code

    def generate_code_structure(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a high-level structure for the analysis code.

        Args:
        analysis (Dict[str, Any]): The analysis step details.

        Returns:
        str: A string containing the high-level code structure.
        """
        prompt = f"""
        Given the following analysis task:

        {analysis}

        Please provide a high-level structure for the Python code that will perform this analysis.
        The structure should be a list of section names, such as:
        1. Import libraries
        2. Load and preprocess data
        3. Perform analysis
        4. Visualize results
        5. Interpret findings

        Return only the list of section names, one per line.
        """

        structure = self.api_client.call_api(prompt)
        return structure

    def refine_code(self, code: str, error_message: str = None, data_dict: Dict[str, Any] = None, analysis_plan: List[Dict[str, Any]] = None, data_dict_content: str = None, additional_requirements: str = None) -> str:
        """
        Refines the generated code based on error messages or additional requirements.

        Args:
        code (str): The original generated code.
        error_message (str, optional): Any error message produced when running the code.
        data_dict (Dict[str, Any], optional): The data dictionary describing the dataset.
        analysis_plan (List[Dict[str, Any]], optional): The complete analysis plan.
        data_dict_content (str, optional): The full content of the data dictionary markdown file.
        additional_requirements (str, optional): Any additional requirements or modifications needed.

        Returns:
        str: Refined Python code.
        """
        prompt = f"""
        Please refine the following Python code:

        {code}

        """

        if error_message:
            prompt += f"""
            The code produced the following error:
            {error_message}

            Please fix the error and improve the code.
            """

        if data_dict:
            prompt += f"""
            Data Dictionary:
            {data_dict}
            """

        if analysis_plan:
            prompt += f"""
            Complete Analysis Plan:
            {analysis_plan}
            """

        if data_dict_content:
            prompt += f"""
            Full Data Dictionary Content:
            {data_dict_content}
            """

        if additional_requirements:
            prompt += f"""
            Please also incorporate the following requirements:
            {additional_requirements}
            """

        prompt += f"""
        Remember to only use the following libraries in your code:
        {', '.join(ALLOWED_LIBRARIES)}
        """

        refined_code = self.api_client.call_api(prompt)
        return refined_code

    def add_to_notebook(self, analysis_name: str, code: str):
        """
        Adds a new cell to the Jupyter Notebook with the generated code.

        Args:
        analysis_name (str): The name of the analysis step.
        code (str): The generated Python code.
        """
        # Add a markdown cell with the analysis name
        self.notebook.cells.append(new_markdown_cell(f"## {analysis_name}"))
        
        # Add a code cell with the generated code
        self.notebook.cells.append(new_code_cell(code))
        
        # Save the notebook
        with open(self.notebook_path, 'w') as f:
            nbformat.write(self.notebook, f)

    def initialize_notebook(self):
        """
        Initializes the Jupyter Notebook with necessary setup code.
        """
        setup_code = f"""
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Load the data
        df = pd.read_csv('{config.PRODUCTION_CSV_PATH}')
        
        # Set up matplotlib to save figures instead of displaying them
        plt.switch_backend('agg')
        """
        
        self.notebook.cells.append(new_markdown_cell("# Automated Data Scientist Analysis"))
        self.notebook.cells.append(new_markdown_cell("## Setup"))
        self.notebook.cells.append(new_code_cell(setup_code))
        
        # Save the initialized notebook
        with open(self.notebook_path, 'w') as f:
            nbformat.write(self.notebook, f)

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    pass