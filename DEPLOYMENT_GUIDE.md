# Quick Start: Deploying to Vercel

## Changes Made

### 1. **Reduced Scoring Strictness** ✅
The scoring thresholds have been made more lenient:
- **SELECTED threshold**: 65% → 55%
- **BORDERLINE threshold**: 40% → 30%
- **REJECTED threshold**: 18% → 12%
- **Strictness parameter**: 0.60 → 0.35

This means more candidates will be marked as "SELECTED" and fewer will be hard rejected.

### 2. **Vercel Configuration Files** ✅
Created deployment configuration:
- `vercel.json` - Main deployment config
- `api/index.py` - Serverless function entry point
- `.vercelignore` - Files to ignore during build
- `VERCEL_DEPLOYMENT.md` - Detailed deployment guide

## Deploy to Vercel in 3 Steps

### Step 1: Prepare Your Code
```bash
cd /Users/chamanpreetsingh/Documents/ml-evaluator
git add -A
git commit -m "feat: reduce scoring strictness + add Vercel deployment config"
git push origin main
```

### Step 2: Connect to Vercel
Go to [vercel.com](https://vercel.com) and:
1. Click "New Project"
2. Import your GitHub repository
3. Select project root (ml-evaluator folder)
4. Click "Deploy"

**That's it!** Vercel will automatically:
- Build your React frontend
- Set up Python backend functions
- Configure CORS and API rewrites
- Deploy everything

### Step 3: Get Your URL
After deployment completes, you'll get a URL like:
```
https://ml-evaluator-xyz.vercel.app
```

Your app is now live! 🚀

## Environment Variables (Optional)

If you want to use a custom API URL, add to Vercel project settings:
```
VITE_API_URL=https://ml-evaluator-xyz.vercel.app/api
```

But it's not necessary - the app uses relative URLs by default.

## Performance Notes

- **First evaluation**: May take 30-60s (downloading ML models ~500MB)
- **Subsequent evaluations**: 5-10s (models cached)
- **Free tier**: Limited to 60s timeout
- **Pro tier**: Recommended for production ($20/month)

## Scoring Changes Summary

**Before (Strict)**:
- Only top-tier candidates → "SELECTED"
- Most candidates → "REJECTED"

**After (Lenient)**:
- Good candidates → "SELECTED"
- Decent candidates → "BORDERLINE"
- Minimal rejection

Adjust thresholds in `ml-evaluator/backend/ml_engine.py` lines 266-273 if needed.
