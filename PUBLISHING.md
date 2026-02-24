# Publishing to PyPI

This guide explains how to publish the `vietnormalizer` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (optional, for testing): https://test.pypi.org/account/register/
3. **Build Tools**: Install build tools
   ```bash
   pip install --upgrade build twine
   ```

## Step 1: Update Package Metadata

Before publishing, update the following files with your information:

1. **`setup.py`** and **`pyproject.toml`**:
   - Replace `"Your Name"` with your name
   - Replace `"your.email@example.com"` with your email
   - Update GitHub URLs if you have a repository

2. **Check package name availability**:
   - The package name is `vietnormalizer`
   - Check if it's available at: https://pypi.org/project/vietnormalizer/
   - If taken, choose a different name and update `setup.py` and `pyproject.toml`

## Step 2: Build the Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build source distribution and wheel
python3 -m build
```

This creates:
- `dist/vietnormalizer-0.1.0.tar.gz` (source distribution)
- `dist/vietnormalizer-0.1.0-py3-none-any.whl` (wheel)

## Step 3: Test on TestPyPI (Recommended)

Test your package on TestPyPI first:

```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ vietnormalizer
```

## Step 4: Publish to PyPI

Once tested, publish to the real PyPI:

```bash
# Upload to PyPI
python3 -m twine upload dist/*
```

You'll be prompted for:
- **Username**: Your PyPI username
- **Password**: Your PyPI password (or API token)

### Using API Token (Recommended)

1. Go to https://pypi.org/manage/account/token/
2. Create an API token
3. Use `__token__` as username and the token as password

## Step 5: Verify Installation

After publishing, verify the package can be installed:

```bash
pip install vietnormalizer
python3 -c "from vietnormalizer import VietnameseNormalizer; print('Success!')"
```

## Updating the Package

To publish a new version:

1. **Update version** in:
   - `setup.py` (line 14)
   - `pyproject.toml` (line 7)
   - `vietnormalizer/__init__.py` (line 18)

2. **Build and upload**:
   ```bash
   rm -rf build/ dist/ *.egg-info
   python3 -m build
   python3 -m twine upload dist/*
   ```

## Troubleshooting

### "File already exists" error
- The version number already exists on PyPI
- Increment the version number and try again

### "Invalid package name"
- Package names must be lowercase with hyphens
- No underscores or special characters

### "Missing required files"
- Ensure `MANIFEST.in` includes all necessary files
- Check that `include_package_data=True` in `setup.py`

## Package Name Considerations

The package name `vietnormalizer` might be taken. If so, consider:
- `vietnamese-text-normalizer`
- `vn-normalizer`
- `vietnamese-tts-normalizer`
- `vietnamese-nlp-normalizer`

Update the name in:
- `setup.py` (name parameter)
- `pyproject.toml` (project.name)
- This README

