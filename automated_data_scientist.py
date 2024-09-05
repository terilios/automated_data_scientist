import logging
import logging.config
from pathlib import Path
from typing import Dict, List, Any

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
    def __init__(self, production_csv_path: str = None, output_path: str = None, data_dict_path: str = None, api_type: str = None):
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
        self.code_generator = CodeGenerator(self.api_client)
        self.code_executor = CodeExecutor(self.output_path)
        self.result_interpreter = ResultInterpreter(self.api_client)

        # Initialize data structures
        self.analysis_plan = []
        self.completed_analyses = []
        self.key_findings = []

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

        # Execute analyses
        for i, analysis in enumerate(self.analysis_plan):
            if i >= config.MAX_ANALYSES:
                logging.info(f"Reached maximum number of analyses ({config.MAX_ANALYSES}). Stopping.")
                break

            logging.info(f"Executing analysis: {analysis['name']}")

            # Generate code
            code = self.code_generator.generate_code(analysis, self.data_handler.data_dict)

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
                        code = self.code_generator.refine_code(code, error_message=str(e))
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
            except Exception as e:
                logging.error(f"Error updating analysis plan: {str(e)}")
                logging.info("Continuing with the current plan...")

        # Generate final report
        self.generate_final_report()

        logging.info("Automated data science process completed")

    def generate_final_report(self):
        report = self.result_interpreter.generate_summary_report(self.completed_analyses, self.key_findings)
        report_path = self.output_path / f"final_report.{config.OUTPUT_FORMAT}"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logging.info(f"Final report generated and saved to {report_path}")

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    ads = AutomatedDataScientist()
    ads.run()