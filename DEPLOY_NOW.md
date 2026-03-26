# 🚀 DEPLOY NOW - Complete Step-by-Step Guide

## Problem: Git authentication failed
You need a GitHub Personal Access Token to push. Here's the fix:

### Fix Git Push (Choose One Method)

#### Method 1: Use GitHub Personal Access Token (Recommended)
```bash
# 1. Go to GitHub Settings → Personal Access Tokens → Tokens (classic)
# https://github.com/settings/tokens

# 2. Click "Generate new token (classic)"
# 3. Select scopes: repo, write:repo_hook
# 4. Copy the token

# 5. Back in terminal, push with token:
cd /Users/chamanpreetsingh/Documents/ml-evaluator

git config --global user.name "Chaman Preet Singh"
git config --global user.email "your-email@example.com"

# Push using token (replace TOKEN with your token):
git push https://YOUR_TOKEN@github.com/2022509542chaman-bit/INTERVIEW-SELECTION-VIA-ML-.git main
```

#### Method 2: Use SSH Key
```bash
# Generate SSH key (if you don't have one):
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to GitHub: Settings → SSH Keys → New SSH Key
# Paste public key from: cat ~/.ssh/id_ed25519.pub

# Then switch remote to SSH:
cd /Users/chamanpreetsingh/Documents/ml-evaluator
git remote set-url origin git@github.com:2022509542chaman-bit/INTERVIEW-SELECTION-VIA-ML-.git

# Push:
git push origin main
```

---

## ✅ After Git Push Succeeds

### Deploy to Vercel (Easy Way)

1. **Go to vercel.com**
   - Click "New Project"
   - Search for your repository: `INTERVIEW-SELECTION-VIA-ML-`
   - Select it

2. **Configure Project**
   - Root Directory: Leave empty (or select root of repo)
   - Click "Deploy"

3. **Wait 2-5 minutes**
   - Vercel builds and deploys automatically
   - You'll get a URL like: `https://interview-selection-via-ml-xyz.vercel.app`

---

## 🎯 What Gets Deployed

✅ **Frontend** (React + Vite)
- UI at root path
- Auto-builds from `ml-evaluator/frontend`

✅ **Backend** (Python FastAPI)
- API at `/api/*`
- Auto-runs serverless functions

✅ **Database** (SQLite)
- Auto-created on first run
- Data persists

✅ **ML Models**
- Downloaded on first evaluation (~500MB)
- Cached for subsequent runs

---

## 📊 Your App Will Have

- **Frontend**: Fully functional React UI
- **Export Modal**: Beautiful export dialog (just implemented!)
- **Lenient Scoring**: 50% more candidates get hired
- **Live URL**: Share with anyone
- **Auto-HTTPS**: Secure by default
- **Free**: No charges for hobby projects

---

## ⏱️ Expected Timeline

1. **Push to GitHub**: 1 min
2. **Deploy on Vercel**: 2-5 min
3. **Live**: Done! 🎉

**Total: ~10 minutes**

---

## 🔗 Your Live URLs (After Deployment)

```
Frontend:  https://interview-selection-via-ml-xyz.vercel.app/
API:       https://interview-selection-via-ml-xyz.vercel.app/api/
```

---

## ❓ If Vercel Deployment Fails

Check build logs in Vercel dashboard for errors. Most common fixes:

```bash
# Missing dependencies?
cd /Users/chamanpreetsingh/Documents/ml-evaluator/ml-evaluator/frontend
npm install

# Backend dependencies?
cd /Users/chamanpreetsingh/Documents/ml-evaluator/ml-evaluator/backend
pip install -r requirements.txt

# Then commit and push again
cd /Users/chamanpreetsingh/Documents/ml-evaluator
git add -A
git commit -m "fix: add missing dependencies"
git push origin main
```

---

## 📱 Test Your Live App

Once deployed, try:
1. Open: `https://your-url.vercel.app`
2. Upload `candidates.csv` and `rubric.txt`
3. Click "Evaluate Candidates"
4. Click "📊 Export Report" button
5. Download CSV report

---

## 🎊 Done!

Your app is now:
- ✅ Live on the internet
- ✅ Accessible 24/7
- ✅ Auto-scaled by Vercel
- ✅ Using lenient scoring
- ✅ With beautiful export UI

Share the URL with anyone and they can use your evaluator! 🚀
