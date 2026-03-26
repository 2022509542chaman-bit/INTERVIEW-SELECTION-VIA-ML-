"""Simplified ML Evaluator API for Vercel serverless"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "ml-evaluator" / "backend"
sys.path.insert(0, str(backend_path))

app = FastAPI(title="ML Evaluator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy load ML engine
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        from ml_engine import process_evaluation_request
        _engine = process_evaluation_request
    return _engine


# Simple response model
class EvaluationResponse(BaseModel):
    status: str
    data: list
    summary: dict
    eval_time_seconds: float
    batch_id: int = 0


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/evaluate")
async def evaluate_candidates(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...),
):
    """Evaluate candidates - simplified endpoint for Vercel."""
    try:
        # Validate files
        if not candidates_file or not rubric_file:
            raise HTTPException(status_code=400, detail="Both candidates_file and rubric_file are required")
        
        # Read files
        candidates_bytes = await candidates_file.read()
        rubric_bytes = await rubric_file.read()
        
        if not candidates_bytes or not rubric_bytes:
            raise HTTPException(status_code=400, detail="Files cannot be empty")
        
        # Process evaluation
        engine = get_engine()
        result = engine(
            candidates_bytes,
            rubric_bytes,
            candidates_file.filename or "candidates"
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        result["batch_id"] = 0
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
