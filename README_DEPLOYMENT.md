# 🚀 ML Evaluator - Complete Deployment Guide

## ⚡ Quick Start (5 minutes)

### Frontend ✅ (Already Live!)
```
https://ml-evaluator.vercel.app
```

### Backend ⏳ (Deploy with One Command)

```bash
bash /Users/chamanpreetsingh/Documents/ml-evaluator/deploy-now.sh
```

That's it! The script handles:
1. Railway authentication (opens browser)
2. Backend deployment to Railway
3. Gets backend URL
4. Guides you to set Vercel environment variable
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
