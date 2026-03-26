"""Absolute minimal test endpoint"""
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/test")
def test():
    return {"message": "ok"}

@app.post("/evaluate")
async def evaluate(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...),
):
    """Test evaluate endpoint"""
    return {
        "status": "ok",
        "data": [],
        "summary": {"total": 0, "hired": 0, "borderline": 0, "rejected": 0},
        "eval_time_seconds": 0,
        "batch_id": 0,
    }
