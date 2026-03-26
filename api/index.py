#!/usr/bin/env python3
"""Vercel serverless - ultra minimal"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent / "ml-evaluator" / "backend"
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(docs_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        from ml_engine import process_evaluation_request
        _engine = process_evaluation_request
    return _engine

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/evaluate")
async def evaluate(candidates_file: UploadFile = File(...), rubric_file: UploadFile = File(...)):
    try:
        cand = await candidates_file.read()
        rubric = await rubric_file.read()
        if not cand or not rubric:
            raise HTTPException(status_code=400, detail="Files empty")
        result = get_engine()(cand, rubric, candidates_file.filename or "c")
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        result["batch_id"] = 0
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
