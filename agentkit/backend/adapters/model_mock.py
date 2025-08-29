"""A mock implementation of the ModelClient for local testing."""

import json
from typing import Any, Dict

from agentkit.backend.models import ModelClient

class MockModelClient(ModelClient):
    """
    A deterministic mock of a ModelClient that can be used for offline testing.
    It does not connect to any real model provider.
    """

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Returns a canned text response."""
        return f"Mock text response for prompt:\n---\n{prompt}\n---"

    def generate_json(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Returns a canned JSON response that loosely mimics the requested schema.
        For properties of type 'string', it returns a descriptive string.
        For other types, it returns a default value.
        """
        mock_response = {}
        properties = schema.get("properties", {})

        def _generate_mock_value(prop_schema: Dict[str, Any], path: str):
            prop_type = prop_schema.get("type")
            if prop_type == "string":
                return f"mock_{path}"
            elif prop_type == "integer":
                return 1
            elif prop_type == "number":
                return 1.0
            elif prop_type == "boolean":
                return True
            elif prop_type == "array":
                items_schema = prop_schema.get("items", {})
                # Generate one mock item for the array
                return [_generate_mock_value(items_schema, f"{path}[0]")]
            elif prop_type == "object":
                nested_props = prop_schema.get("properties", {})
                return {key: _generate_mock_value(val, f"{path}.{key}") for key, val in nested_props.items()}
            else:
                return f"mock_value_for_{path}"

        for key, prop_schema in properties.items():
            mock_response[key] = _generate_mock_value(prop_schema, key)

        # To make it feel a bit more real, we can embed the prompt in the response
        # if there's a 'description' field, which is common.
        if "description" in mock_response and isinstance(mock_response["description"], str):
             mock_response["description"] = f"Mock description based on prompt: {prompt[:100]}..."

        return mock_response
