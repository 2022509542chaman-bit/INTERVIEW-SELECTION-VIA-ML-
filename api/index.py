"""
Vercel Serverless Backend using FastAPI
"""

import os
import sys
from typing import Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'ml-evaluator', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_ml_engine = None

def get_ml_engine():
    global _ml_engine
    if _ml_engine is None:
        try:
            from ml_engine import process_evaluation_request
            _ml_engine = process_evaluation_request
            print("✓ ML Engine loaded")
        except Exception as e:
            print(f"✗ ML Engine error: {e}")
            raise
    return _ml_engine

@app.get("/api/health")
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml-evaluator-api"}

@app.post("/api/evaluate")
@app.post("/evaluate")
async def evaluate(candidates_file: UploadFile = File(...), rubric_file: UploadFile = File(...)):
    try:
        candidates_data = await candidates_file.read()
        rubric_data = await rubric_file.read()
        
        candidates_text = candidates_data.decode('utf-8')
        rubric_text = rubric_data.decode('utf-8')
        
        ml_engine = get_ml_engine()
        results = ml_engine(
            candidates_csv=candidates_text,
            rubric_text=rubric_text
        )
        
        return JSONResponse(results)
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/")
@app.get("/api")
async def root():
    return {"message": "ML Evaluator API"}

# Required for Vercel
handler = app

