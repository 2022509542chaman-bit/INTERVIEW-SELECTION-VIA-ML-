#!/bin/bash
set -e

echo "🚀 ML Evaluator - Complete Railway + Vercel Deployment"
echo "======================================================"
echo ""

PROJECT_ROOT="/Users/chamanpreetsingh/Documents/ml-evaluator"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}STEP 1: Railway Authentication${NC}"
echo "================================"
echo ""
echo "⚠️  Railway login requires browser interaction."
echo "Please follow these steps manually:"
echo ""
echo "1. Open this command in your terminal:"
echo "   railway login"
echo ""
echo "2. Follow the browser prompt to authenticate with GitHub"
echo ""
echo "3. Once logged in, run this script again OR continue with:"
echo "   railway init"
echo "   railway up"
echo ""
read -p "Have you logged in to Railway? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please run 'railway login' first, then run this script again."
    exit 1
fi

echo ""
echo -e "${BLUE}STEP 2: Initialize Railway Project${NC}"
echo "===================================="

if [ ! -d ".railway" ]; then
    echo "Creating new Railway project..."
    railway init --name "ml-evaluator-backend"
else
    echo "Railway project already linked."
fi

echo ""
echo -e "${BLUE}STEP 3: Deploy Backend to Railway${NC}"
echo "=================================="
echo ""
echo "This will take 5-15 minutes on first run (downloading ML models)..."
echo "Railway will use the Dockerfile in the project root."
echo ""

railway up

echo ""
echo -e "${GREEN}✅ Backend deployed!${NC}"
echo ""

echo -e "${BLUE}STEP 4: Get Backend URL${NC}"
echo "======================="

RAILWAY_URL=$(railway environment | grep -oP 'RAILWAY_STATIC_URL=\K[^ ]+' || true)

if [ -z "$RAILWAY_URL" ]; then
    echo "Getting service URL from Railway..."
    railway open
    echo ""
    read -p "Enter your Railway backend URL (e.g., https://xxx.up.railway.app): " RAILWAY_URL
fi

if [ -z "$RAILWAY_URL" ]; then
    echo "❌ Could not get Railway URL. Please try again."
    exit 1
fi

echo -e "${GREEN}✅ Backend URL: $RAILWAY_URL${NC}"
echo ""

echo -e "${BLUE}STEP 5: Update Vercel with Backend URL${NC}"
echo "======================================"
echo ""
echo "Go to: https://vercel.com/dashboard"
echo ""
echo "1. Click 'ml-evaluator' project"
echo "2. Go to Settings → Environment Variables"
echo "3. Add new variable:"
echo "   Name:  VITE_API_URL"
echo "   Value: $RAILWAY_URL"
echo "4. Click Save"
echo "5. Vercel will auto-redeploy"
echo ""
read -p "Have you set the Vercel environment variable? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Please set VITE_API_URL=$RAILWAY_URL in Vercel before testing."
fi

echo ""
echo -e "${BLUE}STEP 6: Test Everything${NC}"
echo "======================="
echo ""

echo "Testing backend health..."
sleep 2
HEALTH_RESPONSE=$(curl -s "$RAILWAY_URL/health")
echo "Response: $HEALTH_RESPONSE"

if [[ $HEALTH_RESPONSE == *"status"* ]]; then
    echo -e "${GREEN}✅ Backend is working!${NC}"
else
    echo -e "${YELLOW}⚠️  Backend might still be starting up. Wait a few moments and try again.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo ""
echo "Frontend: https://ml-evaluator.vercel.app"
echo "Backend:  $RAILWAY_URL"
echo ""
echo "Next: Upload your CSV/TXT files on the frontend!"
