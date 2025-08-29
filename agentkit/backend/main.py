"""
The main FastAPI application for AgentKit.
"""

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from agentkit.backend import registry, storage
from agentkit.backend.orchestrator import orchestrator
from agentkit.backend.schemas import AgentDefinition, RunRequest, RunStatus

# --- FastAPI App Initialization ---

app = FastAPI(
    title="AgentKit",
    description="A vendor-agnostic framework for running AI agents.",
)

# --- CORS Middleware ---
# Allow all origins for simple local development.
# In a production environment, this should be more restrictive.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup Event ---

@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup."""
    print("Loading agent definitions...")
    registry.load_agents()
    print(f"Found {len(registry.list_agents())} agents.")

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    """A simple endpoint to confirm the server is running."""
    return {"status": "ok"}

@app.get("/api/agents", response_model=list[AgentDefinition])
async def list_available_agents():
    """Returns a list of all available agent definitions."""
    return registry.list_agents()

@app.post("/api/run", response_model=RunStatus)
async def start_agent_run(request: RunRequest):
    """
    Starts an agent run synchronously and returns the final status.
    """
    try:
        run_status = orchestrator.run_agent(request)
        return run_status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred during run: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during the agent run.")

@app.get("/api/runs/{run_id}", response_model=RunStatus)
async def get_run_details(run_id: str):
    """
    Retrieves the details and status of a specific run.
    """
    try:
        run_dir = storage.get_run_dir(run_id)
        status_file = run_dir / "run_status.json"

        if not status_file.exists():
            raise HTTPException(status_code=404, detail=f"Run with ID '{run_id}' not found.")

        with open(status_file, 'r') as f:
            run_data = json.load(f)

        return RunStatus(**run_data)
    except Exception as e:
        print(f"Error retrieving run {run_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve run details.")

# --- Static Files ---
# Serve the frontend (index.html) from the /web directory.
# This must be defined after all other routes.
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="static")
