# Dependency Inversion Principle (DIP)

The **Dependency Inversion Principle (DIP)** is the fifth SOLID principle. It states that:
> 1. "High-level modules should not import or depend on low-level modules. Both should depend on abstractions."
> 2. "Abstractions should not depend on details. Details (concrete implementations) should depend on abstractions."

Traditionally, high-level policies (like business logic) import and depend on low-level utility modules (like databases, APIs, file systems). DIP "inverts" this relationship, so that both layers depend on a common abstract interface, decoupling the business domain from infrastructure details.

---

## Key Concepts

- **Abstractions**: In Python, these are represented by Abstract Base Classes (ABCs) or Protocols (structural typing/interfaces).
- **Dependency Injection (DI)**: The practice of passing dependencies into a class (usually via its constructor) rather than letting the class instantiate them itself.
- **Inversion of Control (IoC)**: Transferring control of object creation and lifecycle management to an external runner or container.

---

## Common Code Smells & Violations

1. **Hardcoded Instantiation**: A class creating instances of its dependencies inside its own `__init__` constructor using direct class calls (e.g., `self.db = PostgreSQLClient()`).
2. **Concrete Imports**: High-level core business services directly importing concrete client implementations from database, disk, or network packages.
3. **Rigid Modification**: When swapping out a service (e.g., changing from SendGrid to Mailchimp) requires editing the core business classes.

---

## Code Examples

### ❌ Violation Example
Here, the high-level `NotificationManager` directly imports and instantiates the concrete `SMTPClient`. If we want to switch to a SMS or Slack notifier, we are forced to rewrite `NotificationManager`.

```python
class SMTPClient:
    def send(self, recipient: str, message: str):
        print(f"Sending SMTP email to {recipient}: {message}")


class NotificationManager:
    def __init__(self):
        # Violation: Direct concrete instantiation coupling NotificationManager to SMTPClient
        self.client = SMTPClient()

    def send_notification(self, user_email: str, content: str):
        self.client.send(user_email, content)
```

---

###  Compliance Example
To comply with DIP, we define an abstract interface (`NotificationSender`) using Python's `abc` module. The `NotificationManager` depends entirely on this interface, and concrete clients are injected into its constructor.

```python
from abc import ABC, abstractmethod


# Abstraction (Interface)
class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str):
        pass


# Concrete Implementation 1
class SMTPClient(NotificationSender):
    def send(self, recipient: str, message: str):
        print(f"SMTP to {recipient}: {message}")


# Concrete Implementation 2
class SMSClient(NotificationSender):
    def send(self, recipient: str, message: str):
        print(f"SMS to {recipient}: {message}")


# High-Level Module complying with DIP
class NotificationManager:
    def __init__(self, sender: NotificationSender):
        # Compliance: Depends on the abstraction, injected at construction
        self.sender = sender

    def send_notification(self, recipient: str, content: str):
        self.sender.send(recipient, content)


# Usage (Inversion of Control)
smtp_sender = SMTPClient()
sms_sender = SMSClient()

# We can easily swap implementations without modifying the NotificationManager class!
manager_email = NotificationManager(smtp_sender)
manager_sms = NotificationManager(sms_sender)
```

---

## Automated Validation Heuristics

The Architecture Principles MCP Server validates Python code against DIP using these heuristics:
- **Direct Constructor Instantiation**: Inspects class methods (`__init__` and others) to detect instantiations of local or external objects (e.g. `self.db = ...()`).
- **Constructor Dependencies**: Checks if classes that reference dependency instances accept those dependencies as constructor parameters rather than creating them.
