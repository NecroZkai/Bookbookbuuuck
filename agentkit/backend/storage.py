"""Utility functions for file-based storage and path management."""

import json
import re
from pathlib import Path
from typing import Any, Dict

# --- Path Definitions ---

# The root directory of the agentkit project.
# We assume this script is run from the project root.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Directory to store all data related to agent runs.
RUNS_DIR = BASE_DIR / "runs"

def get_run_dir(run_id: str) -> Path:
    """Returns the directory for a specific run."""
    return RUNS_DIR / run_id

def get_artifacts_dir(run_id: str) -> Path:
    """Returns the artifacts directory for a specific run."""
    return get_run_dir(run_id) / "artifacts"

# --- Helper Functions ---

def slugify(value: str) -> str:
    """
    Normalizes a string, converting it to a lowercase, dash-separated,
    URL-friendly slug.
    """
    value = str(value)
    value = value.strip().lower()
    value = re.sub(r'[^\w\s-]', '', value) # remove non-word characters
    value = re.sub(r'[\s_-]+', '-', value) # replace spaces/underscores with dashes
    value = re.sub(r'^-+|-+$', '', value) # remove leading/trailing dashes
    return value

def write_text(path: Path, content: str):
    """
    Writes text content to a file, creating parent directories if they don't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_json(path: Path, data: Dict[str, Any]):
    """
    Writes a dictionary to a JSON file, creating parent directories if they don't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def write_binary(path: Path, content: bytes):
    """
    Writes binary content to a file, creating parent directories if they don't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
