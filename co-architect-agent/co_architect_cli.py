#!/usr/bin/env python3
import asyncio
import sys
import os
import argparse

# Load .env file if present (must happen before importing google.antigravity)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # python-dotenv not installed; rely on the shell environment

from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
from google.antigravity.types import McpStdioServer
from google.antigravity.utils.interactive import run_interactive_loop

# Resolve relative paths
CLI_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CLI_DIR)

MCP_DIR = os.path.join(PROJECT_ROOT, "architecture-principles-mcp")
SERVER_PATH = os.path.join(MCP_DIR, "src", "server.py")
VENV_PYTHON = os.path.join(MCP_DIR, ".venv", "bin", "python3")
SKILLS_DIR = os.path.join(CLI_DIR, ".agents") # Points to customization root containing skills/

def check_dependencies():
    """Ensure the MCP server file, skills folder, and API key exist before starting."""
    if not os.path.exists(SERVER_PATH):
        print(f"❌ Error: MCP Server not found at '{SERVER_PATH}'", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(SKILLS_DIR):
        print(f"❌ Error: Skills directory not found at '{SKILLS_DIR}'", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("GEMINI_API_KEY"):
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        print(
            "❌ Error: GEMINI_API_KEY is not set.\n"
            "  Option 1 — export it in your shell before running:\n"
            "             export GEMINI_API_KEY=\"your_key_here\"\n"
            f"  Option 2 — create a .env file at '{env_file}'\n"
            "             with the line: GEMINI_API_KEY=your_key_here\n"
            "  Get a key at: https://aistudio.google.com/app/apikey",
            file=sys.stderr
        )
        sys.exit(1)

async def run_automated_evaluation(agent, target_path: str, principle: str):
    """Prompts the agent to perform an automated code or directory architectural evaluation."""
    target_abs = os.path.abspath(target_path)
    if not os.path.exists(target_abs):
        print(f"❌ Error: Target path '{target_abs}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Starting co-architect evaluation on: {target_abs}")
    print(f"🎯 Target Principles: {principle}\n" + "=" * 50 + "\n")

    if os.path.isfile(target_abs):
        # Read the file content to feed it directly to the agent's context
        try:
            with open(target_abs, "r", encoding="utf-8") as f:
                code_content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}", file=sys.stderr)
            sys.exit(1)

        prompt = f"""
Please perform a thorough architectural evaluation of the following code snippet from the file '{os.path.basename(target_abs)}'.
You must use your 'co-architect-skill' and the connected 'architecture-principles-mcp' server to fetch design principles, run validation, and formulate your findings.

Ensure you grade all architectural violations by severity (Severe, High, Medium, Low) and provide a Refactoring Action Plan containing before/after code blocks as defined in your skill.

CODE SNIPPET:
```python
{code_content}
```
"""
    else:
        # For directories, let the agent use its capabilities to inspect the files themselves
        prompt = f"""
Please perform a thorough architectural evaluation of the directory located at '{target_abs}'.
You should discover and inspect the Python files in this directory. 
You must use your 'co-architect-skill' and the connected 'architecture-principles-mcp' server to analyze the codebases.

Generate a unified, comprehensive Software Architecture Evaluation Report grading issues by severity (Severe, High, Medium, Low) and detailing a Refactoring Action Plan as instructed in your skill.
"""

    # Call the agent and stream the response token-by-token
    response = await agent.chat(prompt)
    async for token in response:
        sys.stdout.write(token)
        sys.stdout.flush()
    print("\n" + "=" * 50)
    print("✨ Architectural Evaluation Completed.")

async def main_async():
    parser = argparse.ArgumentParser(
        description="Co-Architect CLI Agent: Automated architectural evaluation of AI-generated code."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", "-f",
        help="Path to a single Python file to evaluate."
    )
    group.add_argument(
        "--dir", "-d",
        help="Path to a directory containing Python files to evaluate."
    )
    group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start an interactive chat session with the Co-Architect Agent."
    )
    parser.add_argument(
        "--principle", "-p",
        default="all",
        help="Specific design principle to target (e.g., 'SingleResponsibility', 'DependencyInversion', or 'all'). Default is 'all'."
    )
    
    args = parser.parse_args()
    check_dependencies()

    # Configure the MCP stdio server
    # Use the venv's Python so all MCP dependencies are automatically available
    mcp_python = VENV_PYTHON if os.path.exists(VENV_PYTHON) else "python3"
    mcp_server = McpStdioServer(
        name="architecture-principles",
        command=mcp_python,
        args=[SERVER_PATH]
    )

    # Set up the local agent configuration
    config = LocalAgentConfig(
        api_key=os.environ.get("GEMINI_API_KEY"),  # explicitly pass the key
        system_instructions=(
            "You are a senior Software Architect agent. Your goal is to review and evaluate "
            "codebases for architectural quality and SOLID design principles. You must leverage "
            "your local 'co-architect-skill' and the connected 'architecture-principles-mcp' server tools "
            "to perform code validation, retrieve markdown guides, and generate evaluation reports."
        ),
        capabilities=CapabilitiesConfig(),  # Equip the agent with standard read/write toolsets
        mcp_servers=[mcp_server],
        skills_paths=[SKILLS_DIR],
        model="gemini-3.5-flash"  # Use gemini-3.5-flash as the standard modern model
    )

    print("🤖 Initializing Co-Architect Agent (ADK 2.0)...")
    async with Agent(config) as agent:
        if args.interactive:
            print("🚀 Co-Architect Agent started. Entering interactive chat mode (Type 'exit' or 'quit' to end).")
            print("You can ask questions or prompt the agent to review code directly.")
            print("-" * 60)
            await run_interactive_loop(agent)
        else:
            target_path = args.file if args.file else args.dir
            await run_automated_evaluation(agent, target_path, args.principle)

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n👋 Co-Architect Agent terminated by user.")
        sys.exit(0)
