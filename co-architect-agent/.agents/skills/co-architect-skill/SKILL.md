
---
name: Co-Architect Skill
description: Instructions to effectively validate codebases for software architecture and design principles using the 'architecture-principles-mcp' server and document findings with clear severity rankings.
---

# Co-Architect Skill Guidelines

This skill equips the agent to perform comprehensive architectural reviews on a codebase by leveraging the `architecture-principles-mcp` server. It outlines how to fetch, read, and apply design principles to evaluate code quality, and provides a standardized framework to report issues by severity.

---

## 🚀 Workflow for Codebase Architecture Reviews

Whenever a user requests an architectural review, code validation, or design inspection, execute the following workflow:

### Step 1: Discover Principles
Call the `list_principles` tool on the `architecture-principles-mcp` server to find out what design principles are currently available in the system.

### Step 2: Fetch Principle References
For any targeted design principle (e.g. `SingleResponsibility`, `DependencyInversion`), retrieve its full guidelines using the `get_principle` tool (or via the `principles://{name}` resource URI). This ensures you have the exact definition, violation models, and refactoring techniques in your immediate context.

### Step 3: Execute Automated Validation
Run the `validate_code` tool on the source code files. This performs AST-based rule checking (detecting long classes, too many methods, naming anti-patterns, and direct concrete instantiations) and generates an initial structural analysis report with an Architecture Quality Score.

### Step 4: Perform Manual/Deep Architectural Analysis
Automated AST tools only catch structural patterns. Perform a deep semantic review of the codebase using the principles retrieved in Step 2:
- **Single Responsibility (SRP)**: Inspect if a class is serving multiple external stakeholders/actors (e.g., mixing database logic, email-sending logic, and UI display).
- **Open/Closed (OCP)**: Check for massive `if-elif` or `switch` chains matching on types/strings that should be refactored into polymorphic subclasses.
- **Liskov Substitution (LSP)**: Verify that subclasses don't break base-class invariants or raise `NotImplementedError` for inherited methods.
- **Interface Segregation (ISP)**: Look for large interfaces that force classes to implement stub methods they don't need.
- **Dependency Inversion (DIP)**: Verify that high-level modules interact with abstractions (abstract base classes or protocols) rather than direct concrete details.

---

## ⚠️ Severity Classification Framework

When documenting architectural issues and violations, classify and group your findings using the following severity levels:

### 🚨 Severe (Critical)
- **Definition**: Fundamental architectural violations that severely compromise testability, modularity, and extensibility. 
- **Examples**:
  - Direct database connections or low-level SMTP instantiations hardcoded inside high-level business services (strict DIP violation).
  - Massive "God Classes" mixing domain business logic, data persistence, and networking.
  - Cyclic dependencies between packages.
- **Impact**: Code cannot be unit tested in isolation without spawning live infrastructure.

### 🟠 High
- **Definition**: Significant design issues that heavily couple modules and make refactoring difficult.
- **Examples**:
  - Class name anti-patterns (e.g., `DataManager`, `CommonHelper`) coupled with a high method count (> 10 methods).
  - Multiple class definitions with mixed, non-cohesive responsibilities within a single file.
  - Subclasses overriding base class methods to alter argument or return types (LSP violation).
- **Impact**: High risk of regression errors when adding new features.

### 🟡 Medium
- **Definition**: Moderate design smells that reduce readability and ease of maintenance.
- **Examples**:
  - Classes approaching limits (e.g., class length > 120 lines or 6 methods).
  - Extensive `if-elif` blocks on string types (potential OCP smell).
  - Standard helper class coupling where dependency injection is omitted but mockable.
- **Impact**: Makes the codebase harder for new developers to understand and navigate.

### 🟢 Low
- **Definition**: Minor structural smells, naming issues, or stylistic inconsistencies.
- **Examples**:
  - Non-descriptive names, or using generic suffixes without breaking functional boundaries.
  - Missing type hints on public method signatures.
  - Outdated or missing docstrings describing class responsibilities.
- **Impact**: Negligible impact on design, but reduces self-documentation quality.

---

## 📋 Evaluation Report Template

Format your architectural review findings using this structured layout:

```markdown
# 🏗️ Software Architecture Evaluation Report

## 1. Executive Summary
- **Overall Quality Score**: [0 - 100] (from the MCP server or custom calculation)
- **Core Summary**: A brief paragraph summarizing the current architectural health of the analyzed code.

## 2. Severity Breakdown
| Severity | Count | Primary Smells Identified |
| :--- | :--- | :--- |
| 🚨 Severe | 0 | - |
| 🟠 High | 0 | - |
| 🟡 Medium | 0 | - |
| 🟢 Low | 0 | - |

## 3. Detailed Findings Grouped by Severity

### 🚨 Severe Findings
#### [Finding Name] (e.g., Hardcoded Database Dependency)
- **Location**: `filename.py:L123`
- **Principle Violated**: `DependencyInversion`
- **Description**: Detailed explanation of the coupling.
- **👉 Refactoring Suggestion**: Code snippet of the current code vs. the proposed refactored solution.

### 🟠 High / 🟡 Medium Findings
... [similar structure] ...

## 4. Prioritized Action Plan
1. **Phase 1 (Immediate)**: Address all `Severe` violations (e.g., inject repositories).
2. **Phase 2 (Subsequent)**: Address `High` & `Medium` issues (e.g., split large helper classes).
```
