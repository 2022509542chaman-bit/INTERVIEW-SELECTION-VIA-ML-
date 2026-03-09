#!/usr/bin/env python3
"""Start the ML Evaluator API server."""
import sys
import os

# Ensure we're in the backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
