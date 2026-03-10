from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn
from ml_engine import process_evaluation_request

app = FastAPI(title="ML Evaluator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route now handled by StaticFiles at the bottom

@app.post("/evaluate")
async def evaluate_candidates(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...)
):
    try:
        candidates_bytes = await candidates_file.read()
        rubric_bytes = await rubric_file.read()
        
        result = process_evaluation_request(
            candidates_bytes, 
            rubric_bytes, 
            candidates_file.filename
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve React App (only if dist exists — on Railway, frontend is separate)
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

@app.exception_handler(404)
async def catch_all(request, exc):
    frontend_index = "../frontend/dist/index.html"
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": "Frontend not built yet"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
