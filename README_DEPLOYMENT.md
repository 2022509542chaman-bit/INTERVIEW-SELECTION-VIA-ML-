# 🚀 ML Evaluator - Complete Deployment Guide

## ⚡ STATUS: Frontend LIVE ✅ | Backend Ready ⏳

### Frontend ✅ (LIVE - Ready Now)
```
https://ml-evaluator.vercel.app
```

### Backend ⏳ (Ready for Render deployment - 6 steps below)

---

## 📋 6 Simple Steps to Complete Deployment

### STEP 1: Add Payment Method (1 minute)
1. Go to: https://dashboard.render.com/billing
2. Click "Add Payment Method"
3. Enter credit card (won't charge for free tier)

### STEP 2: Deploy Backend (2 minutes)
1. Go to: https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub (authorize if needed)
4. Select: `2022509542chaman-bit/INTERVIEW-SELECTION-VIA-ML-`
5. Branch: `main`
6. Deploy → Render auto-detects render.yaml

### STEP 3: Wait for Build (10-15 minutes)
- First deployment downloads ML models (9.6GB)
- Status changes: Building... → Live ✨

### STEP 4: Copy Backend URL (1 minute)
Once Live, you'll see: `https://ml-evaluator-backend-XXXX.onrender.com`
(Save this URL)

### STEP 5: Connect Vercel (2 minutes)
1. Go to: https://vercel.com/dashboard
2. Select: ml-evaluator
3. Settings → Environment Variables
4. Add: `VITE_API_URL` = `https://ml-evaluator-backend-XXXX.onrender.com`
5. Vercel auto-redeploys

### STEP 6: Test (2 minutes)
1. Open: https://ml-evaluator.vercel.app
2. Upload candidates.csv + rubric.txt
3. Click Evaluate
4. See results = ✨ SUCCESS!
5. Tests everything

---

## 📋 What Gets Deployed

### Frontend (Vercel) - Already Done ✅
- React + TypeScript UI
- File upload interface
- Results display
- No backend dependencies (lightweight)

### Backend (Railway) - Using This Script
- FastAPI server with ML models
- Sentence-transformers for evaluations
- SQLite database
- All 500MB+ of ML models
- Production-grade Python environment

---

## 🎯 The Complete Process

### Manual Steps (if script doesn't work)

#### 1. Login to Railway (Browser Required)
```bash
railway login
# Browser opens - sign in with GitHub
```

#### 2. Deploy
```bash
cd /Users/chamanpreetsingh/Documents/ml-evaluator
railway init --name "ml-evaluator-backend"
railway up
# Wait 5-15 minutes for deployment
```

#### 3. Get URL
```bash
railway open
# Note your URL: https://ml-evaluator-xxx.up.railway.app
```

#### 4. Update Vercel
- Go to: https://vercel.com/dashboard
- Select: ml-evaluator project
- Settings → Environment Variables
- Add:
  ```
  Name:  VITE_API_URL
  Value: https://your-railway-url.up.railway.app
  ```
- Save (auto-redeploys)

#### 5. Test
```bash
# Test backend
curl https://your-railway-url/health

# Visit frontend
https://ml-evaluator.vercel.app
# Upload files and evaluate!
```

---

## 📊 Architecture

```
┌──────────────────────────────────┐
│  Vercel (Frontend)               │
│  https://ml-evaluator.vercel.app │
│  ✅ Live Now!                    │
└────────────┬─────────────────────┘
             │
             │ HTTP Requests
             │ (VITE_API_URL env var)
             ↓
┌──────────────────────────────────┐
│  Railway (Backend)               │
│  https://xxx.up.railway.app      │
│  ⏳ Deploy with script           │
│  - FastAPI                       │
│  - ML Models                     │
│  - Database                      │
└──────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Backend Deployment Takes Too Long
**Normal!** First deployment:
- Downloads ML models (~500MB)
- Installs Python dependencies
- Compiles packages
- Takes 10-20 minutes

Subsequent deployments are faster.

### "Failed to evaluate" on Frontend
Check:
1. Is `VITE_API_URL` set in Vercel? (Settings → Environment Variables)
2. Is the URL correct? (starts with `https://`)
3. Is Railway backend running? (`railway logs`)
4. Wait 5 minutes if just deployed

### Backend returns 500 errors
```bash
# Check logs
railway logs

# Restart service
railway down
railway up
```

### Models Downloading Slowly
- This is normal for first request (~30 seconds)
- Subsequent requests are instant
- Models are cached

---

## 📁 Project Structure

```
ml-evaluator/
├── ml-evaluator/
│   ├── frontend/              ← React app (Vercel)
│   │   ├── src/
│   │   ├── package.json
│   │   └── dist/              ← Built output
│   └── backend/               ← FastAPI server (Railway)
│       ├── main.py
│       ├── ml_engine.py       ← ML scoring logic
│       ├── models.py          ← Database models
│       ├── requirements.txt   ← Python dependencies
│       └── ...
├── Dockerfile                 ← Railway builds with this
├── vercel.json               ← Vercel config
├── railway.json              ← Railway config
├── deploy-now.sh             ← 🔥 Main deployment script
└── ...
```

---

## 🎓 How It Works

1. **User Uploads Files** on Frontend
   - Candidates CSV
   - Rubric TXT

2. **Frontend Sends to Backend**
   - Makes HTTP POST to `/evaluate`
   - Includes both files

3. **Backend Processes**
   - Reads CSV candidates
   - Parses rubric criteria
   - Uses ML models to score
   - Returns results

4. **Frontend Displays**
   - Rankings
   - Scores
   - Decisions
   - Export options

---

## 📞 Need Help?

- **Vercel Issues**: https://vercel.com/support
- **Railway Issues**: https://railway.app/status
- **Project Issues**: Check GitHub repo

---

## ✅ Deployment Checklist

- [ ] Run `deploy-now.sh`
- [ ] Authenticate with Railway (GitHub)
- [ ] Wait for backend to deploy (~10 min)
- [ ] Set `VITE_API_URL` in Vercel
- [ ] Test `/health` endpoint
- [ ] Visit frontend and upload files
- [ ] See results! 🎉

---

## 🎯 Success Criteria

✅ Backend deployed to Railway  
✅ Frontend connects to backend  
✅ Can upload CSV and TXT files  
✅ Evaluation completes in <2 minutes  
✅ Results display correctly

---

## 💰 Cost

- **Vercel Frontend**: Free tier includes 50GB bandwidth/month
- **Railway Backend**: $5/month for production usage
  - Free tier available for testing
  - Models cached after first run

---

**🚀 Ready? Run:** `bash /Users/chamanpreetsingh/Documents/ml-evaluator/deploy-now.sh`
