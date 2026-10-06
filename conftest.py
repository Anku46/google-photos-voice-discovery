"""conftest.py — pytest configuration for the project root."""
import sys
from pathlib import Path

# Make `src/` importable as a package when running pytest from the project root.
sys.path.insert(0, str(Path(__file__).parent))
