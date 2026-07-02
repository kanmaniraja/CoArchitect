# Co-Architect CLI Agent 🤖📐

This is an automated, CLI-based architectural evaluation agent built using the **Antigravity SDK 2.0 (ADK 2.0)**. 

The agent is designed to inspect, evaluate, and score Python source files and directories against software architecture and SOLID design principles. It works by seamlessly orchestrating:
1. **The Custom Skill (`co-architect-skill`)**: Guides the agent's semantic analysis, grading system, severity definitions (`Severe`, `High`, `Medium`, `Low`), and reporting templates.
2. **The MCP Server (`architecture-principles-mcp`)**: Exposes structural validation tools and dynamic Markdown design principle references.

---

## Features

- **Automated Single File Analysis**: Reads code from a specified Python file and prompts the agent to perform an evaluation using its local skills and connected MCP tools.
- **Automated Directory Analysis**: Prompts the agent to scan and read Python files inside a directory to perform a unified architectural health assessment of a whole component or module.
- **Interactive Chat Loop**: Enters a console-based conversation panel with the virtual Software Architect where you can discuss refactorings, ask design questions, or paste snippets manually.
- **Severity Ranking**: Groups findings into `Severe` (Critical), `High`, `Medium`, and `Low` with clear before/after refactored code blocks in the output.

---

## Requirements & Setup

1. **Python**: `>= 3.10`
2. **Dependencies**:
   - `google-antigravity` (The core Antigravity SDK 2.0)
   - `pydantic`
   - `mcp`

Install requirements in your virtual environment:
```bash
pip install google-antigravity pydantic mcp
```

---

## How to Run

Ensure you have your target API keys or credentials set in your environment if required by your default SDK client.

### 1. View Help Menu
```bash
./co_architect_cli.py --help
```

### 2. Evaluate a Single File
Evaluate a target Python file (e.g., `my_script.py`) against all principles:
```bash
./co_architect_cli.py --file path/to/my_script.py
```

Target a specific design principle:
```bash
./co_architect_cli.py --file path/to/my_script.py --principle SingleResponsibility
```

### 3. Evaluate an Entire Directory
Ask the agent to discover and analyze all Python files in a directory:
```bash
./co_architect_cli.py --dir path/to/project_module/
```

### 4. Enter Interactive Console Chat
Start an interactive chat session with the senior software architect:
```bash
./co_architect_cli.py --interactive
```

---

## Architecture and Integration

The CLI agent initializes its environment with a local configuration defined dynamically inside `co_architect_cli.py`:

```python
config = LocalAgentConfig(
    system_instructions="...",
    capabilities=CapabilitiesConfig(),
    mcp_servers=[mcp_server],
    skills_paths=[SKILLS_DIR],
    model="gemini-3.5-flash"
)
```

- **`mcp_servers`**: Directly launches the Python-based `architecture-principles-mcp` server on startup via standard `stdio` transport.
- **`skills_paths`**: Automatically registers the workspace customizations located under `.agents`, activating the `co-architect-skill` instructions.
