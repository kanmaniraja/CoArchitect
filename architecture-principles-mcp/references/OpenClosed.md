# Open/Closed Principle (OCP)

The **Open/Closed Principle (OCP)** states that:
> "Software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification."

This means that you should be able to extend a class's behavior without modifying its existing source code. Doing so prevents regression bugs in tested code and keeps classes simple and modular.

---

## Code Examples

### ❌ Violation Example
An `if-elif` chain or `switch` matching on types or strings inside a method is a classic OCP violation. Adding a new shape requires modifying the `AreaCalculator.calculate_area` method.

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height


class Circle:
    def __init__(self, radius: float):
        self.radius = radius


class AreaCalculator:
    def calculate_area(self, shapes: list) -> float:
        total_area = 0.0
        for shape in shapes:
            # Violation: Modifying this class is required to add new shapes
            if isinstance(shape, Rectangle):
                total_area += shape.width * shape.height
            elif isinstance(shape, Circle):
                import math
                total_area += math.pi * (shape.radius ** 2)
        return total_area
```

---

###  Compliance Example
Use polymorphism. Define an interface and let each shape compute its own area.

```python
from abc import ABC, abstractmethod
import math


class Shape(ABC):
    @abstractmethod
    def get_area(self) -> float:
        pass


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def get_area(self) -> float:
        return self.width * self.height


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def get_area(self) -> float:
        return math.pi * (self.radius ** 2)


class AreaCalculator:
    def calculate_area(self, shapes: list[Shape]) -> float:
        # Compliance: Calculator does not change when shapes are added
        return sum(shape.get_area() for shape in shapes)
```
