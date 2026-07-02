# Architecture Principles MCP Server 🏗️

A Model Context Protocol (MCP) server written in Python that hosts, describes, and validates software architecture and design principles (such as SOLID). It provides both informative resources and automated, rule-based static analysis heuristics to evaluate and score code snippets for architectural compliance.

---

## Features

### 📖 1. MCP Resources
- **URI Scheme**: `principles://{principle_name}`
- Dynamically loads and serves raw Markdown documentation for design principles stored inside the `references/` directory.

### 🛠️ 2. MCP Tools
- **`list_principles()`**: Lists all available design principles alongside their summaries.
- **`get_principle(name: str)`**: Retrieves the raw Markdown documentation of a requested principle (e.g., `SingleResponsibility`, `DependencyInversion`).
- **`validate_code(code: str, principle: str)`**: Parses a Python snippet into an Abstract Syntax Tree (AST), executes heuristic quality checks for the selected design principle (or `"all"`), and outputs a highly detailed, human/LLM-readable markdown architectural validation report complete with a scoring metric (0-100).

---

## Static Validation Heuristics

The server does not require an LLM or external web calls to analyze code; instead, it uses Python's standard `ast` library to run fast, robust static analysis rules:

### 🧩 Single Responsibility Principle (SRP)
- **Class Length**: Flags any class exceeding **150 lines of code** (classes should be concise and focused).
- **Method Count**: Flags any class defining more than **7 methods** (large interfaces indicate too many responsibilities).
- **Naming Anti-Patterns**: Flags any class whose name contains generic catch-all words such as `Manager`, `Helper`, `Utility`, `Common`, `Handler`, or `Controller`.

### 🔄 Dependency Inversion Principle (DIP)
- **Direct Constructor Instantiation**: Inspects constructors (`__init__`) and method bodies to find hardcoded instantiations of external custom classes (detected by PEP 8 PascalCase class names, while ignoring builtins and standard exceptions).
- **Dependency Injection Check**: Encourages developers to pass abstract interfaces or objects as constructor arguments rather than hardcoding concrete dependencies inside the class.

---

## Requirements & Dependencies

- **Python**: `>= 3.10`
- **Core Dependencies**:
  - `mcp>=1.1.0` (The official Model Context Protocol Python SDK)
  - `pydantic>=2.0` (For robust JSON schemas and internal data validation)
- **Developer Dependencies**:
  - `pytest>=7.0` (For executing unit tests)

---

## Installation

### 1. Navigate to the project directory

```bash
cd architecture-principles-mcp
```

### 2. Create a Python virtual environment

A virtual environment keeps the project's dependencies isolated from your system Python installation.

```bash
python3 -m venv .venv
```

This creates a `.venv/` folder in the project root containing a clean Python interpreter and `pip`.

### 3. Activate the virtual environment

| Platform | Shell | Command |
|----------|-------|---------|
| macOS / Linux | bash / zsh | `source .venv/bin/activate` |
| Windows | Command Prompt | `.venv\Scripts\activate.bat` |
| Windows | PowerShell | `.venv\Scripts\Activate.ps1` |

Once activated, your shell prompt will be prefixed with `(.venv)`, confirming the environment is active:

```bash
source .venv/bin/activate
# (.venv) $
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

To also install developer dependencies (e.g., `pytest` for running tests):

```bash
pip install ".[dev]"
```

### 5. Verify the installation

```bash
python3 -c "import mcp; import pydantic; print('Dependencies OK')"
```

### 6. Deactivating the virtual environment

When you are done working on the project, deactivate the environment to restore your system Python:

```bash
deactivate
```

> [!TIP]
> Add `.venv/` to your `.gitignore` to avoid committing the virtual environment to version control.

---

## Running the Server

By default, the server runs over standard input/output (stdio) transport, which is the protocol standard for local integrations.

Ensure your virtual environment is activated first, then run:

```bash
source .venv/bin/activate   # if not already active
python3 src/server.py
```

---

## Integration Guide

To connect this MCP server to your favorite AI assistant or IDE, add it to your configuration file.

### 1. Claude Desktop
Add the following configuration to your `claude_desktop_config.json` file (typically located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "architecture-principles": {
      "command": "/Users/raja/appdev/Autonomous Co-Architect/architecture-principles-mcp/.venv/bin/python3",
      "args": [
        "/Users/raja/appdev/Autonomous Co-Architect/architecture-principles-mcp/src/server.py"
      ]
    }
  }
}
```

> [!NOTE]
> Using the **venv's Python interpreter** (`/.venv/bin/python3`) directly means Claude Desktop will automatically use the correct isolated environment — no `PYTHONPATH` hacks needed. Adjust the absolute paths to match your local setup.

### 2. Cursor or Windsurf IDE
1. Open your IDE Settings.
2. Search or navigate to the **MCP** section.
3. Click **Add New MCP Server**.
4. Configure the settings:
   - **Name**: `Architecture Principles`
   - **Type**: `command`
   - **Command**: `"/Users/raja/appdev/Autonomous Co-Architect/architecture-principles-mcp/.venv/bin/python3" "/Users/raja/appdev/Autonomous Co-Architect/architecture-principles-mcp/src/server.py"`

---

## Usage Examples (MCP Tools)

### `validate_code`
**Input code**:
```python
class EmailManager:
    def __init__(self):
        # Violation: Direct instantiations of SMTPClient coupling the code!
        self.client = SMTPClient()

    def send(self, to_addr, msg):
        self.client.send(to_addr, msg)
```

**Output markdown report**:
> ## 🏗️ Architectural Validation Report
> **Status**: ❌ NON-CONFORMING
> **Architecture Quality Score**: `65/100`
>
> ### 🔍 Identified Architectural Issues & Violations:
> 1. **[⚠️ WARNING]** in Class `EmailManager` (Line 1):
>    - **Rule**: `SRP_Naming_AntiPattern`
>    - **Issue**: Class 'EmailManager' uses generic term 'manager' in its name.
>    - **👉 Suggestion**: *Rename 'EmailManager' to focus on a specific singular responsibility and avoid generic catch-all suffixes.*
>
> 2. **[🚨 ERROR]** in Class `EmailManager` (Line 4):
>    - **Rule**: `DIP_Hardcoded_Dependency`
>    - **Issue**: Method '__init__' directly instantiates concrete class 'SMTPClient'.
>    - **👉 Suggestion**: *Invert the dependency. Pass 'SMTPClient' (or an abstract interface) as a parameter in the constructor or method, rather than hardcoding its creation.*

---

## Running Unit Tests

We have implemented extensive test cases to verify both the AST parser rules and the server tools directly.

Run the test suite using `pytest`:
```bash
python3 -m pytest tests/
```

Expected output:
```text
============================= test session starts ==============================
collected 13 items

tests/test_server.py .......                                             [ 53%]
tests/test_validator.py ......                                           [100%]

============================== 13 passed in 0.44s ==============================
```

---

## Extending the Server

It is incredibly easy to add new architectural principles to this server:
1. Create a new markdown file inside the `references/` directory (e.g., `references/Don-t-Repeat-Yourself.md`).
2. The server will **automatically** register it under the `principles://{your_new_principle}` resource and list it via the `list_principles` tool on subsequent startups!
