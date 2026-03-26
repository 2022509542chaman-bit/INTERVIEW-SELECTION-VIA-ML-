# ML Evaluator Vercel Deployment

## Frontend Environment Variables

Add these to Vercel project settings under Environment Variables:

```
VITE_API_URL=https://your-vercel-project.vercel.app/api
```

Or leave it empty to use relative URLs (recommended for same-origin deployment).

## Backend Environment Variables (if using separate backend)

```
DATABASE_URL=postgresql://user:password@host/db
PYTHONUNBUFFERED=1
```

## Deployment Steps

### Option 1: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel --prod
```

### Option 2: Deploy via Git (GitHub/GitLab)

1. Push code to GitHub
2. Go to vercel.com
3. Create new project
4. Select your repository
5. Configure environment variables
6. Click Deploy

### Configuration

The vercel.json is already configured to:
- Build frontend with `npm run build`
- Serve from `ml-evaluator/frontend/dist`
- Handle API rewrites to `/api/index.py`
- Use Python 3.11 runtime for backend functions
- Memory: 3GB, Timeout: 60s

## Local Testing

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally with Vercel environment
vercel dev

# This will run on http://localhost:3000
```

## Notes

- Machine learning models (all-MiniLM-L6-v2, ms-marco-MiniLM-L-6-v2) are downloaded on first run (~500MB)
- Vercel free tier may timeout on first evaluation (models download)
- Consider using Vercel Pro ($20/month) for production with increased timeout
- Or pre-download models and bundle them (requires Docker or custom build)

## Troubleshooting

### Build fails: "Module not found"
- Check `requirements.txt` includes all dependencies
- Verify path aliases in vite.config.ts match actual structure

### Timeout errors on first run
- This is normal - Vercel is downloading ML models
- Subsequent requests will be faster
- Consider upgrading to Pro tier (extended timeout)

### Environment variable not loading
- Ensure variables are set in Vercel project settings
- Rebuild after adding variables (git push or manual redeploy)
