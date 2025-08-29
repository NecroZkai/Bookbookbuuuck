"""
The core run loop for executing an agent's sequence of steps.
"""

import time
import uuid
import json
from jinja2 import Template

from agentkit.backend import registry, storage
from agentkit.backend.adapters.model_mock import MockModelClient
from agentkit.backend.guards import guard_manager
from agentkit.backend.schemas import (
    AgentDefinition, RunRequest, RunStatus, StepResult
)
from agentkit.backend.tools import AVAILABLE_TOOLS

class Orchestrator:
    """
    Manages the execution of an agent run, stepping through the defined
    workflow, calling models and tools, and persisting state and artifacts.
    """

    def __init__(self):
        # In a real app, a factory would select the client based on model_id
        self.model_client = MockModelClient()

    def run_agent(self, request: RunRequest) -> RunStatus:
        """The main entry point for executing an agent run."""
        run_id = f"{request.agent_id}-{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        agent_def = registry.get_agent(request.agent_id)
        if not agent_def:
            raise ValueError(f"Agent with ID '{request.agent_id}' not found.")

        run_status = RunStatus(
            run_id=run_id,
            agent_id=request.agent_id,
            model_id=request.model_id,
            input=request.input,
            state=request.input.copy(), # Start with input as the initial state
            created_at=start_time,
        )

        try:
            self._execute_steps(run_status, agent_def)
            run_status.status = "completed"
        except Exception as e:
            run_status.status = "failed"
            # In a real app, you'd have more structured error logging
            print(f"Run {run_id} failed: {e}")

        run_status.finished_at = time.time()
        # Persist the final run status
        self._save_run_status(run_status)
        return run_status

    def _execute_steps(self, run_status: RunStatus, agent_def: AgentDefinition):
        """Iterates through and executes each step of the agent's definition."""
        options = run_status.input.get("options") or agent_def.defaults

        for i, step_def in enumerate(agent_def.steps):
            if i >= options.step_limit:
                print(f"Step limit of {options.step_limit} reached. Halting run.")
                break

            step_result = StepResult(step_id=step_def.id, status="running", start_time=time.time())
            run_status.steps.append(step_result)

            try:
                # 1. Render the prompt
                prompt = self._render_prompt(step_def.prompt_template, run_status.state)
                step_result.prompt = prompt

                if not guard_manager.check_prompt(prompt):
                    raise ValueError("Prompt failed guard check.")

                # 2. Call the model
                if step_def.expects.type == "text":
                    raw_output = self.model_client.generate_text(prompt)
                    step_result.raw_output = raw_output
                elif step_def.expects.type == "json":
                    json_output = self.model_client.generate_json(prompt, step_def.expects.schema_def)
                    step_result.json_output = json_output
                    step_result.raw_output = json.dumps(json_output, indent=2)
                else:
                    raise TypeError(f"Unsupported expect type: {step_def.expects.type}")

                if not guard_manager.check_model_output(step_result.raw_output):
                     raise ValueError("Model output failed guard check.")

                # 3. Update state
                self._update_state(run_status.state, step_def.update_state, step_result)

                # 4. Write artifacts
                self._write_artifacts(run_status.run_id, step_def.writes, step_result)
                run_status.artifacts.extend([w.path for w in step_def.writes])

                step_result.status = "success"

            except Exception as e:
                step_result.status = "failure"
                step_result.error_message = str(e)
                print(f"Error in step {step_def.id}: {e}")
                raise # Re-raise to stop the whole run

            finally:
                step_result.end_time = time.time()


    def _render_prompt(self, template_str: str, state: dict) -> str:
        """Renders the Jinja2 template with the current state."""
        template = Template(template_str)
        # We provide the whole state dict under the 'state' key, plus top-level keys
        render_context = {**state, "state": state}
        return template.render(render_context)

    def _update_state(self, run_state: dict, update_rules: dict, step_result: StepResult):
        """Updates the run state based on the step's output."""
        for dest_key, src_path in update_rules.items():
            # Simple JSONPath-like accessor for "$.key" or "$.key.nested"
            if src_path.startswith("$."):
                value = step_result.json_output
                path_parts = src_path[2:].split('.')
                try:
                    for part in path_parts:
                        value = value[part]
                    run_state[dest_key] = value
                except (KeyError, TypeError):
                    print(f"Warning: Could not resolve state path '{src_path}'")
            else:
                print(f"Warning: Unsupported state path format '{src_path}'")

    def _write_artifacts(self, run_id: str, write_rules: list, step_result: StepResult):
        """Writes artifacts to the run's storage directory."""
        if not write_rules:
            return

        artifacts_dir = storage.get_artifacts_dir(run_id)

        for rule in write_rules:
            out_path = artifacts_dir / rule.path.lstrip("artifacts/")

            content_to_write = None
            if rule.from_text:
                if rule.from_text == "$":
                    content_to_write = step_result.raw_output
                storage.write_text(out_path, content_to_write or "")

            elif rule.from_json:
                if rule.from_json == "$":
                    content_to_write = step_result.json_output
                # Can be extended to support JSONPath to select sub-trees
                storage.write_json(out_path, content_to_write or {})

    def _save_run_status(self, run_status: RunStatus):
        """Saves the final run status object to a file."""
        run_dir = storage.get_run_dir(run_status.run_id)
        status_path = run_dir / "run_status.json"
        storage.write_json(status_path, run_status.dict())

orchestrator = Orchestrator()
