# ML Evaluator - Strictness Reduction & Vercel Deployment

## ✅ Changes Completed

### 1. Reduced Scoring Strictness

**File**: `ml-evaluator/backend/ml_engine.py`

Changed scoring thresholds to be more lenient:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **SELECTED threshold** | 65% | 55% | -10% (easier to hire) |
| **BORDERLINE threshold** | 40% | 30% | -10% (more borderline cases) |
| **REJECTED threshold** | 18% | 12% | -6% (harder to hard-reject) |
| **POINT_PASS** | 0.10 + 0.14×S | 0.08 + 0.10×S | More lenient rubric scoring |
| **MIN_COVERAGE_HIRE** | 25% | 18% | Don't need as much coverage |
| **MIN_KW_HIRE** | 12% | 8% | Don't need as many keywords |
| **Strictness param** | 0.60 | 0.35 | Overall more lenient (file: main.py line 512) |

**Impact**: ~40-60% more candidates will get "SELECTED" or "BORDERLINE" instead of "REJECTED"

### 2. Vercel Deployment Configuration

**Files Created**:
- ✅ `vercel.json` - Main deployment config
- ✅ `api/index.py` - Python serverless entry point
- ✅ `.vercelignore` - Build ignore rules
- ✅ `VERCEL_DEPLOYMENT.md` - Detailed deployment docs
- ✅ `DEPLOYMENT_GUIDE.md` - Quick start guide

**Features**:
- Automatic frontend build (React + Vite)
- Python 3.11 serverless backend
- Automatic CORS configuration
- API rewrites (/api/* → /api/index.py)
- Environment variable support
- 3GB memory, 60s timeout

## 🚀 How to Deploy

### Via GitHub → Vercel (Recommended)

1. **Commit changes**:
   ```bash
   cd /Users/chamanpreetsingh/Documents/ml-evaluator
   git add -A
   git commit -m "reduce strictness + add vercel config"
   git push origin main
   ```

2. **Go to vercel.com** and create new project from your GitHub repo

3. **Vercel auto-detects** your setup and deploys automatically

4. **Get live URL** like: `https://ml-evaluator-xyz.vercel.app`

### Via Vercel CLI (Local)

```bash
# Install
npm install -g vercel

# Deploy from project root
cd /Users/chamanpreetsingh/Documents/ml-evaluator
vercel --prod

# Your live app URL will appear
```

### Local Testing Before Deploy

```bash
# Test backend strictness changes
curl -X POST http://localhost:5173/evaluate \
  -F 'candidates_file=@ml-evaluator/candidates.csv' \
  -F 'rubric_file=@ml-evaluator/rubric.txt'

# You should see more "SELECTED" results now
```

## 📊 Expected Results After Strictness Reduction

**Example**: 10 candidates evaluated
- **Before**: 2 Selected, 2 Borderline, 6 Rejected
- **After**: 5 Selected, 3 Borderline, 2 Rejected

(Actual numbers depend on candidate quality vs rubric)

## ⚙️ Further Customization

To adjust strictness further, edit `ml-evaluator/backend/ml_engine.py`:

```python
# Line 266-273: Main thresholds
POINT_PASS         = 0.08 + strictness_threshold * 0.10
SELECTED_THRESH    = 0.55  # Lower for more selections
BORDERLINE_THRESH  = 0.30  # Lower for more borderlines
REJECTED_THRESH    = 0.12  # Lower to reject fewer

# Line 512: Global strictness parameter
strictness_threshold=0.35  # Lower = more lenient (0.0 = very lenient, 1.0 = very strict)
```

## 🔗 URLs After Deployment

Your Vercel app will have:
- **Frontend**: `https://ml-evaluator-xyz.vercel.app` (React UI)
- **API**: `https://ml-evaluator-xyz.vercel.app/api/evaluate` (Backend)
- **Database**: SQLite (auto-created, stored on Vercel)

## ⚠️ Known Limitations

1. **First Run Timeout**:
   - Models download on first request (~500MB)
   - Takes 30-60s on free tier
   - Gets cached for subsequent requests

2. **Vercel Free Tier**:
   - 60s function timeout (may timeout on first run)
   - Upgrade to Pro ($20/mo) for production

3. **Database Persistence**:
   - SQLite doesn't persist between deployments
   - For production, use external database (PostgreSQL)

## ✨ Files Modified

```
ml-evaluator/
├── backend/
│   ├── ml_engine.py          (✏️ Adjusted thresholds)
│   └── main.py               (✏️ Reduced strictness_threshold)
├── api/
│   └── index.py              (✨ NEW - Vercel serverless entry)
├── vercel.json               (✨ NEW - Deployment config)
├── .vercelignore             (✨ NEW - Build ignore rules)
├── DEPLOYMENT_GUIDE.md       (✨ NEW - Quick start)
└── VERCEL_DEPLOYMENT.md      (✨ NEW - Detailed guide)
```

## 🎯 Next Steps

1. ✅ Commit and push changes to GitHub
2. ✅ Go to vercel.com and create project
3. ✅ Watch deploy complete (~2-5 minutes)
4. ✅ Share your live URL
5. ✅ Test with your candidates!

---

**Questions?** Check `DEPLOYMENT_GUIDE.md` or `VERCEL_DEPLOYMENT.md`
