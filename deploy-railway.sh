#!/bin/bash
# Railway Deployment Script for ML Evaluator Backend

set -e

echo "🚀 ML Evaluator - Railway Backend Deployment"
echo "============================================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Step 1: Login
echo "Step 1: Logging into Railway..."
echo "Please follow the browser login prompt"
railway login

echo ""
echo "Step 2: Initializing Railway project..."
# This will create a new project and link it
railway init --name "ml-evaluator-backend"

echo ""
echo "Step 3: Deploying to Railway..."
echo "This will take 5-15 minutes on first run (models download)"
railway up

echo ""
echo "Step 4: Getting deployed URL..."
RAILWAY_URL=$(railway environment | grep "RAILWAY_STATIC_URL" | cut -d'=' -f2 | tr -d ' ')

if [ -z "$RAILWAY_URL" ]; then
    echo "⚠️  Could not auto-detect URL. Getting service URL..."
    railway open
    echo ""
    echo "Copy your Railway URL from the browser"
    read -p "Enter your Railway backend URL (e.g., https://xxx.railway.app): " RAILWAY_URL
fi

echo ""
echo "✅ Backend deployed to: $RAILWAY_URL"
echo ""
echo "Step 5: Next steps:"
echo "1. Go to Vercel dashboard: https://vercel.com"
echo "2. Select 'ml-evaluator' project"
echo "3. Settings → Environment Variables"
echo "4. Add new variable:"
echo "   Name: VITE_API_URL"
echo "   Value: $RAILWAY_URL"
echo "5. Redeploy Vercel project"
echo ""
echo "Then test:"
echo "  curl $RAILWAY_URL/health"
echo "  curl -X POST $RAILWAY_URL/evaluate -F 'candidates_file=@ml-evaluator/candidates.csv' -F 'rubric_file=@ml-evaluator/rubric.txt'"
