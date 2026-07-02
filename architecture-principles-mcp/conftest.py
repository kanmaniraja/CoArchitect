import sys
import os

# Ensure the project root is on sys.path so 'src' package is importable
sys.path.insert(0, os.path.dirname(__file__))
# Ensure tests/ is on sys.path so validator.py (co-located there) is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))
