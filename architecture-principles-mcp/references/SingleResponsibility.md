# Single Responsibility Principle (SRP)

The **Single Responsibility Principle (SRP)** states that:
> "A module, class, or function should have one, and only one, reason to change."

In other words, a class should do one thing and do it well. When a class has multiple responsibilities, those responsibilities become coupled, leading to fragile designs that are hard to maintain, test, and extend.

---

## Key Concepts

- **Cohesion**: High cohesion indicates that all elements of a class or module are closely related to a single task. SRP promotes high cohesion.
- **Responsibility**: A "responsibility" is defined as a family of functions that serves a particular actor or business function.
- **Actor**: An actor is a group of users or stakeholders who require a specific change in the software. If a class serves multiple actors, it violates SRP.

---

## Common Code Smells & Violations

1. **Large Classes (God Classes)**: A class containing hundreds of lines of code and many methods.
2. **Generic Suffixes**: Names ending with `Manager`, `Helper`, `Utility`, `Common`, or `Handler` often indicate a dump of unrelated functions.
3. **Mixed Concerns**: 
   - A data entity/model that also handles database persistence (Active Record pattern can violate SRP if mixed with business logic).
   - A business logic class that also handles logging, UI rendering, or network requests.
4. **Too Many Imports**: A module importing components from completely different layers (e.g., database drivers, UI kits, and crypto libraries) inside a single file.

---

## Code Examples

### ❌ Violation Example
In this example, the `User` class holds user data, validates email, manages database persistence, and sends emails. It has at least four reasons to change (data schema, validation rules, database technology, email API).

```python
class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    def get_details(self) -> str:
        return f"{self.username} ({self.email})"

    def validate_email(self) -> bool:
        return "@" in self.email

    def save_to_database(self):
        # Database persistence logic
        print(f"Saving {self.username} to DB...")
        db_connection = "postgresql://localhost:5432"
        # ... SQL connection and insert queries ...

    def send_welcome_email(self):
        # Email transmission logic
        print(f"Sending welcome email to {self.email}...")
        smtp_server = "smtp.mailprovider.com"
        # ... SMTP send mail queries ...
```

---

###  Compliance Example
To satisfy SRP, we separate these concerns into four cohesive classes, each serving a single actor or concern.

```python
from dataclasses import dataclass

@dataclass
class User:
    """Pure data model representing a user."""
    username: str
    email: str


class EmailValidator:
    """Handles email formatting validation."""
    def validate(self, email: str) -> bool:
        return "@" in email and "." in email


class UserRepository:
    """Responsible for persistence operations."""
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def save(self, user: User):
        print(f"Persisting user {user.username} to database...")
        # Database code here


class EmailService:
    """Responsible for notification delivery."""
    def __init__(self, smtp_config: dict):
        self.smtp_config = smtp_config

    def send_welcome(self, user: User):
        print(f"Delivering welcome email to {user.email}...")
        # SMTP code here
```

---

## Automated Validation Heuristics

The Architecture Principles MCP Server validates Python code against SRP using these heuristics:
- **Class Length**: Flags any class exceeding **150 lines of code** (excluding comments and docs).
- **Method Count**: Flags any class defining more than **7 methods**.
- **Naming Anti-Patterns**: Flags any class with names containing `Manager`, `Helper`, `Utility`, `Common`, or `Handler`.
