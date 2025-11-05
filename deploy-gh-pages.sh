#!/bin/bash
set -e

echo "📦 Building site..."
python3 build.py

echo "📝 Creating .nojekyll file..."
touch output/.nojekyll

echo "🌿 Creating gh-pages branch..."
cd output
git init
git add -A
git commit -m "Deploy to GitHub Pages

🤖 Generated with Claude Code
"
git branch -M gh-pages

echo "🚀 Pushing to GitHub..."
git remote add origin https://github.com/tranhoangkhuongvn/my-blog.git
git push -f origin gh-pages

echo "✅ Deployed successfully!"
echo "📍 Enable GitHub Pages at: https://github.com/tranhoangkhuongvn/my-blog/settings/pages"
