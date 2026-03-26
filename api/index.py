"""
Vercel Serverless Backend
- Serves frontend from /ml-evaluator/frontend/dist
- Handles /evaluate API endpoint
- Lazy loads ML models on first request
"""

import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml-evaluator', 'backend'))

from fastapi import FastAPI, UploadFile, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import io
import csv
import json

# Lazy ML engine import
_ml_engine = None

def get_ml_engine():
    global _ml_engine
    if _ml_engine is None:
        from ml_engine import process_evaluation_request
        _ml_engine = process_evaluation_request
    return _ml_engine

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/evaluate")
async def evaluate(candidates_file: UploadFile = File(...), rubric_file: UploadFile = File(...)):
    """
    Evaluate candidates against rubric.
    Lazy loads ML models on first request.
    """
    try:
        # Read uploaded files
        candidates_data = await candidates_file.read()
        rubric_data = await rubric_file.read()
        
        candidates_text = candidates_data.decode('utf-8')
        rubric_text = rubric_data.decode('utf-8')
        
        # Get ML engine (lazy loads on first request)
        ml_engine = get_ml_engine()
        
        # Process evaluation
        results = ml_engine(
            candidates_csv=candidates_text,
            rubric_text=rubric_text
        )
        
        return results
        
    except Exception as e:
        return {"error": str(e)}, 400

# Serve frontend if it exists
frontend_dist = os.path.join(os.path.dirname(__file__), '..', 'ml-evaluator', 'frontend', 'dist')
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

# Export for Vercel
export = app

