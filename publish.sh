#!/bin/bash
# Script to publish vietnormalizer to PyPI

set -e

echo "🚀 Publishing vietnormalizer to PyPI"
echo ""

# Check if dist files exist
if [ ! -d "dist" ] || [ -z "$(ls -A dist/*.whl dist/*.tar.gz 2>/dev/null)" ]; then
    echo "❌ No distribution files found. Building package..."
    rm -rf build dist *.egg-info
    python3 -m build
    echo ""
fi

echo "📦 Distribution files:"
ls -lh dist/*.whl dist/*.tar.gz 2>/dev/null
echo ""

# Ask user which repository to use
echo "Select publishing option:"
echo "1) TestPyPI (recommended for first-time publishing)"
echo "2) PyPI (production)"
read -p "Enter choice [1 or 2]: " choice

case $choice in
    1)
        REPO="testpypi"
        echo ""
        echo "📤 Uploading to TestPyPI..."
        python3 -m twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Uploaded to TestPyPI!"
        echo ""
        echo "🧪 Test installation with:"
        echo "   pip install --index-url https://test.pypi.org/simple/ vietnormalizer"
        ;;
    2)
        REPO="pypi"
        echo ""
        echo "⚠️  You are about to publish to PRODUCTION PyPI!"
        read -p "Are you sure? [y/N]: " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo ""
            echo "📤 Uploading to PyPI..."
            python3 -m twine upload dist/*
            echo ""
            echo "✅ Published to PyPI!"
            echo ""
            echo "🎉 Your package is now available at:"
            echo "   https://pypi.org/project/vietnormalizer/"
            echo ""
            echo "📥 Install with:"
            echo "   pip install vietnormalizer"
        else
            echo "❌ Publishing cancelled."
            exit 1
        fi
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

