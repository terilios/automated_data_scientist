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
import ast
import traceback

# Set Seaborn plot theme
sns.set_theme(context='notebook', style='darkgrid', palette='pastel')

class CodeExecutor:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.figure_dir = output_path / "figures"
        self.figure_dir.mkdir(parents=True, exist_ok=True)
        self.installed_packages = set()
        self.notebook_path = self.output_path / 'analysis_notebook.ipynb'

    def execute_code(self, sanitized_code: str, data: pd.DataFrame) -> Tuple[Any, str, List[str]]:
        logging.info("Executing sanitized code")
        logging.debug(f"Sanitized code:\n{sanitized_code}")

        # Capturing output
        output_buffer = io.StringIO()
        figure_paths = []

        global_vars = self._prepare_global_namespace(data, figure_paths)

        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            try:
                prepared_code = self._prepare_code(sanitized_code)
                logging.debug(f"Prepared code for execution:\n{prepared_code}")  # Log the prepared code
                
                exec(prepared_code, global_vars)

                # Suggest code refinements based on feedback
                self.review_and_refine(global_vars)

                result = global_vars.get('result', None)
            except Exception as e:
                logging.error(f"Error during code execution: {str(e)}")
                logging.error(f"Detailed traceback:\n{traceback.format_exc()}")
                result = None

        output = output_buffer.getvalue()
        self.save_to_notebook(sanitized_code, output, result)
        logging.info("Sanitized code execution completed")
        return result, output, figure_paths

    def _prepare_global_namespace(self, data: pd.DataFrame, figure_paths: List[str]) -> Dict[str, Any]:
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
        # Standardize code indentation
        indented_code = '\n'.join('    ' + line for line in code.splitlines())

        # Properly creating try-except block
        code_block = f"""
try:
{indented_code}
except Exception as e:
    print(f"Error during code execution: {{str(e)}}")
    print(f"Traceback: {{traceback.format_exc()}}")
    raise
"""
        return code_block

    def _sanitize_text(self, text: str) -> str:
        return text.replace('\r', '')

    def _save_figures(self, figure_paths: List[str]) -> List[Dict]:
        figure_metadata = []
        for i, fig in enumerate(plt.get_fignums()):
            figure = plt.figure(fig)
            file_path = self.figure_dir / f"figure_{i}.png"
            figure.savefig(file_path)
            figure_paths.append(str(file_path))

            logging.info(f"Figure saved: {file_path}")
            
            ax = figure.gca()
            metadata = {
                "title": self._sanitize_text(ax.get_title()),
                "x_label": self._sanitize_text(ax.get_xlabel()),
                "y_label": self._sanitize_text(ax.get_ylabel()),
                "num_lines": len(ax.get_lines()),
                "legends": [self._sanitize_text(leg.get_text()) for leg in ax.get_legend().get_texts()] if ax.get_legend() else []
            }
            figure_metadata.append(metadata)
            
            plt.tight_layout()
            plt.close(fig)
        return figure_metadata

    def review_and_refine(self, global_vars: Dict[str, Any]):
        figure_metadata = self._save_figures(global_vars['figure_paths'])

        feedback = self.review_visualizations(figure_metadata)
        logging.info(f"Visualization Feedback: {feedback}")  
        for note in feedback:
            if 'improvement' in note:
                self.refine_visualizations(note)

    def review_visualizations(self, figure_metadata: List[Dict]) -> List[str]:
        feedback = []
        for metadata in figure_metadata:
            prompt = f"""
            Review the following visualization metadata and suggest improvements:

            Title: {metadata['title']}
            X-axis label: {metadata['x_label']}
            Y-axis label: {metadata['y_label']}
            Number of lines plotted: {metadata['num_lines']}
            Legends: {metadata['legends']}

            Suggest improvements to enhance clarity and usability.
            """
            response = "Sample feedback."  # Replace with actual API call if needed
            feedback.append(response)
        return feedback

    def refine_visualizations(self, feedback: str):
        # Implement visualization refinement based on feedback
        logging.info(f"Refining visualization based on feedback: {feedback}")
        # Add your refinement logic here

    def save_to_notebook(self, sanitized_code: str, output: str, result: Any):
        with open(self.notebook_path, 'a') as notebook:
            notebook.write(f"### Sanitized Code:\n{sanitized_code}\n\n")
            notebook.write(f"### Output:\n{output}\n\n")
            notebook.write(f"### Result:\n{result}\n\n")
        logging.info(f"Saved results to notebook {self.notebook_path}.")

    def import_library(self, library_name: str) -> Any:
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
        return {
            "result_type": type(result).__name__,
            "output_length": len(output),
            "num_figures": len(figure_paths),
            "installed_packages": list(self.installed_packages)
        }

    def generate_report(self, figure_paths, report_path='output/final_report.pdf'):
        from matplotlib.backends.backend_pdf import PdfPages
        with PdfPages(report_path) as pdf:
            for fig_path in figure_paths:
                plt.figure()
                img_data = plt.imread(fig_path)
                plt.imshow(img_data)
                pdf.savefig()
                plt.close()
        logging.info(f"Generated report saved to {report_path}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='debug.log')  # Changed from execution.log to debug.log
