import logging
import io
import sys
import contextlib
from pathlib import Path
from typing import Any, Tuple, List, Dict
import importlib
import subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class CodeExecutor:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.figure_dir = output_path / "figures"
        self.figure_dir.mkdir(parents=True, exist_ok=True)
        self.installed_packages = set()

    def execute_code(self, code: str, data: pd.DataFrame) -> Tuple[Any, str, List[str]]:
        """
        Executes the generated Python code and captures its output.

        Args:
        code (str): The Python code to execute.
        data (pd.DataFrame): The data to be used in the analysis.

        Returns:
        Tuple[Any, str, List[str]]: A tuple containing the result, output, and list of figure paths.
        """
        logging.info("Executing generated code")

        # Create a string buffer to capture stdout and stderr
        output_buffer = io.StringIO()
        
        # List to store paths of generated figures
        figure_paths = []

        # Prepare the global namespace for execution
        global_vars = self._prepare_global_namespace(data, figure_paths)

        # Redirect stdout and stderr to our buffer
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            try:
                # Prepare and execute the code
                prepared_code = self._prepare_code(code)
                exec(prepared_code, global_vars)
                
                # Capture and save any open figures
                self._save_figures(figure_paths)
                
                # Get the result from the global namespace
                result = global_vars.get('result', None)
                
            except Exception as e:
                logging.error(f"Error during code execution: {str(e)}")
                result = None

        # Get the captured output
        output = output_buffer.getvalue()
        
        logging.info("Code execution completed")
        return result, output, figure_paths

    def _prepare_global_namespace(self, data: pd.DataFrame, figure_paths: List[str]) -> Dict[str, Any]:
        """Prepares the global namespace for code execution."""
        return {
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'df': data,
            'figure_dir': self.figure_dir,
            'figure_paths': figure_paths,
            'import_library': self.import_library
        }

    def _prepare_code(self, code: str) -> str:
        """Prepares the code for execution by adding necessary imports and safety checks."""
        return f"""
def safe_exec(code):
    forbidden = ['eval', 'exec', '__import__', 'open']
    for word in forbidden:
        if word in code:
            raise ValueError(f"Unauthorized operation detected: {{word}}")

safe_exec('''{code}''')

{code}
"""

    def _save_figures(self, figure_paths: List[str]):
        """Saves any open matplotlib figures."""
        for i, fig in enumerate(plt.get_fignums()):
            figure = plt.figure(fig)
            file_path = self.figure_dir / f"figure_{i}.png"
            figure.savefig(file_path)
            figure_paths.append(str(file_path))
            plt.close(fig)

    def import_library(self, library_name: str) -> Any:
        """
        Safely imports a library, installing it if necessary.

        Args:
        library_name (str): The name of the library to import.

        Returns:
        Any: The imported library module.

        Raises:
        ImportError: If the library cannot be imported or installed.
        """
        try:
            return importlib.import_module(library_name)
        except ImportError:
            if library_name not in self.installed_packages:
                logging.info(f"Attempting to install {library_name}")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", library_name])
                    self.installed_packages.add(library_name)
                    logging.info(f"Successfully installed {library_name}")
                except subprocess.CalledProcessError:
                    logging.error(f"Failed to install {library_name}")
                    raise ImportError(f"Could not import or install {library_name}")
            return importlib.import_module(library_name)

    def get_execution_summary(self, result: Any, output: str, figure_paths: List[str]) -> dict:
        """Generates a summary of the code execution."""
        return {
            "result_type": type(result).__name__,
            "output_length": len(output),
            "num_figures": len(figure_paths),
            "installed_packages": list(self.installed_packages)
        }

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    pass