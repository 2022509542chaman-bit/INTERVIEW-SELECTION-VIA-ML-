from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
import uvicorn

app = FastAPI(title="ML Evaluator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lazy import: don't load heavy ML models until first request ──
_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        from ml_engine import process_evaluation_request
        _engine = process_evaluation_request
    return _engine


# ── Health / Root ─────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Landing page so the Railway URL isn't blank."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Evaluator API</title>
    <style>
      body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
           font-family:system-ui;background:#0f172a;color:#e2e8f0}
      .card{text-align:center;padding:3rem;border-radius:1rem;
            background:#1e293b;box-shadow:0 4px 30px rgba(0,0,0,.3)}
      h1{font-size:2rem;margin-bottom:.5rem}
      .badge{display:inline-block;padding:.3rem .8rem;border-radius:9999px;
             background:#22c55e;color:#000;font-weight:600;font-size:.85rem;margin:.5rem 0}
      p{color:#94a3b8;max-width:28rem;line-height:1.6}
      a{color:#38bdf8;text-decoration:none}
      code{background:#334155;padding:.15rem .4rem;border-radius:.25rem;font-size:.9rem}
    </style></head><body><div class="card">
      <h1>🤖 ML Evaluator API</h1>
      <span class="badge">● Online</span>
      <p>The backend is running. Use <code>POST /evaluate</code> with
         <code>candidates_file</code> and <code>rubric_file</code>.</p>
      <p><a href="/docs">📄 Interactive API Docs</a></p>
    </div></body></html>
    """)


# ── Evaluate endpoint ────────────────────────────────────────────
@app.post("/evaluate")
async def evaluate_candidates(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...)
):
    try:
        engine = _get_engine()           # lazy-load models on first call
        candidates_bytes = await candidates_file.read()
        rubric_bytes = await rubric_file.read()

        result = engine(
            candidates_bytes,
            rubric_bytes,
            candidates_file.filename
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Serve React frontend if it exists (local dev) ────────────────
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.exception_handler(404)
    async def catch_all(request, exc):
        index = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"detail": "Not found"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
