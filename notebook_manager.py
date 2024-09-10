import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import logging
from typing import Dict, Any
import json
import config

class NotebookManager:
    def __init__(self, notebook_path: str = None):
        self.notebook_path = notebook_path or config.NOTEBOOK_PATH
        self.notebook = new_notebook()
        self._initialize_notebook()

    def _initialize_notebook(self):
        # Set up metadata
        self.notebook.metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            }
        }

        # Add initial markdown cell
        self.add_markdown_cell("# Automated Data Scientist Analysis", level=1)
        logging.info(f"Initialized notebook with path: {self.notebook_path}")

    def add_markdown_cell(self, content: str, level: int = 2):
        header = '#' * level
        cell = new_markdown_cell(f"{header} {content}")
        self.notebook.cells.append(cell)
        logging.info(f"Added markdown cell: {content}")

    def add_code_cell(self, code: str):
        cell = new_code_cell(code)
        self.notebook.cells.append(cell)
        logging.info("Added code cell.")

    def add_analysis_step(self, name: str, description: str, goals: str, code: str):
        self.add_markdown_cell(name, level=2)
        self.add_markdown_cell("Description:", level=3)
        self.add_markdown_cell(description)
        self.add_markdown_cell("Goals:", level=3)
        self.add_markdown_cell(goals)
        self.add_code_cell(code)
        logging.info(f"Added analysis step for: {name}")

    def save_notebook(self):
        # Serialize the notebook content to JSON
        notebook_json = nbformat.writes(self.notebook)
        
        # Log the entire notebook content
        logging.debug("Serialized Notebook JSON content:\n%s", notebook_json)
        
        # Write the JSON content to a file
        with open(self.notebook_path, 'w', encoding='utf-8') as f:
            f.write(notebook_json)
        
        logging.info(f"Notebook saved to {self.notebook_path}")

    def get_notebook_json(self) -> Dict[str, Any]:
        return json.loads(nbformat.writes(self.notebook))

if __name__ == "__main__":
    # This block is for testing purposes
    nm = NotebookManager()
    nm.add_analysis_step("Test Analysis", "This is a test description", "These are test goals", "print('Hello, World!')")
    nm.save_notebook()
    print("Test notebook created and saved.")
