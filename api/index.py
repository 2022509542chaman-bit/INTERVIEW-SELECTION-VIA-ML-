#!/usr/bin/env python3
"""Vercel serverless function for ML Evaluator backend"""

import sys
from pathlib import Path

# Critical: Set up path BEFORE any imports
backend_path = Path(__file__).parent.parent / "ml-evaluator" / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

app = FastAPI(title="ML Evaluator API", docs_url=None, openapi_url=None)

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


# Create routers for both paths
router_root = APIRouter()
router_api = APIRouter(prefix="/api")

@router_root.get("/health")
async def health_root():
    return {"status": "ok"}

@router_api.get("/health")
async def health_api():
    return {"status": "ok"}

@router_root.post("/evaluate")
async def evaluate_root(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...),
):
    try:
        cand_bytes = await candidates_file.read()
        rubric_bytes = await rubric_file.read()
        
        if not cand_bytes or not rubric_bytes:
            raise HTTPException(status_code=400, detail="Files cannot be empty")
        
        engine = get_engine()
        result = engine(cand_bytes, rubric_bytes, candidates_file.filename or "candidates")
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        result["batch_id"] = 0
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router_api.post("/evaluate")
async def evaluate_api(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...),
):
    """Delegate to root handler"""
    return await evaluate_root(candidates_file, rubric_file)

# Include routers
app.include_router(router_root)
app.include_router(router_api)

__all__ = ["app"]





