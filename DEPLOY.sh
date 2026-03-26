#!/bin/bash
# ML Evaluator - Deploy to Vercel (Copy & Paste Commands)

# Step 1: Commit your changes
cd /Users/chamanpreetsingh/Documents/ml-evaluator

echo "📦 Committing changes..."
git add -A
git commit -m "refactor: reduce scoring strictness (55%→55%, 30%→30%) + add Vercel deployment config"
git push origin main

echo "✅ Changes pushed to GitHub"
echo ""
echo "🚀 Next steps:"
echo "1. Go to https://vercel.com"
echo "2. Click 'New Project'"
echo "3. Select your GitHub repository (ml-evaluator)"
echo "4. Click 'Deploy'"
echo ""
echo "⏱️  Wait 2-5 minutes for deployment"
echo ""
echo "✨ Your live app URL will appear in the Vercel dashboard"
echo ""
echo "📝 To test locally first:"
echo "   npm install -g vercel"
echo "   vercel dev"
echo "   (then open http://localhost:3000)"
