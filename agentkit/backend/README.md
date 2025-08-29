# AgentKit Backend

This directory contains the core backend logic for the AgentKit framework, including the FastAPI server, orchestrator, and all related components.

## How to Run Locally

Follow these steps to run the AgentKit server on your local machine.

### Prerequisites
- Python 3.11 or higher
- `pip` for package management

### 1. Set up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# Navigate to the root of the agentkit project
cd /path/to/your/agentkit

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Run the Server

Use `uvicorn` to run the FastAPI application.

```bash
uvicorn agentkit.backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- `--host` and `--port` specify the address to run on.
- `--reload` enables auto-reloading, so the server will restart automatically when you change the code.

### 4. Access the Web UI

Once the server is running, open your web browser and navigate to:

**http://127.0.0.1:8000**

You should see the AgentKit web interface.

---

## Using Real Model APIs (OpenAI Example)

By default, the AgentKit uses a `mock-model` for offline testing. To connect to a real API like OpenAI, follow these steps:

### 1. Set Your API Key

You need to provide your API key as an environment variable. The recommended way to do this is to create a `.env` file in the root of the `agentkit` project.

- Make a copy of `.env.example` and name it `.env`.
- Open the `.env` file and add your OpenAI API key:

```
# .env
OPENAI_API_KEY="sk-..."
```
The application will automatically load this variable when it starts.

### 2. Select an OpenAI Model in the UI

When you run an agent from the web interface, you can specify which model to use. To use the real OpenAI API, enter one of the supported OpenAI model IDs in the "Model ID" field, such as:
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

When the orchestrator receives one of these IDs, it will automatically use the `OpenAIModelClient` to make a real API call. Any other model ID will use the `MockModelClient` as a fallback.

---

## How to Define a New Agent

Agents are defined as `.yaml` files in the `agentkit/agents/` directory. The server automatically loads and validates all YAML files from this directory on startup.

### 1. Create a YAML File

Create a new file in the `agentkit/agents/` directory, for example, `my_researcher.yaml`.

### 2. Define the Agent Structure

An agent definition has several key parts:

- `id`: A unique, machine-readable identifier for the agent.
- `name`: A human-readable name displayed in the UI.
- `description`: A short explanation of what the agent does.
- `input_schema`: A JSON schema defining the inputs the agent requires.
- `defaults`: Default run options like `step_limit` and `timeout_sec`.
- `steps`: A list of steps the agent will execute in sequence.

Each **step** has its own properties:
- `id`: A unique identifier for the step within the agent.
- `prompt_template`: A [Jinja2](https://jinja.palletsprojects.com/) template for the prompt. You can use variables from the initial `input` or the current `state` (e.g., `{{ title }}` or `{{ state.summary }}`).
- `expects`: Defines the expected output from the model (`text` or `json` with a specific `schema`).
- `update_state`: A dictionary mapping keys in the run `state` to values from the model's JSON output (using `$.` notation, e.g., `summary: $.new_summary`).
- `writes`: A list of artifacts to save to files.

### Example: A Simple Summarizer Agent

Here is an example of a simple agent that takes a piece of text and summarizes it.

```yaml
# agents/summarizer.yaml

id: summarizer
name: "Text Summarizer"
description: "Generates a one-sentence summary of a long text."
input_schema:
  type: object
  properties:
    text_to_summarize: {type: string}
  required: [text_to_summarize]
defaults:
  step_limit: 1
  timeout_sec: 45
steps:
  - id: generate_summary
    prompt_template: |
      Please summarize the following text in a single sentence:
      ---
      {{ text_to_summarize }}
      ---
      Return the result as JSON: { "summary": "..." }
    expects:
      type: json
      schema:
        type: object
        properties:
          summary: {type: string}
        required: [summary]
    update_state:
      summary: $.summary
    writes:
      - path: "summary.txt"
        from_text: "{{ state.summary }}" # Note: This shows templating in writes, a potential feature. The current impl is simpler.
```

### 3. Relaunch the Server

If the server is already running with `--reload`, it will automatically restart and load your new agent. Otherwise, stop and restart the server. Your new agent will now be available in the dropdown on the web UI.
