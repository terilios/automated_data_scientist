import logging
from typing import Dict, Any, List
from api_client import APIClient
import config
from config import ALLOWED_LIBRARIES
import ast
import traceback

class CodeGenerator:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def generate_code(self, analysis: Dict[str, Any], data_dict: Dict[str, Any], analysis_plan: List[Dict[str, Any]], data_dict_content: str) -> str:
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
           df = pd.read_csv(config.PRODUCTION_CSV_PATH)
        10. Consider the complete analysis plan when generating code for this step
        11. You may only use the following libraries in your code:
            {', '.join(ALLOWED_LIBRARIES)}
        12. Ensure plots are well-labeled, including titles, axis labels, and legends where appropriate.
        13. Test for data readiness before plotting and consider showing plots inline if necessary for review.

        Return only the well formed Python code, without any explanations or markdown formatting.
        """

        try:
            code = self.api_client.call_api(prompt)
            logging.info(f"Code generated for analysis: {analysis['name']}")
            
            # Sanitize and prepare code
            sanitized_code = self.sanitize_code(code)
            parameterized_code = self.parameterize_code(sanitized_code)
            
            return parameterized_code
        except Exception as e:
            logging.error(f"Error generating code for analysis {analysis['name']}: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    def sanitize_code(self, code: str) -> str:
        try:
            # Handle characters that might be formatted wrongly
            sanitized_code = code.replace('`', "'")
            # Remove Python code block markers
            sanitized_code = sanitized_code.replace("'''python", "").replace("'''", "")
            
            # Parse the code and fix any indentation issues
            try:
                tree = ast.parse(sanitized_code)
                sanitized_code = ast.unparse(tree)
            except IndentationError as ie:
                logging.error("Indentation error detected: attempting automatic correction.")
                # Implement correction logic if needed
                raise ie
            
            # Ensure code cells end properly
            if not sanitized_code.endswith('\n'):
                sanitized_code += '\n'
            return sanitized_code
        except Exception as e:
            logging.error(f"Error sanitizing code: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    def parameterize_code(self, code: str) -> str:
        try:
            parameterized_code = code.replace('data.plot(', 'plot_data(data, plot_type=plot_type, ')
            return parameterized_code
        except Exception as e:
            logging.error(f"Error parameterizing code: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    def generate_code_structure(self, analysis: Dict[str, Any]) -> str:
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

        try:
            structure = self.api_client.call_api(prompt)
            return structure
        except Exception as e:
            logging.error(f"Error generating code structure for analysis {analysis['name']}: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    def refine_code(self, code: str, error_message: str = None, data_dict: Dict[str, Any] = None, analysis_plan: List[Dict[str, Any]] = None, data_dict_content: str = None, additional_requirements: str = None) -> str:
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

        try:
            refined_code = self.api_client.call_api(prompt)
            sanitized_code = self.sanitize_code(refined_code)
            parameterized_code = self.parameterize_code(sanitized_code)
            return parameterized_code
        except Exception as e:
            logging.error(f"Error refining code: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    def validate_code(self, code: str) -> bool:
        """
        Validate the generated code for potential security issues.
        """
        forbidden_functions = ['eval', 'exec', 'os.system', 'subprocess.run', '__import__']
        for func in forbidden_functions:
            if func in code:
                logging.warning(f"Potential security risk: {func} found in generated code")
                return False
        return True

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='code_generation.log')

    # This block is for testing purposes
    api_client = APIClient()
    code_gen = CodeGenerator(api_client)
    
    # Mock analysis for testing
    mock_analysis = {
        "name": "Test Analysis",
        "description": "This is a test analysis",
        "expected_insights": "We expect to see some interesting patterns",
        "focus": ["column1", "column2"]
    }
    
    mock_data_dict = {"column1": {"type": "int"}, "column2": {"type": "str"}}
    mock_analysis_plan = [mock_analysis]
    mock_data_dict_content = "Column1: integer\nColumn2: string"
    
    try:
        generated_code = code_gen.generate_code(mock_analysis, mock_data_dict, mock_analysis_plan, mock_data_dict_content)
        print("Generated Code:")
        print(generated_code)
        
        is_valid = code_gen.validate_code(generated_code)
        print(f"Is code valid? {is_valid}")
        
        if not is_valid:
            refined_code = code_gen.refine_code(generated_code, additional_requirements="Remove any potentially unsafe functions.")
            print("Refined Code:")
            print(refined_code)
    except Exception as e:
        logging.error(f"Error in code generation test: {str(e)}")
        logging.error(traceback.format_exc())
