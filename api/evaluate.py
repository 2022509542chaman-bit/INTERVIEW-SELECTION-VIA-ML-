"""Ultra-minimal ML Evaluator API for Vercel serverless"""

import json
import sys
from pathlib import Path
from typing import Optional

# Minimal FastAPI import
try:
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except Exception as e:
    print(f"FastAPI import error: {e}")
    raise

app = FastAPI(title="ML Evaluator API", docs_url=None, openapi_url=None)

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
        try:
            backend_path = Path(__file__).parent.parent / "ml-evaluator" / "backend"
            sys.path.insert(0, str(backend_path))
            from ml_engine import process_evaluation_request
            _engine = process_evaluation_request
            print("✓ ML engine loaded")
        except Exception as e:
            print(f"ML engine load error: {e}")
            raise
    return _engine


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/evaluate")
async def evaluate_candidates(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...),
):
    """Evaluate candidates."""
    error_details = []
    
    try:
        # Read files
        try:
            cand_bytes = await candidates_file.read()
            error_details.append(f"candidates_file: {len(cand_bytes)} bytes read")
        except Exception as e:
            error_details.append(f"Error reading candidates_file: {str(e)}")
            raise
        
        try:
            rubric_bytes = await rubric_file.read()
            error_details.append(f"rubric_file: {len(rubric_bytes)} bytes read")
        except Exception as e:
            error_details.append(f"Error reading rubric_file: {str(e)}")
            raise
        
        # Validate not empty
        if not cand_bytes or not rubric_bytes:
            raise HTTPException(status_code=400, detail="Files cannot be empty")
        
        # Get engine
        engine = get_engine()
        
        # Process
        result = engine(
            cand_bytes,
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
        trace = traceback.format_exc()
        print(f"ERROR: {str(e)}")
        print(trace)
        error_msg = f"Failed: {str(e)}. Debug: {'; '.join(error_details)}"
        raise HTTPException(status_code=500, detail=error_msg)

