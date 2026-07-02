import ast
from pydantic import BaseModel
from typing import List, Set

class Finding(BaseModel):
    class_name: str
    rule_name: str
    severity: str  # "warning" or "error"
    message: str
    line_number: int
    suggestion: str

class ValidationReport(BaseModel):
    is_conforming: bool
    findings: List[Finding]
    score: int  # 0 to 100

# Set of standard builtins or common decorators/callables starting with uppercase
# or common safe lowercase structures that we shouldn't flag as DIP violations.
SAFE_CALLS: Set[str] = {
    "Exception", "ValueError", "TypeError", "RuntimeError", "KeyError", "IndexError",
    "AttributeError", "AssertionError", "StopIteration", "dict", "list", "set", "tuple",
    "str", "int", "float", "bool", "super", "range", "enumerate", "zip", "len", "sum",
    "any", "all", "print", "open", "dir", "id", "map", "filter", "hasattr", "getattr",
    "setattr", "delattr", "isinstance", "issubclass", "dataclass", "property", "classmethod",
    "staticmethod", "object", "bytes", "bytearray"
}

class ArchitectureValidator:
    """Performs static code validation using AST analysis to check for design principles."""

    @staticmethod
    def validate(code: str, target_principle: str = "all") -> ValidationReport:
        findings: List[Finding] = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationReport(
                is_conforming=False,
                findings=[
                    Finding(
                        class_name="N/A",
                        rule_name="SyntaxError",
                        severity="error",
                        message=f"Failed to parse python code: {str(e)}",
                        line_number=e.lineno or 1,
                        suggestion="Ensure the provided code is valid Python syntax."
                    )
                ],
                score=0
            )

        target_principle = target_principle.lower().strip()

        # Extract all class definitions
        class_defs = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for class_def in class_defs:
            class_name = class_def.name
            
            # 1. Single Responsibility Principle (SRP) checks
            if target_principle in ("all", "singleresponsibility", "srp"):
                # Heuristic A: Name contains generic suffixes indicating lack of focus
                generic_suffixes = ["manager", "helper", "utility", "common", "handler", "util", "controller"]
                for suffix in generic_suffixes:
                    if class_name.lower().endswith(suffix) or f"{suffix}_" in class_name.lower():
                        findings.append(Finding(
                            class_name=class_name,
                            rule_name="SRP_Naming_AntiPattern",
                            severity="warning",
                            message=f"Class '{class_name}' uses generic term '{suffix}' in its name.",
                            line_number=class_def.lineno,
                            suggestion=f"Rename '{class_name}' to focus on a specific singular responsibility and avoid generic catch-all suffixes."
                        ))
                        break

                # Heuristic B: Class Length (excluding comments/blank lines in AST is hard, so we use actual lines range in code)
                class_lines = class_def.end_lineno - class_def.lineno + 1
                if class_lines > 150:
                    findings.append(Finding(
                        class_name=class_name,
                        rule_name="SRP_Class_Too_Long",
                        severity="warning",
                        message=f"Class '{class_name}' is very long ({class_lines} lines).",
                        line_number=class_def.lineno,
                        suggestion="Consider breaking this class down into smaller, highly cohesive classes each handling one concern."
                    ))

                # Heuristic C: Method Count
                methods = [node for node in class_def.body if isinstance(node, ast.FunctionDef)]
                method_count = len(methods)
                if method_count > 7:
                    findings.append(Finding(
                        class_name=class_name,
                        rule_name="SRP_Too_Many_Methods",
                        severity="warning",
                        message=f"Class '{class_name}' defines {method_count} methods.",
                        line_number=class_def.lineno,
                        suggestion="Large method count suggests multiple responsibilities. Extract groups of related methods into helper or strategy classes."
                    ))

            # 2. Dependency Inversion Principle (DIP) checks
            if target_principle in ("all", "dependencyinversion", "dip"):
                # Find __init__ method parameters to check constructor injection
                init_method = None
                for node in class_def.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                        init_method = node
                        break

                # Get the set of parameter names passed into __init__
                init_param_names = set()
                if init_method:
                    for arg in init_method.args.args:
                        if arg.arg != "self":
                            init_param_names.add(arg.arg)

                # Scan all methods for hardcoded concrete class instantiations
                for node in class_def.body:
                    if isinstance(node, ast.FunctionDef):
                        # Walk the AST inside this method to find instantiations
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                called_name = None
                                # Check if calling an identifier e.g. MyClient()
                                if isinstance(child.func, ast.Name):
                                    called_name = child.func.id
                                # Check if calling an attribute e.g. clients.MyClient()
                                elif isinstance(child.func, ast.Attribute):
                                    called_name = child.func.attr

                                if called_name:
                                    # Heuristic: Uppercase-starting name (PEP 8 class naming convention)
                                    # that is not a safe builtin/type, and is not in the parameter names.
                                    if (called_name[0].isupper() 
                                        and called_name not in SAFE_CALLS 
                                        and called_name.lower() not in init_param_names):
                                        
                                        findings.append(Finding(
                                            class_name=class_name,
                                            rule_name="DIP_Hardcoded_Dependency",
                                            severity="error",
                                            message=f"Method '{node.name}' directly instantiates concrete class '{called_name}'.",
                                            line_number=child.lineno,
                                            suggestion=(f"Invert the dependency. Pass '{called_name}' (or an abstract interface) as a parameter "
                                                        f"in the constructor or method, rather than hardcoding its creation.")
                                        ))

        # Calculate a simple architectural compliance score
        # Start at 100, deduct 10 for each warning, 25 for each error, bounded between 0 and 100.
        score = 100
        for finding in findings:
            if finding.severity == "error":
                score -= 25
            else:
                score -= 10
        score = max(0, min(100, score))

        is_conforming = len(findings) == 0

        return ValidationReport(
            is_conforming=is_conforming,
            findings=findings,
            score=score
        )
