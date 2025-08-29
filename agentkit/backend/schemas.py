"""Pydantic schemas for AgentKit data structures."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

# --- Agent Definition Schemas (for YAML validation) ---

class ToolSpec(BaseModel):
    """Defines a tool that can be used in a step."""
    name: str
    schema_def: Dict[str, Any] = Field(..., alias="schema")

class StepExpects(BaseModel):
    """Defines the expected output from a model for a given step."""
    type: Literal["text", "json"]
    schema_def: Optional[Dict[str, Any]] = Field(None, alias="schema")

class StepWrites(BaseModel):
    """Defines an artifact to be written to storage."""
    path: str
    from_json: Optional[str] = None
    from_text: Optional[str] = None

class AgentStep(BaseModel):
    """Defines a single step within an agent's workflow."""
    id: str
    prompt_template: str
    expects: StepExpects
    tools: List[str] = []
    writes: List[StepWrites] = []
    update_state: Dict[str, str] = {}

class AgentDefaults(BaseModel):
    """Default settings for an agent."""
    step_limit: int = 10
    timeout_sec: int = 60

class AgentDefinition(BaseModel):
    """The complete definition of an agent, loaded from YAML."""
    id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    defaults: AgentDefaults = Field(default_factory=AgentDefaults)
    steps: List[AgentStep]

# --- API & Orchestration Schemas ---

class RunRequest(BaseModel):
    """Request body for POST /api/run."""
    agent_id: str
    model_id: str
    input: Dict[str, Any]
    options: Optional[AgentDefaults] = None

class StepResult(BaseModel):
    """The result of a single step execution."""
    step_id: str
    status: Literal["pending", "running", "success", "failure"] = "pending"
    prompt: str
    raw_output: Optional[str] = None
    json_output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class RunStatus(BaseModel):
    """Represents the complete status and result of an agent run."""
    run_id: str
    status: Literal["running", "completed", "failed"] = "running"
    agent_id: str
    model_id: str
    input: Dict[str, Any]
    state: Dict[str, Any] = {}
    steps: List[StepResult] = []
    artifacts: List[str] = []
    created_at: float
    finished_at: Optional[float] = None
