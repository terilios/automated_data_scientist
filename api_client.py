import os
import logging
import time
from typing import Dict, Any
from openai import OpenAI
from openai import APIError, RateLimitError
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import backoff

class APIClient:
    def __init__(self, api_type: str = 'openai'):
        self.api_type = api_type
        self.setup_client()
        self.max_retries = 3
        self.retry_delay = 1  # in seconds

    def setup_client(self):
        """Set up the API client based on the specified API type."""
        if self.api_type == 'openai':
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=openai_api_key)
        elif self.api_type == 'anthropic':
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.client = Anthropic(api_key=anthropic_api_key)
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")
        
        logging.info(f"API client set up for {self.api_type}")

    @backoff.on_exception(backoff.expo, 
                          (RateLimitError, APIError),
                          max_tries=5)
    def call_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Call the API with error handling and retrying.

        Args:
        prompt (str): The prompt to send to the API.
        max_tokens (int): The maximum number of tokens to generate.

        Returns:
        str: The API response.

        Raises:
        Exception: If the API call fails after max retries.
        """
        if self.api_type == 'openai':
            return self._call_openai_api(prompt, max_tokens)
        elif self.api_type == 'anthropic':
            return self._call_anthropic_api(prompt, max_tokens)

    def _call_openai_api(self, prompt: str, max_tokens: int) -> str:
        """Call the OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise

    def _call_anthropic_api(self, prompt: str, max_tokens: int) -> str:
        """Call the Anthropic API."""
        try:
            response = self.client.completions.create(
                model="claude-3-sonnet-20240229",
                prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
                max_tokens_to_sample=max_tokens
            )
            return response.completion
        except Exception as e:
            logging.error(f"Anthropic API error: {str(e)}")
            raise

    def get_token_count(self, text: str) -> int:
        """
        Get the token count for a given text.

        Args:
        text (str): The text to count tokens for.

        Returns:
        int: The number of tokens in the text.
        """
        # Using a simple estimation for both OpenAI and Anthropic
        return len(text.split())

    def get_model_name(self) -> str:
        """Get the name of the current model being used."""
        if self.api_type == 'openai':
            return "gpt-4o-2024-08-06"
        elif self.api_type == 'anthropic':
            return "claude-3-sonnet-20240229"

    def get_max_tokens(self) -> int:
        """Get the maximum number of tokens supported by the current model."""
        if self.api_type == 'openai':
            return 4096  # for gpt-4o
        elif self.api_type == 'anthropic':
            return 200000  # for claude-3-sonnet-20240229

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    pass