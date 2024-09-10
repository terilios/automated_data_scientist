import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import pandas as pd
import json
from automated_data_scientist import AutomatedDataScientist

class TestAutomatedDataScientist(unittest.TestCase):
    def setUp(self):
        self.test_csv_path = 'test_data.csv'
        self.test_output_path = 'test_output'
        self.test_data_dict_path = 'test_data_dict.json'

    @patch('automated_data_scientist.DataHandler')
    @patch('automated_data_scientist.AnalysisPlanner')
    @patch('automated_data_scientist.CodeGenerator')
    @patch('automated_data_scientist.CodeExecutor')
    @patch('automated_data_scientist.ResultInterpreter')
    @patch('automated_data_scientist.NotebookManager')
    def test_initialization(self, mock_notebook_manager, mock_result_interpreter, 
                            mock_code_executor, mock_code_generator, 
                            mock_analysis_planner, mock_data_handler):
        ads = AutomatedDataScientist(
            production_csv_path=self.test_csv_path,
            output_path=self.test_output_path,
            data_dict_path=self.test_data_dict_path
        )
        
        self.assertEqual(ads.production_csv_path, Path(self.test_csv_path))
        self.assertEqual(ads.output_path, Path(self.test_output_path))
        self.assertEqual(ads.data_dict_path, Path(self.test_data_dict_path))
        
        mock_data_handler.assert_called_once()
        mock_analysis_planner.assert_called_once()
        mock_code_generator.assert_called_once()
        mock_code_executor.assert_called_once()
        mock_result_interpreter.assert_called_once()
        mock_notebook_manager.assert_called_once()

    @patch('automated_data_scientist.DataHandler')
    @patch('automated_data_scientist.AnalysisPlanner')
    @patch('automated_data_scientist.CodeGenerator')
    @patch('automated_data_scientist.CodeExecutor')
    @patch('automated_data_scientist.ResultInterpreter')
    @patch('automated_data_scientist.NotebookManager')
    @patch('pandas.read_csv')
    def test_run_method(self, mock_read_csv, mock_notebook_manager, mock_result_interpreter, 
                        mock_code_executor, mock_code_generator, 
                        mock_analysis_planner, mock_data_handler):
        mock_df = MagicMock(spec=pd.DataFrame)
        mock_df.shape = (100, 10)
        mock_read_csv.return_value = mock_df

        ads = AutomatedDataScientist(
            production_csv_path=self.test_csv_path,
            output_path=self.test_output_path,
            data_dict_path=self.test_data_dict_path
        )
        
        mock_data_handler().initialize_data.return_value = None
        mock_data_handler().production_data_sample = mock_df
        mock_data_handler().data_dict = {}
        mock_data_handler().data_dict_content = ''
        mock_analysis_planner().generate_initial_plan.return_value = [{'name': 'Test Analysis'}]
        mock_analysis_planner().enhance_analysis_plan.return_value = [{'name': 'Enhanced Test Analysis'}]
        mock_code_generator().generate_code.return_value = 'print("Test")'
        mock_code_executor().execute_code.return_value = ('Result', 'Output', [])
        mock_result_interpreter().interpret_results.return_value = 'Interpretation'
        mock_result_interpreter().extract_key_findings.return_value = ['Finding']
        mock_result_interpreter().generate_summary_report.return_value = "Mock Report"

        with patch('builtins.open', mock_open()) as mock_file:
            ads.run()
        
        mock_data_handler().initialize_data.assert_called_once()
        mock_analysis_planner().generate_initial_plan.assert_called_once()
        mock_analysis_planner().enhance_analysis_plan.assert_called_once()
        mock_code_generator().generate_code.assert_called_once()
        mock_code_executor().execute_code.assert_called_once()
        mock_result_interpreter().interpret_results.assert_called_once()
        mock_notebook_manager().add_analysis_step.assert_called_once()
        mock_notebook_manager().save_notebook.assert_called_once()

    @patch('pandas.read_csv')
    def test_full_data_row_count(self, mock_read_csv):
        mock_df = MagicMock(spec=pd.DataFrame)
        mock_df.shape = (100, 10)
        mock_read_csv.return_value = mock_df

        with patch('automated_data_scientist.AnalysisPlanner') as mock_planner, \
             patch('automated_data_scientist.DataHandler') as mock_data_handler, \
             patch('builtins.open', mock_open()):
            mock_data_handler().production_data_sample = mock_df
            ads = AutomatedDataScientist(production_csv_path=self.test_csv_path)
            ads.run()

            mock_read_csv.assert_called_once_with(Path(self.test_csv_path))
            mock_planner().generate_initial_plan.assert_called_once()
            self.assertEqual(mock_planner().generate_initial_plan.call_args[0][2], 100)

    @patch('automated_data_scientist.CodeExecutor')
    @patch('pandas.read_csv')
    @patch('automated_data_scientist.AnalysisPlanner')
    @patch('automated_data_scientist.DataHandler')
    @patch('automated_data_scientist.CodeGenerator')
    @patch('automated_data_scientist.ResultInterpreter')
    @patch('automated_data_scientist.NotebookManager')
    def test_code_execution_retry(self, mock_notebook_manager, mock_result_interpreter, 
                                  mock_code_generator, mock_data_handler, mock_analysis_planner, 
                                  mock_read_csv, mock_code_executor):
        mock_df = MagicMock(spec=pd.DataFrame)
        mock_df.shape = (100, 10)
        mock_read_csv.return_value = mock_df

        ads = AutomatedDataScientist(production_csv_path=self.test_csv_path)
        
        mock_data_handler().production_data_sample = mock_df
        mock_data_handler().data_dict = {}
        mock_data_handler().data_dict_content = ''
        
        initial_plan = [{'name': 'Test Analysis', 'status': 'pending'}]
        mock_analysis_planner().generate_initial_plan.return_value = initial_plan
        mock_analysis_planner().enhance_analysis_plan.return_value = initial_plan
        mock_analysis_planner().update_plan.return_value = initial_plan
        
        mock_code_generator().generate_code.return_value = 'print("Test")'
        
        mock_result_interpreter().interpret_results.return_value = 'Interpretation'
        mock_result_interpreter().extract_key_findings.return_value = ['Finding']
        mock_result_interpreter().generate_summary_report.return_value = "Mock Report"

        def execute_code_side_effect(*args, **kwargs):
            if mock_code_executor().execute_code.call_count < 3:
                raise Exception(f"Failure {mock_code_executor().execute_code.call_count}")
            else:
                initial_plan[0]['status'] = 'completed'
                return ('Result', 'Output', [])

        mock_code_executor().execute_code.side_effect = execute_code_side_effect

        with patch('builtins.open', mock_open()):
            ads.run()

        self.assertEqual(mock_code_executor().execute_code.call_count, 3)
        self.assertEqual(initial_plan[0]['status'], 'completed')

    def test_save_progress(self):
        ads = AutomatedDataScientist(output_path=self.test_output_path)
        ads.analysis_plan = [{'name': 'Test Analysis'}]
        ads.completed_analyses = [{'name': 'Completed Analysis'}]
        ads.key_findings = ['Key Finding']

        mock_open_func = mock_open()
        with patch('builtins.open', mock_open_func):
            ads.save_progress()

        mock_open_func.assert_called_once_with(Path(self.test_output_path) / "progress_snapshot.json", 'w', encoding='utf-8')
        handle = mock_open_func()
        handle.write.assert_called()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn('"analysis_plan":', written_data)
        self.assertIn('"completed_analyses":', written_data)
        self.assertIn('"key_findings":', written_data)

    @patch('automated_data_scientist.CodeGenerator')
    def test_code_generation(self, mock_code_generator):
        ads = AutomatedDataScientist(production_csv_path=self.test_csv_path)
        
        ads.data_handler = MagicMock()
        ads.data_handler.data_dict = {'column1': 'int', 'column2': 'string'}
        ads.data_handler.data_dict_content = 'Sample data dictionary content'
        ads.analysis_plan = [{'name': 'Test Analysis', 'type': 'descriptive'}]

        mock_code_generator().generate_code.return_value = 'print("Generated Code")'

        code = ads.code_generator.generate_code(
            ads.analysis_plan[0],
            ads.data_handler.data_dict,
            ads.analysis_plan,
            ads.data_handler.data_dict_content
        )

        mock_code_generator().generate_code.assert_called_once_with(
            ads.analysis_plan[0],
            ads.data_handler.data_dict,
            ads.analysis_plan,
            ads.data_handler.data_dict_content
        )

        self.assertEqual(code, 'print("Generated Code")')

if __name__ == '__main__':
    unittest.main()