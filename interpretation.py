import logging
import base64
import gzip
import pandas as pd
from typing import Dict, Any, List
from api_client import APIClient
import json
import traceback
from pathlib import Path

class ResultInterpreter:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler("debug.log"),
                                logging.StreamHandler()
                            ])

    def encode_image(self, file_path: str) -> bytes:
        try:
            with open(file_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read())
                compressed = gzip.compress(encoded)
                return compressed
        except Exception as e:
            logging.error(f"Error encoding image {file_path}: {str(e)}")
            return b""

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

        try:
            data_dictionary_content = self.read_data_dictionary()
            production_data_sample = self.read_production_data_sample()

            important_figure_paths = figure_paths[:1]
            encoded_images = [self.encode_image(path) for path in important_figure_paths] if important_figure_paths else []

            analysis_summary = analysis.get("summary", "No summary available")[:1000]
            key_points = "; ".join(key_findings[:5])

            prompt = f"""
            Analysis Summary (Top Points):
            {analysis_summary}
            
            Key Findings Detailed (Up to 5 insights): {key_points}

            Data Dictionary Overview: 
            {data_dictionary_content}

            Sample Data from Production Data:
            {production_data_sample}

            Visuals: Compressed Base64

            Provide nuanced interpretation focusing on insights and critical recommendations.
            """
            
            interpretation = self.api_client.call_api(prompt)

            logging.info("API Response: %s", interpretation)
            print("API Response:", interpretation)

            if "compressed" not in interpretation.lower():
                logging.warning("The API response did not acknowledge compressed image data.")

            if "recommendations" not in interpretation.lower():
                logging.warning("The API response may lack specific recommendations on insights.")

            logging.info(f"Results interpretation completed for analysis: {analysis['name']}")
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
        {json.dumps(completed_analyses, indent=2)}

        Key Findings:
        {json.dumps(key_findings, indent=2)}

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
    mock_figure_paths = ["test_figure1.png", "test_figure2.png"]
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
