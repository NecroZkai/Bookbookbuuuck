"""An adapter for interacting with the OpenAI API."""

import os
import json
from typing import Any, Dict

import openai
from openai import OpenAI

from agentkit.backend.models import ModelClient

class OpenAIModelClient(ModelClient):
    """
    A client for OpenAI's API that implements the generic ModelClient interface.
    """

    def __init__(self, model: str):
        """
        Initializes the OpenAI client.

        Args:
            model: The specific OpenAI model to use (e.g., "gpt-4o").
        """
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        self.client = OpenAI(api_key=api_key)

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generates plain text from a prompt using the OpenAI API.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                **kwargs, # Pass through any other params like temperature
            )
            return response.choices[0].message.content
        except openai.APIError as e:
            # Handle API errors gracefully
            raise RuntimeError(f"OpenAI API error: {e}") from e

    def generate_json(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Generates a JSON object that conforms to a given schema using OpenAI's
        JSON mode.
        """
        try:
            # The prompt should already contain instructions to generate JSON.
            # OpenAI's JSON mode ensures the output is valid JSON.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                **kwargs,
            )

            response_text = response.choices[0].message.content
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON from OpenAI response: {response_text}") from e
        except openai.APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e
