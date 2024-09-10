import logging
import json
from pathlib import Path
from typing import Dict, List, Any
import time
import traceback

import config
from data_handling import DataHandler
from analysis_planning import AnalysisPlanner
from code_generation import CodeGenerator
from execution import CodeExecutor
from interpretation import ResultInterpreter
from api_client import APIClient
from notebook_manager import NotebookManager
import pandas as pd  # Added to read the full CSV file

class AutomatedDataScientist:
    def __init__(self, production_csv_path: str = None, output_path: str = None, data_dict_path: str = None, 
                 api_type: str = None, code_generator: CodeGenerator = None, notebook_manager: NotebookManager = None,
                 data_handler: DataHandler = None):
        # Use config values, but allow overrides
        self.production_csv_path = Path(production_csv_path or config.PRODUCTION_CSV_PATH)
        self.output_path = Path(output_path or config.DEFAULT_OUTPUT_DIR)
        self.data_dict_path = Path(data_dict_path or config.DATA_DICT_PATH)
        self.api_type = api_type or config.DEFAULT_API_TYPE

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.api_client = APIClient(self.api_type)
        self.data_handler = data_handler or DataHandler(self.data_dict_path, self.production_csv_path)
        self.analysis_planner = AnalysisPlanner(self.api_client, self.output_path)
        self.code_generator = code_generator or CodeGenerator(self.api_client)
        self.code_executor = CodeExecutor(self.output_path)
        self.result_interpreter = ResultInterpreter(self.api_client)
        self.notebook_manager = notebook_manager or NotebookManager(config.NOTEBOOK_PATH)

        # Initialize data structures
        self.analysis_plan = []
        self.completed_analyses = []
        self.key_findings = []
        self.analysis_plan_version = 0

        logging.info("Automated Data Scientist initialized")

    def run(self):
        logging.info("Starting automated data science process")

        try:
            # Start new analysis (removed resume feature)
            logging.info("Starting new analysis")
            self.initialize_data_and_plan()

            # Execute analyses
            for i, analysis in enumerate(self.analysis_plan):
                if i >= config.MAX_ANALYSES:
                    logging.info(f"Reached maximum number of analyses ({config.MAX_ANALYSES}). Stopping.")
                    break

                if analysis['status'] == 'completed':
                    logging.info(f"Skipping completed analysis: {analysis['name']}")
                    continue

                logging.info(f"Executing analysis {i+1}/{len(self.analysis_plan)}: {analysis['name']}")

                self.execute_single_analysis(analysis)

                # Optionally save progress after each analysis (can be commented out if not needed)
                # self.save_progress()

            # Generate final report
            logging.info("Generating final report...")
            self.generate_final_report()

            # Save the notebook
            self.notebook_manager.save_notebook()
            logging.info("Notebook has been saved with all analysis steps.")

            logging.info("Automated data science process completed")

        except Exception as e:
            logging.error(f"An error occurred during the automated data science process: {str(e)}")
            logging.error(traceback.format_exc())
            # Attempt to save any progress made
            # self.save_progress() (optionally remove this if saving progress is not desired)
            raise

    def initialize_data_and_plan(self):
        # Initialize data
        logging.info("Initializing data...")
        self.data_handler.initialize_data()

        # Determine the full data row count
        logging.info("Reading full dataset to determine row count...")
        try:
            full_data = pd.read_csv(self.production_csv_path)
            full_data_row_count = full_data.shape[0]
            logging.info(f"Full dataset has {full_data_row_count} rows")
        except Exception as e:
            logging.error(f"Error reading full dataset: {str(e)}")
            raise

        # Generate the initial analysis plan
        logging.info("Generating initial analysis plan...")
        self.analysis_plan = self.analysis_planner.generate_initial_plan(
            self.data_handler.data_dict,
            self.data_handler.production_data_sample,
            full_data_row_count
        )
        logging.info(f"Initial analysis plan generated: {len(self.analysis_plan)} steps")

        # Enhance the analysis plan
        logging.info("Enhancing analysis plan...")
        self.analysis_plan = self.analysis_planner.enhance_analysis_plan(
            self.data_handler.data_dict_content,
            self.analysis_plan
        )
        logging.info("Analysis plan enhanced")

    def execute_single_analysis(self, analysis: Dict[str, Any]):
        # Generate code
        logging.info("Generating code...")
        start_time = time.time()
        code = self.code_generator.generate_code(
            analysis,
            self.data_handler.data_dict,
            self.analysis_plan,
            self.data_handler.data_dict_content
        )
        logging.info(f"Code generation took {time.time() - start_time:.2f} seconds")

        # Execute code with error handling and refinement
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                logging.info(f"Executing code (attempt {attempt+1}/{max_attempts})...")
                start_time = time.time()
                result, output, figure_paths = self.code_executor.execute_code(
                    code,
                    self.data_handler.production_data_sample
                )
                logging.info(f"Code execution took {time.time() - start_time:.2f} seconds")

                # Additional verification of generated plots
                for path in figure_paths:
                    assert Path(path).is_file(), f"Expected plot file not created: {path}"
                # Update status to completed
                analysis['status'] = 'completed'
                logging.info(f"Updated status for {analysis['name']} to completed.")
                break
            except Exception as e:
                logging.error(f"Error during code execution (attempt {attempt + 1}/{max_attempts}): {str(e)}")
                logging.error(traceback.format_exc())
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
        logging.info("Interpreting results...")
        start_time = time.time()
        interpretation = self.result_interpreter.interpret_results(
            analysis,
            result,
            output,
            figure_paths,
            self.completed_analyses,
            self.key_findings
        )
        logging.info(f"Result interpretation took {time.time() - start_time:.2f} seconds")

        # Store results
        analysis['result'] = result
        analysis['output'] = output
        analysis['figure_paths'] = figure_paths
        analysis['interpretation'] = interpretation

        self.completed_analyses.append(analysis)
        self.key_findings.extend(self.result_interpreter.extract_key_findings(interpretation))

        # Add analysis step to notebook
        self.notebook_manager.add_analysis_step(
            analysis['name'],
            analysis.get('description', 'No description available.'),
            analysis.get('expected_insights', 'No goals specified.'),
            code
        )

        self.analysis_planner.save_plan_to_file(self.analysis_plan)  # Save updated status

        # Update analysis plan
        try:
            logging.info("Updating analysis plan...")
            start_time = time.time()
            self.analysis_plan = self.analysis_planner.update_plan(
                self.analysis_plan,
                self.completed_analyses,
                self.key_findings,
                self.data_handler.data_dict,
                self.data_handler.production_data_sample,
                self.data_handler.production_data_sample.shape[0]
            )
            logging.info(f"Analysis plan update took {time.time() - start_time:.2f} seconds")
        except Exception as e:
            logging.error(f"Error updating analysis plan: {str(e)}")
            logging.error(traceback.format_exc())
            logging.info("Continuing with the current plan...")

    def generate_final_report(self):
        report = self.result_interpreter.generate_summary_report(self.completed_analyses, self.key_findings)
        file_extension = 'md' if config.OUTPUT_FORMAT.lower() == 'markdown' else 'html'
        report_path = self.output_path / f"final_report.{file_extension}"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logging.info(f"Final report generated and saved to {report_path}")

    # Removed save_progress and load_progress methods

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='automated_data_scientist.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # This block is for testing purposes and will not be executed when imported
    try:
        ads = AutomatedDataScientist()
        ads.run()
    except Exception as e:
        logging.critical(f"Critical error in main execution: {str(e)}")
        logging.critical(traceback.format_exc())
