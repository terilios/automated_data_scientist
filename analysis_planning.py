import logging
import json
from pathlib import Path
from typing import Dict, List, Any
from api_client import APIClient
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import config

class AnalysisPlanner:
    def __init__(self, api_client: APIClient, output_path: str):
        self.api_client = api_client
        self.output_path = output_path
        self.plan_file = Path(self.output_path) / "analysis_plan.json"

    def generate_initial_plan(self, data_dict: Dict, data_sample: Any, full_data_row_count: int) -> List[Dict]:
        logging.info("Generating initial analysis plan")

        statistical_features = self.extract_statistical_features(data_sample)
        ranked_analyses = self.rank_analysis_steps(statistical_features)

        data_dict_str = json.dumps(data_dict, indent=2)
        data_dict_safe = data_dict_str.replace('"', '\"')

        prompt = f"""
        Given the following data dictionary and production data characteristics:

        Data Dictionary:
        {data_dict_safe}

        Production Data Characteristics:
        - Total number of rows: {full_data_row_count}
        - Number of columns: {len(data_sample.columns)}
        - Column names: {', '.join(data_sample.columns)}
        - Data types: {self.serialize_object(data_sample.dtypes.to_dict())}

        Generate a comprehensive analysis plan with up to {config.MAX_ANALYSES} steps. Each step should include:
        1. A name for the analysis
        2. A brief description of what the analysis will do
        3. The expected insights this analysis might provide
        4. Any specific variables or methods to focus on
        5. Set the status as "pending" for all steps

        Provide your response in the following JSON format:
        {{
            "analysis_steps": [
                {{
                    "name": "string",
                    "description": "string",
                    "expected_insights": "string",
                    "focus": "string",
                    "status": "pending"
                }}
            ]
        }}
        """
        
        logging.info(f"Prompt for initial plan generation:\n{prompt}")
        response = self.api_client.call_api(prompt, use_json_mode=True)
        plan_json = self.api_client.parse_json_response(response)
        plan = plan_json.get("analysis_steps", [])
        logging.info(f"Initial analysis plan: {json.dumps(plan, indent=2)}")
        return plan

    def enhance_analysis_plan(self, data_dict_content: str, initial_plan: List[Dict]) -> List[Dict]:
        logging.info("Enhancing analysis plan based on data dictionary and initial plan")
        
        prompt = f"""
        Provide your response in the following JSON format:
        {{
            "analysis_steps": [
                {{
                    "name": "string",
                    "description": "string",
                    "expected_insights": "string",
                    "focus": "string",
                    "status": "pending"
                }}
            ]
        }}
        
        Given the following data dictionary and initial analysis plan, please provide an enhanced and more comprehensive analysis plan. Consider the relationships between variables, potential advanced analyses, and any insights that could be derived from the data structure.

        Data Dictionary:
        {data_dict_content}

        Initial Analysis Plan:
        {initial_plan}

        Please provide an enhanced analysis plan that includes:
        1. More detailed steps for each analysis
        2. Additional analyses that could provide deeper insights
        3. Potential machine learning models or statistical tests that could be applied
        4. Suggestions for data visualization techniques
        5. Any data preprocessing or feature engineering steps that might be beneficial

        ONLY RETURN JSON FORMAT with no other ornamentation or expressed information.
        """

        try:
            response = self.api_client.call_api(prompt, use_json_mode=True)
            enhanced_plan_json = self.api_client.parse_json_response(response)
            enhanced_plan = enhanced_plan_json.get("analysis_steps", initial_plan)
            logging.info("Analysis plan successfully enhanced")
            return enhanced_plan
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing enhanced plan: {str(e)}. Check API response format.")
            return initial_plan
        except Exception as e:
            logging.error(f"Error enhancing analysis plan: {str(e)}")
            logging.info("Continuing with the original plan")
            return initial_plan

    def update_plan(self, current_plan: List[Dict], completed_analyses: List[Dict], key_findings: List[str], data_dict: Dict, data_sample: Any, full_data_row_count: int) -> List[Dict]:
        logging.info("Updating analysis plan")

        summarized_data = self.summarize_data(current_plan, completed_analyses, key_findings)
        data_dict_str = json.dumps(data_dict, indent=2)
        data_dict_safe = data_dict_str.replace('"', '\"')

        prompt = f"""
        Provide your response in the following JSON format:
        {{
            "analysis_steps": [
                {{
                    "name": "string",
                    "description": "string",
                    "expected_insights": "string",
                    "focus": "string",
                    "status": "string"
                }}
            ]
        }}
        
        Given the summarized current analysis plan, completed analyses, and key findings:

        {summarized_data}

        Expand on the analysis plan considering:
        1. Never remove existing analyses, only append new ones
        2. Add new analyses based on the findings
        3. Create new analyses that extend existing ones if needed
        4. Prioritize the most promising directions
        5. Ensure new analysis tasks have the status: "pending"

        Consider the following data context:

        Data Dictionary:
        {data_dict_safe}

        Production Data Characteristics:
        - Total number of rows: {full_data_row_count}
        - Number of columns: {len(data_sample.columns)}
        - Column names: {', '.join(data_sample.columns)}
        - Data types: {self.serialize_object(data_sample.dtypes.to_dict())}

        Provide your response in the following JSON format:
        {{
            "analysis_steps": [
                {{
                    "name": "string",
                    "description": "string",
                    "expected_insights": "string",
                    "focus": "string",
                    "status": "string"
                }}
            ]
        }}

        ONLY RETURN JSON FORMAT with no other ornamentation or expressed information.
        """

        logging.info(f"Prompt for plan update:\n{prompt}")
        response = self.api_client.call_api(prompt, use_json_mode=True)
        updated_plan_json = self.api_client.parse_json_response(response)
        updated_plan = updated_plan_json.get("analysis_steps", current_plan)
        logging.info(f"Updated analysis plan: {json.dumps(updated_plan, indent=2)}")
        return updated_plan

    def _get_analysis_plan(self, prompt: str) -> List[Dict]:
        response = self.api_client.call_api(prompt, use_json_mode=True)
        
        try:
            plan_data = self.api_client.parse_json_response(response)
            if isinstance(plan_data, str):
                plan_data = json.loads(plan_data)
            
            plan = plan_data.get("analysis_steps", [])
            
            logging.debug("API response: %s", json.dumps(plan, indent=2))
            
            if not isinstance(plan, list):
                raise ValueError("API response is not a list of analysis steps")
            
            for i, step in enumerate(plan):
                if not isinstance(step, dict):
                    raise ValueError(f"Step {i} is not a dictionary")
                if 'name' not in step or not step['name']:
                    step['name'] = f"Analysis Step {i+1}"
                if 'status' not in step:
                    step['status'] = 'pending'
            
            self.save_plan_to_file(plan)
            logging.info(f"Analysis plan generated/updated with {len(plan)} steps")
            return plan
        
        except (json.JSONDecodeError, ValueError) as e:
            logging.error("Failed to parse API response. Error: %s. Response content: %s", str(e), response)
            return []
        except Exception as e:
            logging.error("Unexpected error while processing API response: %s.", str(e))
            return []

    def save_plan_to_file(self, tasks: List[Dict]):
        serializable_tasks = json.loads(json.dumps(tasks, default=str))
        with open(self.plan_file, 'w', encoding='utf-8') as f:
            json.dump({"tasks": serializable_tasks}, f, indent=4)

    def summarize_data(self, current_plan: List[Dict], completed_analyses: List[Dict], key_findings: List[str]) -> str:
        max_length = 1000000
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

    def serialize_object(self, obj):
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

    def extract_statistical_features(self, data_sample: pd.DataFrame) -> pd.DataFrame:
        numeric_data = data_sample.select_dtypes(include=["number"])
        features = {
            'num_rows': len(data_sample),
            'num_columns': len(data_sample.columns),
            'mean_values': numeric_data.mean().to_dict(),
            'median_values': numeric_data.median().to_dict(),
            'std_values': numeric_data.std().to_dict(),
            'missing_values': data_sample.isnull().sum().to_dict(),
            'correlations': numeric_data.corr().to_dict()
        }
        return pd.DataFrame(features)

    def rank_analysis_steps(self, features: pd.DataFrame) -> List[str]:
        return features.columns[:5].tolist()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='analysis_planning.log')

    api_client = APIClient()
    planner = AnalysisPlanner(api_client, "output")
    
    data_dict = {"column1": {"type": "int"}, "column2": {"type": "str"}}
    data_sample = pd.DataFrame({"column1": [1, 2, 3], "column2": ["a", "b", "c"]})
    full_data_row_count = 1000000  # Example: assume the full dataset has 1 million rows
    
    initial_plan = planner.generate_initial_plan(data_dict, data_sample, full_data_row_count)
    print("Initial plan:", initial_plan)
    
    completed_analyses = [{"name": "Test Analysis", "interpretation": "This is a test interpretation"}]
    key_findings = ["Test finding 1", "Test finding 2"]
    updated_plan = planner.update_plan(initial_plan, completed_analyses, key_findings, data_dict, data_sample, full_data_row_count)
    print("Updated plan:", updated_plan)
