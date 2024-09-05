import logging
from typing import Dict, Any
from api_client import APIClient
import config

class CodeGenerator:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def generate_code(self, analysis: Dict[str, Any], data_dict: Dict[str, Any]) -> str:
        """
        Generates Python code for a given analysis step.

        Args:
        analysis (Dict[str, Any]): The analysis step details.
        data_dict (Dict[str, Any]): The data dictionary describing the dataset.

        Returns:
        str: Generated Python code for the analysis.
        """
        logging.info(f"Generating code for analysis: {analysis['name']}")

        prompt = f"""
        Generate Python code for the following analysis:

        {analysis}

        Data Dictionary:
        {data_dict}

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

        Provide only the Python code, without any explanations or markdown formatting.
        """

        code = self.api_client.call_api(prompt)
        logging.info(f"Code generated for analysis: {analysis['name']}")
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

    def refine_code(self, code: str, error_message: str = None, additional_requirements: str = None) -> str:
        """
        Refines the generated code based on error messages or additional requirements.

        Args:
        code (str): The original generated code.
        error_message (str, optional): Any error message produced when running the code.
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

        if additional_requirements:
            prompt += f"""
            Please also incorporate the following requirements:
            {additional_requirements}
            """

        refined_code = self.api_client.call_api(prompt)
        return refined_code

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    pass