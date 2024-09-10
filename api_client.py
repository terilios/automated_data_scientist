import os
import logging
import time
from typing import Dict, Any
import json
from openai import OpenAI
from openai import APIError, RateLimitError, BadRequestError
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import backoff
import httpx

class APIClient:
    def __init__(self, api_type: str = 'openai', timeout: float = 30.0):
        self.api_type = api_type
        self.timeout = timeout
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
                          (RateLimitError, APIError, httpx.TimeoutException),
                          max_tries=5)
    def call_api(self, prompt: str, max_tokens: int = 1000, use_json_mode: bool = False) -> str:
        """
        Call the API with error handling and retrying.

        Args:
        prompt (str): The prompt to send to the API.
        max_tokens (int): The maximum number of tokens to generate.
        use_json_mode (bool): Whether to use JSON mode for structured output.

        Returns:
        str: The API response.

        Raises:
        Exception: If the API call fails after max retries.
        """
        logging.debug(f"Sending prompt to {self.api_type} API: {prompt}")
        if self.api_type == 'openai':
            return self._call_openai_api(prompt, max_tokens, use_json_mode)
        elif self.api_type == 'anthropic':
            return self._call_anthropic_api(prompt, max_tokens)

    def _call_openai_api(self, prompt: str, max_tokens: int, use_json_mode: bool) -> str:
        """Call the OpenAI API."""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            api_params = {
                "model": self.get_model_name(),
                "messages": messages,
                "max_tokens": max_tokens,
                "timeout": self.timeout,
            }
            
            if use_json_mode:
                api_params["response_format"] = {"type": "json_object"}
                logging.debug("Using JSON mode for structured output")

            logging.debug(f"API request parameters: {json.dumps(api_params)}")
            response = self.client.chat.completions.create(**api_params)
            logging.debug(f"Received raw response from OpenAI API: {response}")
            processed_response = self._preprocess_response(response.choices[0].message.content)
            return processed_response
        except httpx.TimeoutException:
            logging.error(f"OpenAI API call timed out after {self.timeout} seconds")
            raise
        except BadRequestError as e:
            logging.error(f"Bad Request Error: {e.response.json()}")
            raise
        except APIError as e:
            logging.error(f"API Error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in OpenAI API call: {str(e)}")
            raise

    def _call_anthropic_api(self, prompt: str, max_tokens: int) -> str:
        """Call the Anthropic API."""
        try:
            response = self.client.completions.create(
                model="claude-3-sonnet-20240229",
                prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
                max_tokens_to_sample=max_tokens,
                timeout=self.timeout
            )
            logging.debug(f"Received raw response from Anthropic API: {response}")
            processed_response = self._preprocess_response(response.completion)
            return processed_response
        except httpx.TimeoutException:
            logging.error(f"Anthropic API call timed out after {self.timeout} seconds")
            raise
        except Exception as e:
            logging.error(f"Anthropic API error: {str(e)}")
            raise

    def _preprocess_response(self, response: str) -> str:
        """
        Preprocess the API response to handle formatting issues.
        
        Args:
        response (str): The raw API response.
        
        Returns:
        str: The preprocessed response.
        """
        # Replace smart quotes with straight quotes
        processed_response = response.replace('“', '"').replace('”', '"')
        
        # Log the preprocessing step
        logging.info("Preprocessed API response to handle smart quotes")
        logging.debug(f"Preprocessed response: {processed_response}")
        
        return processed_response

    def parse_json_response(self, response: str) -> Any:
        """
        Parse the JSON response with error handling.
        
        Args:
        response (str): The preprocessed API response.
        
        Returns:
        Any: The parsed JSON data.
        
        Raises:
        json.JSONDecodeError: If the response cannot be parsed as JSON.
        """
        try:
            # For structured output, the response should already be in JSON format
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to the previous method for non-structured responses
            try:
                # Strip the markdown code block delimiters
                json_str = response.strip("```json").strip("\n```")
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse API response as JSON. Error: {str(e)}")
                logging.error(f"Problematic response content: {response}")
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
            return "gpt-4o-2024-08-06"  # Updated to use the specified model name
        elif self.api_type == 'anthropic':
            return "claude-3-sonnet-20240229"

    def get_max_tokens(self) -> int:
        """Get the maximum number of tokens supported by the current model."""
        if self.api_type == 'openai':
            return 4096  # Assuming the same token limit as GPT-4
        elif self.api_type == 'anthropic':
            return 200000  # for claude-3-sonnet-20240229

if __name__ == "__main__":
    # This block is for testing purposes and will not be executed when imported
    logging.basicConfig(level=logging.DEBUG)
    client = APIClient('openai', timeout=60.0)
    response = client.call_api("What is the capital of France?", use_json_mode=True)
    print(client.parse_json_response(response))