# 🚀 ML Evaluator - DEPLOYMENT READY

## ✅ Status

| Component | Status | URL |
|-----------|--------|-----|
| **Frontend** | ✅ LIVE | https://ml-evaluator.vercel.app |
| **Backend (Local Dev)** | ✅ RUNNING | http://localhost:8000 |
| **Frontend (Local Dev)** | ✅ RUNNING | http://localhost:5173 |

---

## 🎯 QUICK START - LOCAL (FULLY WORKING)

### Prerequisites
- Python 3.9+
- Node.js 16+

### 1️⃣ Install Dependencies

**Backend:**
```bash
cd ml-evaluator/backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd ml-evaluator/frontend
npm install
```

### 2️⃣ Start Servers

**Terminal 1 - Backend:**
```bash
cd ml-evaluator/backend
python3 start_server.py
# Server starts on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd ml-evaluator/frontend
npm run dev
# App loads on http://localhost:5173
```

### 3️⃣ Test It!

Open browser: **http://localhost:5173**

Upload files:
- `candidates.csv` - Sample in repo root
- `rubric.txt` - Sample in repo root

✅ Rankings & scores display immediately

---

## 🌐 PRODUCTION DEPLOYMENT OPTIONS

### Option 1: Railway (Recommended - $5/month)

1. Go to https://railway.app
2. Connect GitHub repo
3. Railway auto-detects and deploys both frontend + backend

**Environment Variables:**
```
VITE_API_URL=https://your-railway-domain/api
```

### Option 2: Vercel + External Backend

**Frontend:** Already deployed at https://ml-evaluator.vercel.app

**Backend:** Deploy separately on:
- Railway (https://railway.app)
- Render (https://render.com)
- Heroku (https://heroku.com)

Then update frontend `.env`:
```
VITE_API_URL=https://your-backend-domain
```

### Option 3: Docker Deployment

```bash
# Build image
docker build -t ml-evaluator .

# Run
docker run -p 8000:8000 -p 3000:3000 ml-evaluator
```

---

## 📊 API Reference

### Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

### Evaluate Candidates
```bash
curl -X POST http://localhost:8000/evaluate \
  -F "candidates_file=@candidates.csv" \
  -F "rubric_file=@rubric.txt"
```

**Response:**
```json
{
  "data": [
    {
      "id": "...",
      "name": "John Smith",
      "score": 85.3,
      "rank": 1,
      "decision": "Hire",
      "strengths": [...],
      "weaknesses": [...]
    }
  ],
  "summary": {
    "total": 10,
    "hired": 2,
    "borderline": 3,
    "rejected": 5
  }
}
```

---

## 🔧 Environment Setup

### Local Development
No environment variables needed - uses localhost defaults.

### Production
Set `VITE_API_URL` environment variable:
```bash
# .env or deployment config
VITE_API_URL=https://api.your-domain.com
```

---

## 📦 Tech Stack

- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + sentence-transformers (MiniLM v2)
- **Deployment:** Vercel (frontend) / Railway (backend)
- **ML Models:** all-MiniLM-L6-v2 (33MB) + cross-encoder (25MB)

---

## ✨ Features

✅ CSV file upload
✅ Rubric-based evaluation  
✅ AI scoring with embeddings
✅ Borderline candidate analysis
✅ Export to Excel/CSV
✅ Real-time ranking display
✅ Grade assignments (A-F)
✅ Star ratings (1-5)

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check port 8000 is free
lsof -ti:8000 | xargs kill -9

# Try again
python3 start_server.py
```

### Frontend can't reach backend
```bash
# Check backend running:
curl http://localhost:8000/health

# Update frontend config in App.tsx if needed:
const endpoint = 'http://localhost:8000/evaluate';
```

### Models take 10+ seconds first request
✅ Normal! Models lazy-load on first request (~30-40 seconds for full download/cache)

---

## 📝 Notes

- ML models download automatically on first request (~58MB total)
- Files cached in `/tmp/sentence-transformers/` for speed
- All candidate data processed locally - no external API calls
- Rubric matching uses semantic similarity (not just keywords)

---

**🎉 Ready to evaluate! Start with local dev above, then scale to Railway for production.**
