"""
Loads and validates agent definitions from the /agents directory.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import ValidationError
from agentkit.backend.schemas import AgentDefinition

# --- Registry Storage ---

# The path to the directory where agent YAML files are stored.
AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"

# A dictionary to hold the loaded and validated agent definitions, keyed by agent_id.
# This is populated at startup by the load_agents() function.
_agent_registry: Dict[str, AgentDefinition] = {}

# --- Public Functions ---

def load_agents(agents_dir: Path = AGENTS_DIR):
    """
    Scans the specified directory for .yaml files, parses them, validates them
    against the AgentDefinition schema, and populates the registry.
    This should be called once when the application starts.
    """
    if not agents_dir.is_dir():
        print(f"Warning: Agents directory not found at {agents_dir}")
        return

    global _agent_registry
    _agent_registry = {}

    for filepath in agents_dir.glob("*.yaml"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                agent_data = yaml.safe_load(f)

            if not agent_data or not isinstance(agent_data, dict):
                print(f"Warning: Skipping empty or invalid YAML file: {filepath.name}")
                continue

            # Validate the data with the Pydantic model
            agent_def = AgentDefinition(**agent_data)

            if agent_def.id in _agent_registry:
                print(f"Warning: Duplicate agent ID '{agent_def.id}' found. Overwriting.")

            _agent_registry[agent_def.id] = agent_def
            print(f"Successfully loaded and validated agent: {agent_def.name} (id: {agent_def.id})")

        except FileNotFoundError:
            print(f"Error: Could not find agent file: {filepath}")
        except yaml.YAMLError as e:
            print(f"Error: Could not parse YAML file {filepath.name}: {e}")
        except ValidationError as e:
            print(f"Error: Validation failed for agent in {filepath.name}:\n{e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading agent {filepath.name}: {e}")

def get_agent(agent_id: str) -> Optional[AgentDefinition]:
    """Retrieves a single agent definition from the registry by its ID."""
    return _agent_registry.get(agent_id)

def list_agents() -> List[AgentDefinition]:
    """Returns a list of all loaded agent definitions."""
    return list(_agent_registry.values())
