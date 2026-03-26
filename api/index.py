#!/usr/bin/env python3
"""Vercel serverless function for ML Evaluator backend"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "ml-evaluator" / "backend"
sys.path.insert(0, str(backend_path))

from evaluate import app

# Export the FastAPI app for Vercel
__all__ = ["app"]


