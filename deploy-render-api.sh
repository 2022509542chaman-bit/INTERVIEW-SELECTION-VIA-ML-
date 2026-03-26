#!/bin/bash

# This script deploys to Render using their API
# However, it requires a Render API key which you need to generate from dashboard

echo "🚀 Render Backend Deployment"
echo "=========================================="
echo ""
echo "Since Render CLI requires manual workspace setup,"
echo "and their API requires authentication tokens,"
echo "the fastest path is to deploy via the web dashboard."
echo ""
echo "📋 QUICK DEPLOY (1 minute setup):"
echo "1. Go to: https://dashboard.render.com"
echo "2. Click: New + → Web Service"
echo "3. Connect: INTERVIEW-SELECTION-VIA-ML- repo (main branch)"
echo "4. Render auto-detects render.yaml → Deploy"
echo "5. Wait 10-15 min for first build (ML models download)"
echo ""
echo "Once deployed, Render gives you:"
echo "   https://ml-evaluator-backend-XXXX.onrender.com"
echo ""
echo "Then we'll:"
echo "1. Update Vercel VITE_API_URL variable"
echo "2. Test the full integration"
echo "3. Give you the final working links"
echo ""
echo "Opening dashboard..."
open "https://dashboard.render.com"
