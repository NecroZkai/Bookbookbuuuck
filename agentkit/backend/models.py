"""Abstract base classes for pluggable AgentKit components."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

class ModelClient(ABC):
    """
    Abstract interface for a client that interacts with a generative model.
    This is vendor-agnostic and supports text or structured JSON generation.
    """

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generates plain text from a prompt."""
        pass

    @abstractmethod
    def generate_json(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generates a JSON object that conforms to a given schema."""
        pass

class SpeechClient(ABC):
    """
    Abstract interface for a client that synthesizes speech from text.
    """

    @abstractmethod
    def synthesize(self, text: str, voice: str, out_path: Path) -> None:
        """
        Synthesizes audio from text and saves it to a file.

        Args:
            text: The text to synthesize.
            voice: A string identifying the voice to use.
            out_path: The Path object where the output audio file (e.g., .mp3) should be saved.
        """
        pass

class Tool(ABC):
    """
    Abstract interface for a tool that an agent can execute.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the tool."""
        pass

    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """A JSON schema defining the tool's input arguments."""
        pass

    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the tool with the given payload.

        Args:
            payload: A dictionary of arguments conforming to the tool's schema.

        Returns:
            A dictionary representing the result of the tool's execution.
        """
        pass
