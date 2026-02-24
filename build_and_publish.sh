#!/bin/bash
# Build and publish script for vietnamese-normalizer

set -e

echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

echo "📦 Building package..."
python3 -m build

echo "✅ Build complete! Files created in dist/:"
ls -lh dist/

echo ""
echo "📤 To publish to PyPI, run:"
echo "   python3 -m twine upload dist/*"
echo ""
echo "🧪 To test on TestPyPI first, run:"
echo "   python3 -m twine upload --repository testpypi dist/*"
echo ""

