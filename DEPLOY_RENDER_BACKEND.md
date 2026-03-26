# Deploy Backend to Render

## Quick Deploy via Web Dashboard

1. **Go to**: https://dashboard.render.com

2. **Create New Service**:
   - Click `New +` → `Web Service`
   - Connect GitHub (select INTERVIEW-SELECTION-VIA-ML-)
   - Select branch: `main`
   - Render will auto-detect `render.yaml`

3. **Configure & Deploy**:
   - Runtime: Docker
   - Build command: (auto-detected)
   - Start command: (auto-detected)
   - Click `Deploy`

4. **Wait 10-15 minutes** (first deployment downloads 9.6GB ML models)

5. **Get Your Backend URL**: 
   - Once deployed, Render shows URL like: `https://ml-evaluator-backend-xxxx.onrender.com`

---

## After Deployment

Once you have your Render URL:

1. Go to: https://vercel.com/dashboard
2. Select project: `ml-evaluator`
3. Settings → Environment Variables
4. Add/Update: `VITE_API_URL` = `https://your-render-url`
5. Redeploy (Vercel auto-redeploys)

---

## Testing

- Frontend: https://ml-evaluator.vercel.app
- Backend Health: `https://your-render-url/health`
- Full Eval: Upload CSV+TXT in frontend, results appear in real-time

