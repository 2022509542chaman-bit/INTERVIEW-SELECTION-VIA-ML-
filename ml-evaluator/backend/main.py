"""FastAPI backend for ML Evaluator with database persistence."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import uvicorn
import hashlib
import json
import csv
import io
from datetime import datetime

from models import Candidate, Rubric, EvaluationBatch, init_db, get_db

app = FastAPI(title="ML Evaluator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize Database ──
init_db()

# ── Lazy import: don't load heavy ML models until first request ──
_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        from ml_engine import process_evaluation_request
        _engine = process_evaluation_request
    return _engine


# ── Pydantic Models for API ──

class CandidateOut(BaseModel):
    """Candidate response schema."""
    id: int
    name: str
    total_score: float
    decision: str
    confidence: float
    grade: str
    star_rating: int
    rank: int
    percentile: float
    coverage: float
    keyword_match_rate: float
    consistency_score: float
    criteria_passed: int
    criteria_total: int
    technical_breadth: int
    technical_depth_score: float
    experience_level: str
    response_depth: float
    matched_keywords: list
    missing_keywords: list
    strengths: list
    weaknesses: list
    recommendation: str
    borderline_analysis: dict = None
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    """Full evaluation response."""
    status: str
    data: list
    summary: dict
    eval_time_seconds: float


# ── Helper Functions ──

def _hash_rubric(rubric_text: str) -> str:
    """Generate SHA256 hash of rubric."""
    return hashlib.sha256(rubric_text.encode()).hexdigest()


def _save_candidates_to_db(db: Session, results: list, rubric_hash: str, batch_name: str = None) -> int:
    """Save evaluation results to database. Returns batch_id."""
    hired = sum(1 for r in results if r['decision'] == 'SELECTED')
    borderline = sum(1 for r in results if r['decision'] == 'BORDERLINE')
    rejected = sum(1 for r in results if r['decision'] == 'REJECTED' or r['decision'] == 'HARD_REJECTED')
    
    batch = EvaluationBatch(
        name=batch_name or f"Batch {datetime.utcnow().isoformat()}",
        rubric_hash=rubric_hash,
        total_candidates=len(results),
        hired_count=hired,
        borderline_count=borderline,
        rejected_count=rejected,
    )
    db.add(batch)
    db.flush()  # Get batch.id
    
    for r in results:
        candidate = Candidate(
            name=r['name'],
            raw_response=r.get('response_snippet', ''),
            total_score=r['score'],
            decision=r['decision'],
            confidence=r.get('confidence', 0),
            grade=r.get('grade', 'F'),
            star_rating=r.get('star_rating', 1),
            rank=r.get('rank', 0),
            percentile=r.get('percentile', 0),
            breakdown=r.get('point_scores', []),
            point_scores=r.get('point_scores', []),
            coverage=r.get('coverage', 0),
            keyword_match_rate=r.get('keyword_match_rate', 0),
            consistency_score=r.get('consistency_score', 0),
            criteria_passed=r.get('criteria_passed', 0),
            criteria_total=r.get('criteria_total', 0),
            technical_breadth=r.get('technical_breadth', 0),
            technical_depth_score=r.get('technical_depth_score', 0),
            experience_level=r.get('experience_level', ''),
            experience_confidence=r.get('experience_confidence', 0),
            must_have_pass_rate=r.get('must_have_pass_rate', 0),
            response_depth=r.get('response_depth', 0),
            matched_keywords=r.get('matched_keywords', []),
            missing_keywords=r.get('missing_keywords', []),
            strengths=r.get('strengths', []),
            weaknesses=r.get('weaknesses', []),
            gaps=r.get('gaps', []),
            reason=r.get('reason', ''),
            recommendation=r.get('recommendation', ''),
            response_snippet=r.get('response_snippet', ''),
            borderline_analysis=r.get('borderline_analysis'),
            rubric_hash=rubric_hash,
        )
        db.add(candidate)
    
    db.commit()
    return batch.id


# ── Health / Root ─────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Landing page."""
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
      <p>The backend is running. Use <code>POST /api/evaluate</code> with
         <code>candidates_file</code> and <code>rubric_file</code>.</p>
      <p><a href="/docs">📄 Interactive API Docs</a></p>
    </div></body></html>
    """)


# ── Evaluate endpoint ────────────────────────────────────────────
@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_candidates(
    candidates_file: UploadFile = File(...),
    rubric_file: UploadFile = File(...),
    batch_name: str = Form(default=None),
    db: Session = Depends(get_db),
):
    """Evaluate candidates and save results to database."""
    try:
        engine = _get_engine()
        candidates_bytes = await candidates_file.read()
        rubric_bytes = await rubric_file.read()
        rubric_text = rubric_bytes.decode('utf-8', errors='ignore')

        result = engine(
            candidates_bytes,
            rubric_bytes,
            candidates_file.filename
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        # Save to database
        rubric_hash = _hash_rubric(rubric_text)
        batch_id = _save_candidates_to_db(
            db, result.get("data", []), rubric_hash, batch_name
        )
        result["batch_id"] = batch_id

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Candidate API endpoints ──────────────────────────────────────

@app.get("/api/candidates", response_model=list[CandidateOut])
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    decision: str = Query(None, description="Filter by decision: SELECTED, BORDERLINE, REJECTED"),
    rubric_hash: str = Query(None, description="Filter by rubric hash"),
    db: Session = Depends(get_db),
):
    """List all candidates with optional filtering."""
    query = db.query(Candidate)
    
    if decision:
        query = query.filter(Candidate.decision == decision)
    
    if rubric_hash:
        query = query.filter(Candidate.rubric_hash == rubric_hash)
    
    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
    return candidates


@app.get("/api/candidates/{candidate_id}", response_model=CandidateOut)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get detailed candidate info."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@app.delete("/api/candidates/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate result."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted"}


@app.delete("/api/candidates")
async def delete_all_candidates(db: Session = Depends(get_db)):
    """Delete all candidate results (use with caution)."""
    db.query(Candidate).delete()
    db.commit()
    return {"message": "All candidates deleted"}


# ── Dashboard stats ─────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats(
    rubric_hash: str = Query(None),
    db: Session = Depends(get_db),
):
    """Get aggregated statistics."""
    query = db.query(Candidate)
    if rubric_hash:
        query = query.filter(Candidate.rubric_hash == rubric_hash)
    
    candidates = query.all()
    
    if not candidates:
        return {
            "total": 0,
            "hired": 0,
            "borderline": 0,
            "rejected": 0,
            "avg_score": 0,
            "score_distribution": {}
        }
    
    scores = [c.total_score for c in candidates]
    
    return {
        "total": len(candidates),
        "hired": sum(1 for c in candidates if c.decision == "SELECTED"),
        "borderline": sum(1 for c in candidates if c.decision == "BORDERLINE"),
        "rejected": sum(1 for c in candidates if c.decision == "REJECTED"),
        "avg_score": round(sum(scores) / len(scores), 2),
        "min_score": round(min(scores), 2),
        "max_score": round(max(scores), 2),
        "score_distribution": {
            "0_17": sum(1 for s in scores if 0 <= s < 18),
            "18_39": sum(1 for s in scores if 18 <= s < 40),
            "40_64": sum(1 for s in scores if 40 <= s < 65),
            "65_100": sum(1 for s in scores if 65 <= s <= 100),
        }
    }


# ── CSV Export ───────────────────────────────────────────────────

@app.get("/api/export/csv")
async def export_csv(
    rubric_hash: str = Query(None),
    db: Session = Depends(get_db),
):
    """Export candidates to CSV."""
    query = db.query(Candidate)
    if rubric_hash:
        query = query.filter(Candidate.rubric_hash == rubric_hash)
    
    candidates = query.order_by(Candidate.rank).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    headers = [
        "Rank", "Name", "Score", "Decision", "Grade", "Stars", "Experience",
        "Coverage %", "Keywords %", "Confidence %", "Recommendation"
    ]
    writer.writerow(headers)
    
    # Data rows
    for c in candidates:
        writer.writerow([
            c.rank,
            c.name,
            round(c.total_score, 2),
            c.decision,
            c.grade,
            c.star_rating,
            c.experience_level,
            round(c.coverage, 1),
            round(c.keyword_match_rate, 1),
            round(c.confidence, 1),
            c.recommendation.split('\n')[0][:50],
        ])
    
    # Return as download
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates.csv"}
    )


# ── Rubric Management ────────────────────────────────────────────

@app.post("/api/rubrics")
async def create_rubric(
    name: str = Form(...),
    content: str = Form(...),
    role: str = Form(default=""),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Create/save a rubric template."""
    from ml_engine import parse_rubric_criteria
    
    criteria = parse_rubric_criteria(content)
    rubric = Rubric(
        name=name,
        content=content,
        role=role,
        description=description,
        criteria_count=len(criteria),
    )
    db.add(rubric)
    db.commit()
    return {"id": rubric.id, "name": rubric.name}


@app.get("/api/rubrics")
async def list_rubrics(db: Session = Depends(get_db)):
    """List all saved rubrics."""
    rubrics = db.query(Rubric).filter(Rubric.is_active == True).all()
    return rubrics


@app.get("/api/rubrics/{rubric_id}")
async def get_rubric(rubric_id: int, db: Session = Depends(get_db)):
    """Get rubric content."""
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return rubric


@app.put("/api/rubrics/{rubric_id}")
async def update_rubric(
    rubric_id: int,
    name: str = Form(default=None),
    content: str = Form(default=None),
    role: str = Form(default=None),
    description: str = Form(default=None),
    db: Session = Depends(get_db),
):
    """Update a rubric."""
    from ml_engine import parse_rubric_criteria
    
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")
    
    if name:
        rubric.name = name
    if content:
        rubric.content = content
        rubric.criteria_count = len(parse_rubric_criteria(content))
    if role:
        rubric.role = role
    if description:
        rubric.description = description
    
    rubric.updated_at = datetime.utcnow()
    db.commit()
    return {"id": rubric.id, "name": rubric.name}


# ── Serve React frontend if it exists ────────────────────────────

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "dist")
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
