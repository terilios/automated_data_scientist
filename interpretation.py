import logging
from typing import Dict, Any, List
from api_client import APIClient

class ResultInterpreter:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def interpret_results(self, analysis: Dict[str, Any], result: Any, output: str, figure_paths: List[str], completed_analyses: List[Dict], key_findings: List[str]) -> str:
        """
        Interprets the results of an analysis step.

        Args:
        analysis (Dict[str, Any]): The analysis step details.
        result (Any): The result returned by the executed code.
        output (str): The captured output of the code execution.
        figure_paths (List[str]): List of paths to generated figures.
        completed_analyses (List[Dict]): List of previously completed analyses.
        key_findings (List[str]): List of key findings from previous analyses.

        Returns:
        str: A string containing the interpretation of the results.
        """
        logging.info(f"Interpreting results for analysis: {analysis['name']}")

        prompt = f"""
        We have completed the following analysis step:

        {analysis}

        The execution resulted in the following:

        Result: {result}

        Output:
        {output}

        Number of visualizations generated: {len(figure_paths)}

        Previous analyses: {len(completed_analyses)}
        Key findings so far: {len(key_findings)}

        Please provide an interpretive analysis of these results. Include:
        1. A summary of what the analysis did
        2. Key findings and insights from the results
        3. Interpretation of any visualizations created (without seeing them, based on their existence and the analysis description)
        4. How these results relate to or build upon previous findings in the project
        5. Potential implications of these results for the overall project goals
        6. Suggestions for further analysis or investigation based on these findings

        Your interpretation should be detailed yet concise, suitable for inclusion in a data science report.
        Format your response in Markdown, using appropriate headers and bullet points.
        """

        interpretation = self.api_client.call_api(prompt)
        logging.info(f"Results interpretation completed for analysis: {analysis['name']}")
        return interpretation

    def extract_key_findings(self, interpretation: str) -> List[str]:
        """
        Extracts key findings from the interpretation.

        Args:
        interpretation (str): The full interpretation of the analysis results.

        Returns:
        List[str]: A list of key findings extracted from the interpretation.
        """
        prompt = f"""
        Given the following interpretation of an analysis:

        {interpretation}

        Please extract and list the key findings from this interpretation. Each finding should be:
        1. Concise (one or two sentences)
        2. Specific and data-driven
        3. Relevant to the overall goals of the data science project

        Provide the findings as a list, with each finding on a new line starting with a dash (-).
        """

        findings = self.api_client.call_api(prompt)
        key_findings = [finding.strip()[2:] for finding in findings.split('\n') if finding.strip().startswith('-')]
        return key_findings

    def suggest_next_steps(self, analysis: Dict[str, Any], interpretation: str, key_findings: List[str]) -> List[str]:
        """
        Suggests next steps for analysis based on the current results and interpretation.

        Args:
        analysis (Dict[str, Any]): The current analysis step details.
        interpretation (str): The interpretation of the current analysis results.
        key_findings (List[str]): List of key findings from all analyses so far.

        Returns:
        List[str]: A list of suggested next steps for further analysis.
        """
        prompt = f"""
        Based on the following:

        Current analysis: {analysis}

        Interpretation of results:
        {interpretation}

        Key findings so far:
        {key_findings}

        Please suggest 3-5 next steps for further analysis. Each suggestion should:
        1. Build upon the current findings
        2. Address unanswered questions or explore promising directions
        3. Be specific and actionable

        Provide the suggestions as a list, with each suggestion on a new line starting with a dash (-).
        """

        suggestions = self.api_client.call_api(prompt)
        next_steps = [step.strip()[2:] for step in suggestions.split('\n') if step.strip().startswith('-')]
        return next_steps

    def generate_summary_report(self, completed_analyses: List[Dict], key_findings: List[str]) -> str:
        """
        Generates a summary report of all completed analyses.

        Args:
        completed_analyses (List[Dict]): List of all completed analyses with their results and interpretations.
        key_findings (List[str]): List of key findings from all analyses.

        Returns:
        str: A Markdown-formatted summary report.
        """
        prompt = f"""
        Please generate a summary report for a data science project based on the following information:

        Completed Analyses:
        {completed_analyses}

        Key Findings:
        {key_findings}

        The summary report should include:
        1. An executive summary of the project
        2. Overview of the analyses performed
        3. Synthesis of key findings and insights
        4. Implications of the findings for the project goals
        5. Recommendations for future work or actions

        Format the report in Markdown, using appropriate headers, bullet points, and emphasis where needed.
        The report should be comprehensive yet concise, suitable for presentation to stakeholders.
        """

        report = self.api_client.call_api(prompt)
        return report

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    pass