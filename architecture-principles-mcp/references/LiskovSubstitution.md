# Liskov Substitution Principle (LSP)

The **Liskov Substitution Principle (LSP)** states that:
> "Subtypes must be substitutable for their base types."

If class `S` is a subtype of class `T`, then objects of type `T` in a program may be replaced with objects of type `S` without altering any of the desirable properties of that program (e.g. correctness, task performed).

---

## Code Examples

### ❌ Violation Example
Overriding behavior in a subclass that violates the contracts of the base class. A classic example is the Square inheriting from Rectangle.

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def set_width(self, width: float):
        self.width = width

    def set_height(self, height: float):
        self.height = height

    def get_area(self) -> float:
        return self.width * self.height


class Square(Rectangle):
    def __init__(self, size: float):
        super().__init__(size, size)

    # Violation: Violates Rectangle's invariant that width and height can vary independently!
    def set_width(self, width: float):
        self.width = width
        self.height = width

    def set_height(self, height: float):
        self.width = height
        self.height = height
```

---

###  Compliance Example
Use composition or a common abstraction that doesn't enforce invalid invariants.

```python
from abc import ABC, abstractmethod


class Polygon(ABC):
    @abstractmethod
    def get_area(self) -> float:
        pass


class Rectangle(Polygon):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def get_area(self) -> float:
        return self.width * self.height


class Square(Polygon):
    def __init__(self, side: float):
        self.side = side

    def get_area(self) -> float:
        return self.side * self.side
```
