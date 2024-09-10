import logging
import base64
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from api_client import APIClient
import json
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.to_list()
        elif isinstance(obj, pd.core.dtypes.base.ExtensionDtype):
            return str(obj)
        elif pd.api.types.is_categorical_dtype(obj):
            return str(obj)
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, pd.Timedelta):
            return obj.total_seconds()
        return super(NumpyEncoder, self).default(obj)

class ResultInterpreter:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.api_key = os.getenv("OPENAI_API_KEY")
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler("debug.log"),
                                logging.StreamHandler()
                            ])

    def encode_image(self, file_path: str) -> bytes:
        try:
            with open(file_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded
        except Exception as e:
            logging.error(f"Error encoding image {file_path}: {str(e)}")
            return ""

    def read_data_dictionary(self) -> str:
        try:
            with open("data/data_dictionary.md", "r") as file:
                return file.read()
        except FileNotFoundError:
            logging.error("Data dictionary file not found.")
            return ""
        except Exception as e:
            logging.error(f"Error reading data dictionary: {str(e)}")
            return ""

    def read_production_data_sample(self) -> str:
        try:
            df = pd.read_csv("data/production_data.csv")
            return df.head(10).to_string(index=False)
        except FileNotFoundError:
            logging.error("Production data file not found.")
            return ""
        except Exception as e:
            logging.error(f"Error reading production data: {str(e)}")
            return ""

    def interpret_results(self, analysis: Dict[str, Any], result: Any, output: str, figure_paths: List[str], completed_analyses: List[Dict], key_findings: List[str]) -> str:
        logging.info(f"Interpreting results for analysis: {analysis['name']}")

        if not figure_paths or len(figure_paths) == 0:
            logging.error("No figure paths provided for image analysis.")
            return "Error: No figure paths provided for image analysis."

        try:
            # Contextual information
            analysis_summary = analysis.get("summary", "No summary available")[:1000]
            
            # Read data dictionary content
            data_dictionary_content = self.read_data_dictionary()

            # Encode the first image
            base64_image = self.encode_image(figure_paths[0])
            base64_prefixed_image = f"data:image/png;base64,{base64_image}"

            # Prepare messages payload
            messages = [
                {
                    "role": "system",
                    "content": "You are an image analysis system. Analyze the following image and provide detailed insights. Consider the analysis summary and data dictionary for further context."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analysis Summary: {analysis_summary}"},
                        {"type": "text", "text": "Analyze this image."},
                        {"type": "text", "text": f"Data Dictionary: {data_dictionary_content[:2000]}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_prefixed_image
                            }
                        }
                    ]
                }
            ]

            # Call API using self.api_client
            response = self.api_client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=messages,
                max_tokens=300
            )
            
            interpretation = response.choices[0].message.content
            logging.info("API Response: %s", interpretation)
            return interpretation

        except Exception as e:
            logging.error(f"Error interpreting results for analysis {analysis['name']}: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return f"Error in interpretation: {str(e)}"

    def extract_key_findings(self, interpretation: str) -> List[str]:
        prompt = f"""
        Given the following interpretation of an analysis:

        {interpretation}

        Extract key findings that are concise and critical to project success. Each finding should:
        1. Be data-driven
        2. Align with the project's strategic goals

        Provide the findings as a list, formatted with a dash (-) for each.
        """
        
        try:
            findings = self.api_client.call_api(prompt)
            key_findings = [finding.strip()[2:] for finding in findings.split('\n') if finding.strip().startswith('-')]
            logging.info("Extracted key findings successfully.")
            return key_findings
        except Exception as e:
            logging.error(f"Error extracting key findings: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return []

    def generate_summary_report(self, completed_analyses: List[Dict], key_findings: List[str]) -> str:
        prompt = f"""
        Generate a comprehensive project report including the following:

        Completed Analyses:
        {json.dumps(completed_analyses, indent=2, cls=NumpyEncoder)}

        Key Findings:
        {json.dumps(key_findings, indent=2, cls=NumpyEncoder)}

        Report must include:
        1. Executive Summary
        2. Detailed Analysis Results
        3. Key Insights and Based Recommendations
        4. Conclusions and Future Suggestions
        
        Format the report using Markdown with clear headings.
        """
        
        try:
            report = self.api_client.call_api(prompt)
            logging.info("Generated summary report successfully.")
            return report
        except Exception as e:
            logging.error(f"Error generating summary report: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return "Error generating report."

    def save_report(self, report: str, output_path: Path):
        try:
            report_path = output_path / "final_report.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logging.info(f"Report saved to {report_path}")
        except Exception as e:
            logging.error(f"Error saving report: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='interpretation.log')

    # This block is for testing purposes
    api_client = APIClient()
    interpreter = ResultInterpreter(api_client)
    
    # Mock data for testing
    mock_analysis = {
        "name": "Test Analysis",
        "summary": "This is a test analysis summary"
    }
    mock_result = "Test result"
    mock_output = "Test output"
    mock_figure_paths = ["output/figures/event_date_distribution.png"]
    mock_completed_analyses = [mock_analysis]
    mock_key_findings = ["Finding 1", "Finding 2"]

    try:
        # Test interpret_results
        interpretation = interpreter.interpret_results(
            mock_analysis, mock_result, mock_output, mock_figure_paths,
            mock_completed_analyses, mock_key_findings
        )
        print("Interpretation:", interpretation)

        # Test extract_key_findings
        key_findings = interpreter.extract_key_findings(interpretation)
        print("Key Findings:", key_findings)

        # Test generate_summary_report
        report = interpreter.generate_summary_report(mock_completed_analyses, key_findings)
        print("Summary Report:", report)

        # Test save_report
        output_path = Path("test_output")
        output_path.mkdir(exist_ok=True)
        interpreter.save_report(report, output_path)

    except Exception as e:
        logging.error(f"Error in interpretation test: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
