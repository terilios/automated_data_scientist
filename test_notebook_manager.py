import unittest
from unittest.mock import patch, mock_open, MagicMock
import nbformat
from notebook_manager import NotebookManager

class TestNotebookManager(unittest.TestCase):
    def setUp(self):
        self.notebook_path = 'test_notebook.ipynb'
        with patch('notebook_manager.config.NOTEBOOK_PATH', self.notebook_path):
            self.notebook_manager = NotebookManager()

    @patch('nbformat.writes')
    def test_save_notebook(self, mock_writes):
        mock_writes.return_value = '{"cells": []}'
        
        with patch('builtins.open', mock_open()) as mock_file:
            self.notebook_manager.save_notebook()

        mock_writes.assert_called_once_with(self.notebook_manager.notebook)
        mock_file.assert_called_once_with(self.notebook_path, 'w', encoding='utf-8')
        mock_file().write.assert_called_once_with('{"cells": []}')

    def test_add_markdown_cell(self):
        initial_cell_count = len(self.notebook_manager.notebook.cells)
        markdown_content = "Test Markdown"
        self.notebook_manager.add_markdown_cell(markdown_content)
        
        self.assertEqual(len(self.notebook_manager.notebook.cells), initial_cell_count + 1)
        self.assertEqual(self.notebook_manager.notebook.cells[-1].cell_type, 'markdown')
        self.assertEqual(self.notebook_manager.notebook.cells[-1].source, f"## {markdown_content}")

    def test_add_code_cell(self):
        initial_cell_count = len(self.notebook_manager.notebook.cells)
        code_content = "print('Hello, World!')"
        self.notebook_manager.add_code_cell(code_content)
        
        self.assertEqual(len(self.notebook_manager.notebook.cells), initial_cell_count + 1)
        self.assertEqual(self.notebook_manager.notebook.cells[-1].cell_type, 'code')
        self.assertEqual(self.notebook_manager.notebook.cells[-1].source, code_content)

    def test_add_analysis_step(self):
        initial_cell_count = len(self.notebook_manager.notebook.cells)
        step_name = "Test Step"
        step_description = "This is a test step"
        step_goals = "To test the add_analysis_step method"
        code = "print('Test code')"

        self.notebook_manager.add_analysis_step(step_name, step_description, step_goals, code)

        self.assertEqual(len(self.notebook_manager.notebook.cells), initial_cell_count + 6)
        self.assertEqual(self.notebook_manager.notebook.cells[-6].cell_type, 'markdown')
        self.assertEqual(self.notebook_manager.notebook.cells[-5].cell_type, 'markdown')
        self.assertEqual(self.notebook_manager.notebook.cells[-4].cell_type, 'markdown')
        self.assertEqual(self.notebook_manager.notebook.cells[-3].cell_type, 'markdown')
        self.assertEqual(self.notebook_manager.notebook.cells[-2].cell_type, 'markdown')
        self.assertEqual(self.notebook_manager.notebook.cells[-1].cell_type, 'code')

        self.assertIn(step_name, self.notebook_manager.notebook.cells[-6].source)
        self.assertIn("Description:", self.notebook_manager.notebook.cells[-5].source)
        self.assertIn(step_description, self.notebook_manager.notebook.cells[-4].source)
        self.assertIn("Goals:", self.notebook_manager.notebook.cells[-3].source)
        self.assertIn(step_goals, self.notebook_manager.notebook.cells[-2].source)
        self.assertEqual(self.notebook_manager.notebook.cells[-1].source, code)

if __name__ == '__main__':
    unittest.main()