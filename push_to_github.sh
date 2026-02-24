#!/bin/bash
# Script to push vietnormalizer to GitHub

set -e

echo "🚀 Pushing vietnormalizer to GitHub"
echo ""

# Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote 'origin' already exists:"
    git remote get-url origin
    echo ""
    read -p "Do you want to update it? [y/N]: " update
    if [[ $update =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "Using existing remote..."
        git push -u origin main
        exit 0
    fi
fi

# Get GitHub username
read -p "Enter your GitHub username [nghimestudio]: " username
username=${username:-nghimestudio}

# Set remote
echo ""
echo "Setting remote to: https://github.com/${username}/vietnormalizer.git"
git remote add origin https://github.com/${username}/vietnormalizer.git

# Check if main branch exists
if git show-ref --verify --quiet refs/heads/main; then
    echo "✅ Branch 'main' exists"
else
    # Rename current branch to main if needed
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        git branch -M main
    fi
fi

echo ""
echo "📤 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "🌐 Your repository is now at:"
echo "   https://github.com/${username}/vietnormalizer"
echo ""
echo "📋 Next steps:"
echo "   1. Visit your repository on GitHub"
echo "   2. Verify all files are there"
echo "   3. Publish to PyPI: ./publish.sh"
echo ""

