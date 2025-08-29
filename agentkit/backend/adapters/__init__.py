"""
Adapter Registry for Model Clients

This module acts as a central registry for all available model clients.
It provides a factory function to get the correct client instance based on a model_id.
"""

from typing import Type

from agentkit.backend.models import ModelClient
from .model_mock import MockModelClient
from .openai import OpenAIModelClient

# A mapping from model_id strings to the client class that handles them.
ADAPTER_MAP: dict[str, Type[ModelClient]] = {
    # Real Adapters
    "gpt-4o": OpenAIModelClient,
    "gpt-4-turbo": OpenAIModelClient,
    "gpt-4": OpenAIModelClient,
    "gpt-3.5-turbo": OpenAIModelClient,

    # Placeholder Adapters (fall back to Mock)
    "gpt-5": MockModelClient,
    "gemini-1.5-pro": MockModelClient,
    "grok-4": MockModelClient,

    # Default Mock Adapter
    "mock-model": MockModelClient,
}

def get_model_client(model_id: str) -> ModelClient:
    """
    Factory function to get an instance of a model client based on the model_id.

    Args:
        model_id: The identifier of the model (e.g., "gpt-4o", "mock-model").

    Returns:
        An instance of a class that implements the ModelClient interface.

    Raises:
        ValueError: If the requested model_id is not supported.
    """
    client_class = ADAPTER_MAP.get(model_id)

    if not client_class:
        # For maximum flexibility, any unknown model ID will fall back to the mock client.
        # This prevents the system from crashing if the UI lists a model that isn't
        # fully implemented in the backend yet.
        print(f"Warning: Model ID '{model_id}' not found in registry. Falling back to MockModelClient.")
        client_class = MockModelClient

    # Pass the model_id to the constructor. This is important for clients
    # like OpenAI's that need to know which specific model to call.
    return client_class(model=model_id)
