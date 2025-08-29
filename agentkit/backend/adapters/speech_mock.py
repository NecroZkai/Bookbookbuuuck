"""A mock implementation of the SpeechClient for local testing."""

from pathlib import Path

from agentkit.backend.models import SpeechClient

class MockSpeechClient(SpeechClient):
    """
    A mock of a SpeechClient that writes a placeholder file instead of
    synthesizing real audio.
    """

    def synthesize(self, text: str, voice: str, out_path: Path) -> None:
        """
        Creates a small text file with an .mp3 extension to act as a placeholder
        for a real audio file.

        Args:
            text: The text that would be synthesized.
            voice: The voice that would be used.
            out_path: The Path object where the output file should be saved.
        """
        out_path.parent.mkdir(parents=True, exist_ok=True)
        placeholder_content = (
            f"This is a mock MP3 file.\n"
            f"Voice: {voice}\n"
            f"Text: \"{text[:100]}...\""
        )
        out_path.write_text(placeholder_content)
