import logging
import logging.config
from pathlib import Path
from typing import Dict, List, Any
import shutil
from datetime import datetime

import config
from data_handling import DataHandler
from analysis_planning import AnalysisPlanner
from code_generation import CodeGenerator
from execution import CodeExecutor
from interpretation import ResultInterpreter
from api_client import APIClient

# Apply logging configuration
logging.config.dictConfig(config.LOGGING_CONFIG)

class AutomatedDataScientist:
    def __init__(self, production_csv_path: str = None, output_path: str = None, data_dict_path: str = None, api_type: str = None, code_generator: CodeGenerator = None):
        # Use config values, but allow overrides
        self.production_csv_path = Path(production_csv_path or config.PRODUCTION_CSV_PATH)
        self.output_path = Path(output_path or config.DEFAULT_OUTPUT_DIR)
        self.data_dict_path = Path(data_dict_path or config.DATA_DICT_PATH)
        self.api_type = api_type or config.DEFAULT_API_TYPE

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.api_client = APIClient(self.api_type)
        self.data_handler = DataHandler(self.data_dict_path, self.production_csv_path)
        self.analysis_planner = AnalysisPlanner(self.api_client)
        self.code_generator = code_generator or CodeGenerator(self.api_client)
        self.code_executor = CodeExecutor(self.output_path)
        self.result_interpreter = ResultInterpreter(self.api_client)

        # Initialize data structures
        self.analysis_plan = []
        self.completed_analyses = []
        self.key_findings = []
        self.analysis_plan_version = 0

        logging.info("Automated Data Scientist initialized")

    def run(self):
        logging.info("Starting automated data science process")

        # Initialize data
        self.data_handler.initialize_data()

        # Generate initial analysis plan
        self.analysis_plan = self.analysis_planner.generate_initial_plan(
            self.data_handler.data_dict,
            self.data_handler.production_data_sample
        )
        self.write_analysis_plan_to_markdown()

        # Enhance the analysis plan
        self.enhance_analysis_plan()

        # Execute analyses
        for i, analysis in enumerate(self.analysis_plan):
            if i >= config.MAX_ANALYSES:
                logging.info(f"Reached maximum number of analyses ({config.MAX_ANALYSES}). Stopping.")
                break

            logging.info(f"Executing analysis: {analysis['name']}")

            # Generate code
            code = self.code_generator.generate_code(
                analysis,
                self.data_handler.data_dict,
                self.analysis_plan,
                self.data_handler.data_dict_content
            )

            # Execute code with error handling and refinement
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    result, output, figure_paths = self.code_executor.execute_code(
                        code,
                        self.data_handler.production_data_sample
                    )
                    break
                except Exception as e:
                    logging.error(f"Error during code execution (attempt {attempt + 1}/{max_attempts}): {str(e)}")
                    if attempt < max_attempts - 1:
                        logging.info("Attempting to refine the code...")
                        code = self.code_generator.refine_code(
                            code,
                            error_message=str(e),
                            data_dict=self.data_handler.data_dict,
                            analysis_plan=self.analysis_plan,
                            data_dict_content=self.data_handler.data_dict_content
                        )
                    else:
                        logging.error("Max attempts reached. Moving to next analysis step.")
                        result, output, figure_paths = None, f"Execution failed: {str(e)}", []

            # Interpret results
            interpretation = self.result_interpreter.interpret_results(
                analysis,
                result,
                output,
                figure_paths,
                self.completed_analyses,
                self.key_findings
            )

            # Update analysis status and store results
            analysis['status'] = 'completed'
            analysis['result'] = result
            analysis['output'] = output
            analysis['figure_paths'] = figure_paths
            analysis['interpretation'] = interpretation

            self.completed_analyses.append(analysis)
            self.key_findings.extend(self.result_interpreter.extract_key_findings(interpretation))

            # Update analysis plan
            try:
                self.analysis_plan = self.analysis_planner.update_plan(
                    self.analysis_plan,
                    self.completed_analyses,
                    self.key_findings
                )
                self.write_analysis_plan_to_markdown()
            except Exception as e:
                logging.error(f"Error updating analysis plan: {str(e)}")
                logging.info("Continuing with the current plan...")

        # Generate final report
        self.generate_final_report()

        logging.info("Automated data science process completed")

    def enhance_analysis_plan(self):
        logging.info("Enhancing analysis plan based on data dictionary and initial plan")
        
        prompt = f"""
        Given the following data dictionary and initial analysis plan, please provide an enhanced and more comprehensive analysis plan. Consider the relationships between variables, potential advanced analyses, and any insights that could be derived from the data structure.

        Data Dictionary:
        {self.data_handler.data_dict_content}

        Initial Analysis Plan:
        {self.analysis_plan}

        Please provide an enhanced analysis plan that includes:
        1. More detailed steps for each analysis
        2. Additional analyses that could provide deeper insights
        3. Potential machine learning models or statistical tests that could be applied
        4. Suggestions for data visualization techniques
        5. Any data preprocessing or feature engineering steps that might be beneficial

        Return the enhanced plan as a list of dictionaries, where each dictionary represents an analysis step with keys for 'name', 'description', 'expected_insights', and 'status'.
        """

        try:
            enhanced_plan = self.api_client.call_api(prompt)
            self.analysis_plan = eval(enhanced_plan)  # Convert the string response to a Python object
            logging.info("Analysis plan successfully enhanced")
            self.write_analysis_plan_to_markdown()
        except Exception as e:
            logging.error(f"Error enhancing analysis plan: {str(e)}")
            logging.info("Continuing with the original plan")

    def generate_final_report(self):
        report = self.result_interpreter.generate_summary_report(self.completed_analyses, self.key_findings)
        file_extension = 'md' if config.OUTPUT_FORMAT.lower() == 'markdown' else 'html'
        report_path = self.output_path / f"final_report.{file_extension}"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logging.info(f"Final report generated and saved to {report_path}")

    def write_analysis_plan_to_markdown(self):
        self.analysis_plan_version += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_content = f"# Analysis Plan (Version {self.analysis_plan_version})\n\n"
        markdown_content += f"Last Updated: {current_time}\n\n"
        
        for i, analysis in enumerate(self.analysis_plan, 1):
            markdown_content += f"## {i}. {analysis['name']}\n\n"
            
            # Check if 'description' key exists, use a default value if it doesn't
            description = analysis.get('description', 'No description provided')
            markdown_content += f"**Description:** {description}\n\n"
            
            markdown_content += f"**Status:** {analysis['status']}\n\n"
            if 'expected_insights' in analysis:
                markdown_content += f"**Expected Insights:** {analysis['expected_insights']}\n\n"
            if 'result' in analysis:
                markdown_content += f"**Result:** {analysis['result']}\n\n"
            if 'interpretation' in analysis:
                markdown_content += f"**Interpretation:** {analysis['interpretation']}\n\n"
            markdown_content += "---\n\n"

        analysis_plan_path = self.output_path / "analysis_plan.md"
        
        # Create a backup of the existing file
        if analysis_plan_path.exists():
            backup_path = self.output_path / f"analysis_plan_backup_v{self.analysis_plan_version-1}.md"
            shutil.copy2(analysis_plan_path, backup_path)
            logging.info(f"Backup of previous analysis plan created at {backup_path}")

        try:
            with open(analysis_plan_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logging.info(f"Analysis plan (Version {self.analysis_plan_version}) written to {analysis_plan_path}")
        except Exception as e:
            logging.error(f"Error writing analysis plan to file: {str(e)}")
            # If writing fails, create an emergency backup
            emergency_backup_path = self.output_path / f"analysis_plan_emergency_backup_v{self.analysis_plan_version}.md"
            try:
                with open(emergency_backup_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                logging.info(f"Emergency backup of analysis plan created at {emergency_backup_path}")
            except Exception as e:
                logging.critical(f"Failed to create emergency backup of analysis plan: {str(e)}")

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    ads = AutomatedDataScientist()
    ads.run()