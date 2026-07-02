import os
import sys
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Add the tests/ directory to sys.path so validator.py can be found
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TESTS_DIR = os.path.join(_BASE_DIR, "tests")
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from validator import ArchitectureValidator, ValidationReport

# Initialize the FastMCP server
mcp = FastMCP("ArchitecturePrinciples")

# Resolve references directory path relative to the project root (one level up from src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCES_DIR = os.path.join(BASE_DIR, "references")

def _get_available_principles() -> Dict[str, str]:
    """Helper to dynamically list all principle markdown files in the references directory."""
    principles = {}
    if not os.path.exists(REFERENCES_DIR):
        return principles
    
    for filename in os.listdir(REFERENCES_DIR):
        if filename.endswith(".md"):
            name = filename[:-3] # Strip '.md' extension
            principles[name.lower()] = filename
            
    return principles

@mcp.resource("principles://{name}")
def get_principle_resource(name: str) -> str:
    """Retrieve a software architecture/design principle's raw markdown text by name."""
    principles = _get_available_principles()
    key = name.lower().strip()
    
    if key not in principles:
        raise ValueError(
            f"Principle '{name}' not found. Available principles: {', '.join(principles.keys())}"
        )
        
    file_path = os.path.join(REFERENCES_DIR, principles[key])
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
def list_principles() -> List[Dict[str, str]]:
    """
    List all available software architecture and design principles.
    Returns their names and dynamic descriptions parsed from headers.
    """
    principles = _get_available_principles()
    results = []
    
    for name, filename in sorted(principles.items()):
        file_path = os.path.join(REFERENCES_DIR, filename)
        description = "No description available."
        
        # Read the first few lines to find a description or title
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    # Look for blockquotes or first paragraph as description
                    line = line.strip()
                    if line.startswith(">"):
                        description = line.lstrip("> ").strip()
                        break
                    elif line and not line.startswith("#"):
                        description = line
                        break
        except Exception:
            pass
            
        # Capitalize the principle name nicely
        # e.g., 'singleresponsibility' -> 'SingleResponsibility'
        display_name = filename[:-3]
        results.append({
            "name": display_name,
            "uri": f"principles://{display_name}",
            "summary": description
        })
        
    return results

@mcp.tool()
def get_principle(name: str) -> str:
    """
    Get the full raw markdown documentation of a specific design principle.
    Example name: 'SingleResponsibility', 'DependencyInversion', 'OpenClosed'.
    """
    return get_principle_resource(name)

@mcp.tool()
def validate_code(code: str, principle: str = "all") -> str:
    """
    Validate a Python code snippet against software design principles (e.g. 'SingleResponsibility', 'DependencyInversion', or 'all').
    Performs static AST rule checks and returns a comprehensive markdown report.
    """
    report: ValidationReport = ArchitectureValidator.validate(code, target_principle=principle)
    
    # Format the report as clean, readable Markdown
    status_emoji = "✅" if report.is_conforming else "❌"
    status_text = "CONFORMING" if report.is_conforming else "NON-CONFORMING"
    
    markdown_output = [
        f"## 🏗️ Architectural Validation Report",
        f"**Status**: {status_emoji} {status_text}",
        f"**Architecture Quality Score**: `{report.score}/100`",
        ""
    ]
    
    if report.is_conforming:
        markdown_output.append("Great job! The analyzed code conforms to the targeted design principles without any structural violations found.")
    else:
        markdown_output.append("### 🔍 Identified Architectural Issues & Violations:")
        markdown_output.append("")
        for idx, finding in enumerate(report.findings, 1):
            severity_badge = "⚠️ WARNING" if finding.severity == "warning" else "🚨 ERROR"
            markdown_output.extend([
                f"{idx}. **[{severity_badge}]** in Class `{finding.class_name}` (Line {finding.line_number}):",
                f"   - **Rule**: `{finding.rule_name}`",
                f"   - **Issue**: {finding.message}",
                f"   - **👉 Suggestion**: *{finding.suggestion}*",
                ""
            ])
            
    return "\n".join(markdown_output)

if __name__ == "__main__":
    mcp.run()
