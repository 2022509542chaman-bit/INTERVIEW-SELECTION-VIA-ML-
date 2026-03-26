#!/bin/bash
# Quick Railway + Vercel Integration Script
# This automates the entire deployment process

set -e

echo "🚀 ML Evaluator - Complete Deployment Setup"
echo "==========================================="
echo ""

WORK_DIR="/Users/chamanpreetsingh/Documents/ml-evaluator"
cd "$WORK_DIR"

# Function to wait for backend to be ready
wait_for_backend() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for backend to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url/health" > /dev/null 2>&1; then
            echo "✅ Backend is ready!"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts - waiting..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ Backend did not respond. It might still be initializing."
    echo "   First deployment takes 10-15 minutes while models download."
    return 1
}

echo "STEP 1: Ensure Railway is configured"
echo "===================================="
echo ""

if [ ! -d ".railway" ]; then
    echo "Checking Railway authentication..."
    if ! railway whoami > /dev/null 2>&1; then
        echo ""
        echo "⚠️  AUTHENTICATION REQUIRED"
        echo ""
        echo "Railway login requires browser interaction:"
        echo ""
        echo "1. Run this command in your terminal:"
        echo "   railway login"
        echo ""
        echo "2. Follow the browser prompt to sign in with GitHub"
        echo ""
        echo "3. Return here and this script will continue"
        echo ""
        read -p "Press ENTER after you've logged in to Railway..."
    fi
    
    echo ""
    echo "Initializing Railway project..."
    railway init --name "ml-evaluator-backend" 2>&1 | grep -v "^$"
fi

echo ""
echo "STEP 2: Deploy Backend"
echo "===================="
echo ""
echo "Deploying ML Evaluator backend to Railway..."
echo "This may take 5-15 minutes on first run (downloading ML models)"
echo ""

railway up

echo ""
echo "STEP 3: Get Backend URL"
echo "==================="
echo ""

# Try to get URL from Railway
RAILWAY_URL=""
attempts=0
while [ -z "$RAILWAY_URL" ] && [ $attempts -lt 5 ]; do
    echo "Fetching deployment URL... (attempt $((attempts + 1))/5)"
    RAILWAY_URL=$(railway environment 2>&1 | grep -oP 'RAILWAY_STATIC_URL=\K[^ ]+' || true)
    if [ -z "$RAILWAY_URL" ]; then
        sleep 5
        attempts=$((attempts + 1))
    fi
done

# Fallback: Get from service info
if [ -z "$RAILWAY_URL" ]; then
    echo "Getting URL from Railway service info..."
    RAILWAY_URL=$(railway service | grep -oP 'https://[^ ]+' | head -1 || true)
fi

# Last resort: Open Railway dashboard
if [ -z "$RAILWAY_URL" ]; then
    echo ""
    echo "Opening Railway dashboard to get your URL..."
    railway open
    echo ""
    read -p "Enter your Railway backend URL (e.g., https://ml-evaluator-production-xxx.up.railway.app): " RAILWAY_URL
fi

if [ -z "$RAILWAY_URL" ]; then
    echo "❌ Could not determine Railway URL. Please check Railway dashboard."
    exit 1
fi

# Clean up URL
RAILWAY_URL=$(echo "$RAILWAY_URL" | sed 's/\/$//')

echo ""
echo "✅ Backend deployed to: $RAILWAY_URL"
echo ""

echo "STEP 4: Test Backend"
echo "=================="
echo ""

if wait_for_backend "$RAILWAY_URL"; then
    echo "✅ Backend is responding!"
else
    echo "⚠️  Backend may still be initializing. Check:"
    echo "   $RAILWAY_URL/health"
fi

echo ""
echo "STEP 5: Update Vercel Frontend"
echo "============================"
echo ""
echo "You need to add your backend URL to Vercel:"
echo ""
echo "1. Go to: https://vercel.com/dashboard"
echo "2. Click: ml-evaluator project"
echo "3. Go to: Settings → Environment Variables"
echo "4. Click: Add New Variable"
echo ""
echo "   Name:  VITE_API_URL"
echo "   Value: $RAILWAY_URL"
echo ""
echo "5. Click: Save"
echo "6. Wait for Vercel to redeploy (1-2 minutes)"
echo ""

read -p "Press ENTER once you've saved the Vercel environment variable..."

echo ""
echo "STEP 6: Test Complete Setup"
echo "========================="
echo ""

echo "Testing backend health endpoint..."
if curl -s "$RAILWAY_URL/health" | grep -q "status"; then
    echo "✅ Backend health: OK"
else
    echo "⚠️  Could not verify backend health"
fi

echo ""
echo "Opening frontend in browser..."
echo ""

FRONTEND_URL="https://ml-evaluator.vercel.app"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Frontend:  $FRONTEND_URL"
echo "Backend:   $RAILWAY_URL"
echo ""
echo "Next Steps:"
echo "1. Go to: $FRONTEND_URL"
echo "2. Upload your candidates CSV file"
echo "3. Upload your rubric TXT file"
echo "4. Click 'Evaluate'"
echo ""
echo "🎯 Your ML Evaluator is now live!"
echo ""
