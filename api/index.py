"""
Vercel Serverless Backend using FastAPI
Handles /api/* routes for ML evaluation
"""

import os
import sys
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml-evaluator', 'backend'))

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy ML engine loading
_ml_engine = None

def get_ml_engine():
    global _ml_engine
    if _ml_engine is None:
        try:
            from ml_engine import process_evaluation_request
            _ml_engine = process_evaluation_request
            print("✓ ML Engine loaded successfully")
        except Exception as e:
            print(f"✗ ML Engine load failed: {e}")
            raise
    return _ml_engine

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return JSONResponse({"status": "ok", "timestamp": "ok"})

@app.post("/api/evaluate")
async def evaluate(candidates_file: UploadFile = File(...), rubric_file: UploadFile = File(...)):
    """
    Evaluate candidates against rubric.
    Receives CSV and TXT files, returns JSON results.
    """
    try:
        # Read files
        candidates_data = await candidates_file.read()
        rubric_data = await rubric_file.read()
        
        candidates_text = candidates_data.decode('utf-8')
        rubric_text = rubric_data.decode('utf-8')
        
        # Get ML engine
        ml_engine = get_ml_engine()
        
        # Process
        results = ml_engine(
            candidates_csv=candidates_text,
            rubric_text=rubric_text
        )
        
        return JSONResponse(results)
        
    except Exception as e:
        print(f"Evaluation error: {e}")
        return JSONResponse({"error": str(e), "type": type(e).__name__}, status_code=400)

# Health check at root
@app.get("/")
async def root():
    return JSONResponse({"message": "ML Evaluator API - Use /api/evaluate or /api/health"})

# For Vercel
handler = app

