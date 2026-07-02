# Interface Segregation Principle (ISP)

The **Interface Segregation Principle (ISP)** states that:
> "Clients should not be forced to depend on methods they do not use."

Instead of creating one fat, multipurpose interface, it is better to create several smaller, highly-focused interfaces.

---

## Code Examples

### ❌ Violation Example
A single large `Worker` interface forces different kinds of workers to implement irrelevant behaviors, raising `NotImplementedError`.

```python
from abc import ABC, abstractmethod


class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass


class Human(Worker):
    def work(self):
        print("Working...")

    def eat(self):
        print("Eating lunch...")


class Robot(Worker):
    def work(self):
        print("Working 24/7...")

    # Violation: Robots don't eat!
    def eat(self):
        raise NotImplementedError("Robots do not eat")
```

---

###  Compliance Example
Split the large interface into smaller, focused interfaces.

```python
from abc import ABC, abstractmethod


class Workable(ABC):
    @abstractmethod
    def work(self):
        pass


class Feedable(ABC):
    @abstractmethod
    def eat(self):
        pass


# Humans can work and eat
class Human(Workable, Feedable):
    def work(self):
        print("Working...")

    def eat(self):
        print("Eating...")


# Robots only need to work
class Robot(Workable):
    def work(self):
        print("Working 24/7...")
```
