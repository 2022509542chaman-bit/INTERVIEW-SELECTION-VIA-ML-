# Railway Deployment Guide - ML Evaluator Backend

## ⚡ Quick 5-Minute Setup

### Step 1: Install Railway CLI (one-time)
```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway
```bash
railway login
# Browser will open - sign up or log in with GitHub/email
```

### Step 3: Navigate to Project & Deploy
```bash
cd /Users/chamanpreetsingh/Documents/ml-evaluator

# Initialize Railway project (creates new project)
railway init

# When prompted:
# - Project name: ml-evaluator-backend
# - Select region: US or nearest to you

# Deploy
railway up

# Wait 5-10 minutes for first deployment (models downloading)
```

### Step 4: Get Your Backend URL
```bash
railway open
# Browser opens Railway dashboard
# Look for your service URL (e.g., https://ml-evaluator-backend-production-abc123.up.railway.app)
# Copy this URL
```

### Step 5: Connect Frontend to Backend
Go to https://vercel.com/dashboard

1. Select **ml-evaluator** project
2. Go to **Settings → Environment Variables**
3. Click **Add New**
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-railway-url-from-step-4` (paste your URL here)
4. Click **Save**
5. Vercel will auto-redeploy - wait 1-2 minutes

### Step 6: Test Everything
```bash
# Test backend health
curl https://your-railway-url/health

# Test full evaluation
curl -X POST https://your-railway-url/evaluate \
  -F 'candidates_file=@ml-evaluator/candidates.csv' \
  -F 'rubric_file=@ml-evaluator/rubric.txt'

# Test frontend
# Go to https://ml-evaluator.vercel.app
# Upload your files - should now work!
```

---

## 📋 Alternative: Docker Push Method

If `railway init` doesn't work:

```bash
# Manual project creation
railway link

# Then deploy
railway up
```

---

## ✅ Verification Checklist

- [ ] Railway backend deployed and running
- [ ] Backend URL copied from Railway dashboard
- [ ] `VITE_API_URL` added to Vercel environment variables
- [ ] Vercel project redeployed
- [ ] `/health` endpoint responds with `{"status":"ok"}`
- [ ] Frontend can upload files and see results

---

## 🆘 Troubleshooting

### "FUNCTION_INVOCATION_FAILED" error
- First deployment takes longer (downloading ML models ~500MB)
- Wait 10 minutes and try again
- Check Railway logs: `railway logs`

### Frontend shows "Failed to evaluate candidates"
- Verify `VITE_API_URL` is set in Vercel
- Make sure it includes the full URL (https://...)
- Check Railway logs: `railway logs`
- Test API directly with curl

### Models not downloading
- Railway needs at least 2GB RAM
- Check Railway logs for download progress
- First request will be slow (5-30 seconds)

---

## 📞 Getting Railway URL

After deployment completes:

```bash
# Check status
railway status

# View logs
railway logs

# Get environment info
railway environment
```

The URL will be in the format:
```
https://ml-evaluator-backend-production-xxxxxxxx.up.railway.app
```

