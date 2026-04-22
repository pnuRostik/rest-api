"""Pytest: set env before any test module imports `main` (engine is created at import)."""

import os

os.environ["TESTING"] = "1"
