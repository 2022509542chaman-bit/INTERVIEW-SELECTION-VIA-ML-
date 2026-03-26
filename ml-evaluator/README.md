# ML Evaluator Platform

An automated candidate evaluation platform that scores written interview responses against a structured skill rubric using machine learning.

## Features

✅ **Automated ML Scoring** - Evaluate candidates using sentence-transformers and cross-encoders  
✅ **Persistent Storage** - SQLite/PostgreSQL database for candidate results  
✅ **Rich Breakdown** - Per-criterion scoring and detailed analysis  
✅ **Admin Dashboard** - View stats, charts, and manage candidates  
✅ **CSV Export** - Download evaluation results  
✅ **Responsive UI** - Beautiful React + Tailwind interface  

## Decision Thresholds (PRD Spec)

| Score Range | Decision | Color |
|---|---|---|
| 0% – 17% | HARD_REJECTED | Dark Red |
| 18% – 39% | REJECTED | Red |
| 40% – 64% | BORDERLINE | Yellow |
| 65% – 100% | SELECTED | Green |

## Tech Stack

**Frontend:**
- React 19 + Vite
- React Router DOM v6
- Tailwind CSS
- Recharts for data visualization
- Lucide React icons

**Backend:**
- Python FastAPI
- SQLAlchemy ORM (models.py)
- scikit-learn + sentence-transformers
- SQLite (dev) → PostgreSQL (prod)

**Infrastructure:**
- Docker multi-stage build
- Railway deployment

## Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- pip

### Backend Setup

```bash
cd ml-evaluator/backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server (with reload)
python main.py
```

Server runs on `http://localhost:8000`

### Frontend Setup

```bash
cd ml-evaluator

# Install dependencies
npm install

# Run dev server with API proxy
npm run dev
```

Frontend runs on `http://localhost:5173`  
Backend API proxied at `localhost:5173/api` and `localhost:5173/evaluate`

## API Endpoints

### Evaluation

**POST** `/evaluate` or `/api/evaluate`
- Submit candidates CSV and rubric for batch evaluation
- Returns: `{status, data: [{id, name, score, decision, breakdown, ...}], summary, eval_time_seconds}`

### Candidates

**GET** `/api/candidates?limit=100&decision=SELECTED&rubric_hash=...`
- List all candidates with optional filtering

**GET** `/api/candidates/{id}`
- Get detailed candidate

**DELETE** `/api/candidates/{id}` 
- Delete candidate

**DELETE** `/api/candidates`
- Delete all

### Dashboard

**GET** `/api/stats?rubric_hash=...`
- Stats: total, hired, borderline, rejected, avg_score, min/max_score, score_distribution

**GET** `/api/export/csv`
- Download CSV of all candidates

### Rubric Management

**POST** `/api/rubrics` - Create rubric  
**GET** `/api/rubrics` - List all  
**GET** `/api/rubrics/{id}` - Get one  
**PUT** `/api/rubrics/{id}` - Update

## Database Models

### Candidate
```python
id, name, total_score, decision, confidence, grade, star_rating,
rank, percentile, coverage, keyword_match_rate, breakdown,
point_scores, matched_keywords, missing_keywords,
strengths, weaknesses, recommendation, borderline_analysis,
created_at, rubric_hash
```

### Rubric
```python
id, name, content, role, description, criteria_count, 
is_active, created_at, updated_at
```

### EvaluationBatch
```python
id, name, rubric_hash, total_candidates, 
hired_count, borderline_count, rejected_count, 
eval_time_seconds, created_at
```

## Development

### File Structure

```
ml-evaluator/
├── backend/
│   ├── main.py           # FastAPI app
│   ├── models.py         # SQLAlchemy ORM
│   ├── ml_engine.py      # ML scoring
│   ├── requirements.txt
│   └── ...
├── src/
│   ├── App.tsx           # Router
│   ├── components/
│   │   ├── EvaluationForm.tsx
│   │   ├── ScoreCard.tsx
│   │   └── Dashboard.tsx
│   └── ...
├── package.json
├── vite.config.js
└── README.md
```

### Key Implementation Details

- **ML Pipeline**: sentence-transformers (bi-encoder) → cross-encoder → keyword overlap → final score
- **Decision Logic**: Applies PRD thresholds strictly (65%, 40%, 18%)
- **Lazy Loading**: ML models only load on first evaluation
- **Database Init**: Tables auto-created via `init_db()` in models.py
- **Frontend Proxy**: Vite proxies `/api/*` and `/evaluate` to backend

### Performance

- Bi-encoder warm-up: ~2s
- Cross-encoder warm-up: ~3s  
- Per-candidate eval: ~200-300ms
- Batch of 20: ~6-8s total

## Deployment (Railway)

1. Push code to GitHub
2. Connect repo to Railway  
3. Add `DATABASE_URL` env var (auto for PostgreSQL addon)
4. Backend auto-serves frontend from `/dist`

## Next Steps (Optional)

- Add rubric editor UI modal in dashboard
- Implement role-based access control
- Add comparison view (side-by-side candidates)
- Implement interview feedback templates
- Add candidate import/bulk operations
- Webhooks for hiring system integration

## License

MIT
