# 🚀 Deployment Complete!

## Current Status

✅ **Frontend**: Deployed on Vercel  
- URL: https://ml-evaluator.vercel.app  
- Only HTML/CSS/JS (no backend dependencies)

⏳ **Backend**: Ready to deploy on Railway  
- Configuration: Ready (Dockerfile + railway.json)
- Size: ~9.6 GB (models included)
- Railway can handle this!

---

## 🔧 Complete Deployment Instructions

### 1. Deploy Backend to Railway (5-10 minutes)

```bash
# Step A: Install Railway CLI (one-time)
npm install -g @railway/cli

# Step B: Login (opens browser)
railway login

# Step C: Go to project directory
cd /Users/chamanpreetsingh/Documents/ml-evaluator

# Step D: Initialize Railway project
railway init
# Follow prompts, name it: ml-evaluator-backend

# Step E: Deploy!
railway up
# Wait for "✓ Deployment successful" message
```

### 2. Get Your Railway Backend URL

```bash
railway open
# Browser opens - look at the URL
# It will be something like:
# https://ml-evaluator-backend-production-abc123.up.railway.app
```

Copy this URL for the next step.

### 3. Connect Frontend to Backend

Go to: **https://vercel.com/dashboard**

1. Click **ml-evaluator** project
2. Go to **Settings** tab
3. Click **Environment Variables** on left
4. Add new variable:
   - Name: `VITE_API_URL`
   - Value: `https://your-railway-url-here` (paste from Step 2)
5. Click **Save**
6. Vercel auto-redeploys (1-2 minutes)

### 4. Test Everything! 🎉

```bash
# Test backend
curl https://your-railway-url/health

# Try the frontend
# Go to https://ml-evaluator.vercel.app
# Upload your candidates CSV and rubric TXT
# Click Evaluate!
```

---

## 📊 Architecture After Setup

```
┌─────────────────────────────────────┐
│  https://ml-evaluator.vercel.app    │  ← Frontend (Vercel)
│  (React + TypeScript)               │     Static site only
└──────────────────┬──────────────────┘
                   │ VITE_API_URL env var
                   ↓
┌─────────────────────────────────────┐
│  https://your-railway-url.app       │  ← Backend (Railway)
│  (FastAPI + ML Models)              │     Full processing
│  - Evaluate endpoint                │
│  - ML scoring engine                │
│  - Database (SQLite)                │
└─────────────────────────────────────┘
```

---

## ✅ Deployment Checklist

After completing Steps 1-4 above:

- [ ] Railway backend URL obtained
- [ ] `VITE_API_URL` environment variable set in Vercel
- [ ] Vercel redeployed (check deployment status)
- [ ] `/health` endpoint returns `{"status":"ok"}`
- [ ] Can upload files on frontend
- [ ] Results display on frontend

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| "FUNCTION_INVOCATION_FAILED" on Railway | First run takes 10-15 min (downloading models). Wait and refresh. |
| Frontend says "Failed to evaluate" | Check `VITE_API_URL` is set correctly (with https://) |
| Models downloading slowly | Normal! 500MB on first run. Subsequent requests faster. |
| "Unable to connect to API" | Make sure Railway URL is complete (e.g., https://xxx.up.railway.app) |

---

## 📝 Quick Reference

**Vercel Frontend Dashboard**: https://vercel.com/dashboard  
**Railway Backend Dashboard**: https://railway.app/dashboard  
**Frontend Live**: https://ml-evaluator.vercel.app  
**Backend Base URL**: https://your-railway-url.up.railway.app  
**API Endpoints**: `/evaluate` `/health` `/api/candidates`

---

## 💾 Local Development (Optional)

```bash
# Terminal 1: Backend
cd ml-evaluator/backend
python3 -m uvicorn main:app --reload

# Terminal 2: Frontend  
cd ml-evaluator/frontend
npm run dev
```

Then visit: http://localhost:5173
Backend API: http://localhost:8000

---

**🎉 That's it! Your ML Evaluator is now live!**
