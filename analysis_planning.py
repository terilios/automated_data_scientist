import logging
import json
import ast
from typing import Dict, List, Any
from api_client import APIClient
import pandas as pd

class AnalysisPlanner:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def generate_initial_plan(self, data_dict: Dict, data_sample: Any) -> List[Dict]:
        """
        Generates a comprehensive analysis plan including at least 15 analyses based on the data dictionary and production data sample.
        
        Args:
        data_dict (Dict): The data dictionary describing the dataset.
        data_sample (Any): A sample of the production data (e.g., a pandas DataFrame).

        Returns:
        List[Dict]: A list of dictionaries, each representing a step in the analysis plan.
        """
        logging.info("Generating initial analysis plan")
        
        prompt = f"""
        Given the following data dictionary and production data sample characteristics:

        Data Dictionary:
        {json.dumps(data_dict, indent=2)}

        Production Data Sample Characteristics:
        - Number of rows: {len(data_sample)}
        - Number of columns: {len(data_sample.columns)}
        - Column names: {', '.join(data_sample.columns)}
        - Data types: {self.serialize_object(data_sample.dtypes.to_dict())}

        Please generate a comprehensive analysis plan with a minimum of 15 analyses steps. For each step, provide:
        1. A name for the analysis
        2. A brief description of what the analysis will do
        3. The expected insights this analysis might provide
        4. Any specific variables or methods to focus on

        Format your response as a list of dictionaries, where each dictionary represents an analysis step.
        Ensure that all property names and string values are enclosed in double quotes.
        """
        
        response = self.api_client.call_api(prompt)
        
        try:
            logging.debug("API response: %s", response)
            plan = self.parse_api_response(response)
            if not isinstance(plan, list):
                raise ValueError("API response is not a list")
            
            for i, step in enumerate(plan):
                if not isinstance(step, dict):
                    raise ValueError(f"Step {i} is not a dictionary")
                if 'name' not in step:
                    step['name'] = f"Analysis Step {i+1}"
                step['status'] = 'pending'
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.error("Failed to parse API response. Error: %s. Response content: %s", str(e), response)
            plan = self.get_default_analysis_plan()
        except Exception as e:
            logging.error("Unexpected error while processing API response: %s. Using default plan.", str(e))
            plan = self.get_default_analysis_plan()
        
        logging.info(f"Initial analysis plan generated with {len(plan)} steps")
        return plan

    def update_plan(self, current_plan: List[Dict], completed_analyses: List[Dict], key_findings: List[str]) -> List[Dict]:
        """
        Updates the analysis plan based on completed analyses and key findings.

        Args:
        current_plan (List[Dict]): The current analysis plan.
        completed_analyses (List[Dict]): List of completed analyses with their results.
        key_findings (List[str]): List of key findings from completed analyses.

        Returns:
        List[Dict]: An updated analysis plan.
        """
        logging.info("Updating analysis plan")

        summarized_data = self.summarize_data(current_plan, completed_analyses, key_findings)

        prompt = f"""
        Given the summarized current analysis plan, completed analyses, and key findings:

        {summarized_data}

        Please update the analysis plan. Consider:
        1. Removing completed analyses
        2. Adding new analyses based on the findings
        3. Modifying existing analyses if needed
        4. Prioritizing the most promising directions

        Provide the updated plan as a list of dictionaries, similar to the current plan format.
        Each dictionary should have the following keys: 'name', 'description', 'expected_insights', 'focus', 'status'.
        Ensure that all property names and string values are enclosed in double quotes.
        """

        response = self.api_client.call_api(prompt)

        try:
            logging.debug("API response: %s", response)
            updated_plan = self.parse_api_response(response)
            if not isinstance(updated_plan, list):
                raise ValueError("API response is not a list")
            
            for i, step in enumerate(updated_plan):
                if not isinstance(step, dict):
                    raise ValueError(f"Step {i} is not a dictionary")
                required_keys = ['name', 'description', 'expected_insights', 'focus', 'status']
                for key in required_keys:
                    if key not in step:
                        step[key] = f"Missing {key}"
                        logging.warning(f"Step {i} is missing the '{key}' key. Added a placeholder.")
        except (json.JSONDecodeError, ValueError) as e:
            logging.error("Failed to parse API response. Error: %s. Response content: %s", str(e), response)
            return current_plan
        except Exception as e:
            logging.error("Unexpected error while processing API response: %s. Keeping the current plan.", str(e))
            return current_plan

        logging.info(f"Analysis plan updated. New plan has {len(updated_plan)} steps")
        return updated_plan

    def parse_api_response(self, response: str) -> Any:
        """
        Parses the API response, handling both JSON and Python dictionary formats.

        Args:
        response (str): The API response string.

        Returns:
        Any: The parsed response.
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(response)
            except (ValueError, SyntaxError) as e:
                raise ValueError(f"Failed to parse API response: {str(e)}")

    def summarize_data(self, current_plan: List[Dict], completed_analyses: List[Dict], key_findings: List[str]) -> str:
        """
        Summarizes the current plan, completed analyses, and key findings to fit within API limits.

        Args:
        current_plan (List[Dict]): The current analysis plan.
        completed_analyses (List[Dict]): List of completed analyses with their results.
        key_findings (List[str]): List of key findings from completed analyses.

        Returns:
        str: A summarized version of the data.
        """
        max_length = 1000000  # Leave some buffer for other parts of the prompt

        summary = "Current Plan Summary:\n"
        for step in current_plan:
            summary += f"- {step['name']} (Status: {step['status']})\n"

        summary += "\nCompleted Analyses Summary:\n"
        for analysis in completed_analyses:
            summary += f"- {analysis['name']}: {analysis.get('interpretation', 'No interpretation available')[:200]}...\n"

        summary += "\nKey Findings:\n"
        for finding in key_findings:
            summary += f"- {finding[:200]}...\n"

        if len(summary) > max_length:
            summary = summary[:max_length] + "...(truncated)"

        return summary

    def get_default_analysis_plan(self) -> List[Dict]:
        """
        Provides a default analysis plan in case the API fails to generate one.

        Returns:
        List[Dict]: A default analysis plan.
        """
        return [
            {
                "name": "Data Quality Assessment",
                "description": "Assess the quality of the dataset, including missing values, duplicates, and outliers.",
                "expected_insights": "Understanding of data completeness and potential data quality issues.",
                "focus": "All variables",
                "status": "pending"
            },
            {
                "name": "Exploratory Data Analysis",
                "description": "Perform basic statistical analysis and create visualizations for key variables.",
                "expected_insights": "Initial understanding of variable distributions and relationships.",
                "focus": "Key numeric and categorical variables",
                "status": "pending"
            },
            {
                "name": "Correlation Analysis",
                "description": "Analyze correlations between numeric variables and associations between categorical variables.",
                "expected_insights": "Identification of strong relationships between variables.",
                "focus": "All numeric variables, key categorical variables",
                "status": "pending"
            },
            {
                "name": "Feature Importance Analysis",
                "description": "Use machine learning techniques to identify the most important features for predicting a target variable.",
                "expected_insights": "Understanding of which variables are most predictive of the target.",
                "focus": "All variables, with a specific target variable",
                "status": "pending"
            },
            {
                "name": "Time Series Analysis",
                "description": "If time-based data is present, analyze trends, seasonality, and autocorrelation.",
                "expected_insights": "Understanding of temporal patterns in the data.",
                "focus": "Time-based variables and related metrics",
                "status": "pending"
            }
        ]

    def serialize_object(self, obj):
        """
        Serialize object to JSON-compatible format.
        
        Args:
        obj: The object to serialize.

        Returns:
        A JSON-serializable representation of the object.
        """
        if isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: self.serialize_object(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.serialize_object(v) for v in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    pass