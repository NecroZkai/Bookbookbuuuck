"""Base classes and sample implementations for Tools."""

from typing import Any, Dict

from agentkit.backend.models import Tool

# --- Sample Tool Implementations ---

class EchoTool(Tool):
    """A simple tool that echoes back the input text."""

    @property
    def name(self) -> str:
        return "echo_tool"

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to be echoed back."
                }
            },
            "required": ["text"],
        }

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Takes a payload with 'text' and returns it in an 'echo' field."""
        text_to_echo = payload.get("text", "")
        return {"echo": text_to_echo}

class TemplateFillTool(Tool):
    """A tool to fill a template string with provided variables."""

    @property
    def name(self) -> str:
        return "template_fill_tool"

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "template": {
                    "type": "string",
                    "description": "A string with placeholders like {key}.",
                },
                "variables": {
                    "type": "object",
                    "description": "A dictionary of key-value pairs to fill the template.",
                },
            },
            "required": ["template", "variables"],
        }

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fills the template and returns the result."""
        template = payload.get("template", "")
        variables = payload.get("variables", {})

        if not isinstance(variables, dict):
            return {"error": "The 'variables' field must be a dictionary."}

        try:
            filled_text = template.format(**variables)
            return {"result": filled_text}
        except KeyError as e:
            return {"error": f"Missing variable in template: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

# --- Tool Registry ---

# A simple dictionary to register and look up tools by name.
# The orchestrator will use this to find the correct tool to run.
# In a larger application, this might be dynamically populated.
AVAILABLE_TOOLS = {
    tool.name: tool for tool in [EchoTool(), TemplateFillTool()]
}
