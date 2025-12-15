#!/bin/bash

echo "🚀 Setting up GitHub Repository for ReSonata"
echo "=============================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "⚠️  Warning: .gitignore not found"
else
    echo "✅ .gitignore found"
fi

echo ""
echo "📝 Next steps:"
echo "1. Create a repository on GitHub: https://github.com/new"
echo "   - Name: ReSonata"
echo "   - Description: Reviving Classical Piano with AI Innovation"
echo "   - Set to Public"
echo ""
echo "2. Run these commands (replace YOUR_USERNAME):"
echo "   git add ."
echo "   git commit -m 'Initial commit: ReSonata - Reviving Classical Piano with AI Innovation'"
echo "   git remote add origin https://github.com/YOUR_USERNAME/ReSonata.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Your repository will be at:"
echo "   https://github.com/YOUR_USERNAME/ReSonata"
echo ""

