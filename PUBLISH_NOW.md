# 🚀 Publishing vietnormalizer to PyPI - Step by Step

## ✅ Pre-flight Checklist

- [x] Package name `vietnormalizer` is **available** on PyPI
- [x] Distribution files built successfully
- [x] Twine is installed
- [x] All files updated with correct package name

## Step 1: Create PyPI Account (if needed)

1. Go to: https://pypi.org/account/register/
2. Sign up with your email (nghimestudio@gmail.com)
3. Verify your email address

## Step 2: Create API Token (Recommended)

**Why use API token?** More secure than password, can be revoked easily.

1. Go to: https://pypi.org/manage/account/token/
2. Click **"Add API token"**
3. Fill in:
   - **Token name**: `vietnormalizer` (or any name you like)
   - **Scope**: Choose "Entire account" or "Project: vietnormalizer"
4. Click **"Add token"**
5. **IMPORTANT**: Copy the token immediately (starts with `pypi-`)
   - You won't be able to see it again!

## Step 3: Test on TestPyPI (Recommended First Step)

TestPyPI is a separate test environment. Always test here first!

```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: `pypi-xxxxxxxxxxxxx` (your API token)

### Test the installation:

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ vietnormalizer

# Test it works
python3 -c "from vietnormalizer import VietnameseNormalizer; print('✅ Success!')"
```

## Step 4: Publish to Production PyPI

Once tested on TestPyPI, publish to the real PyPI:

```bash
# Upload to PyPI
python3 -m twine upload dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: `pypi-xxxxxxxxxxxxx` (your API token)

## Step 5: Verify Publication

1. Visit: https://pypi.org/project/vietnormalizer/
2. Your package should be live!

3. Test installation:
```bash
pip install vietnormalizer
python3 -c "from vietnormalizer import VietnameseNormalizer; n = VietnameseNormalizer(); print(n.normalize('Hôm nay là 25/12/2023'))"
```

## 🎉 Success!

Your package is now available worldwide! Users can install it with:
```bash
pip install vietnormalizer
```

## Alternative: Use the Interactive Script

I've created `publish.sh` script that guides you through the process:

```bash
./publish.sh
```

It will:
- Check if distribution files exist
- Ask if you want TestPyPI or PyPI
- Upload the package
- Show you the installation commands

## Troubleshooting

### "HTTPError: 400 Bad Request"
- Package name might be taken (but we checked - it's available)
- Version number already exists - increment version in `pyproject.toml` and `setup.py`

### "HTTPError: 403 Forbidden"
- Wrong username/password
- API token expired or incorrect
- Make sure username is exactly `__token__` (with underscores)

### "File already exists"
- This version (0.1.0) was already uploaded
- Increment version number and rebuild:
  ```bash
  # Update version in pyproject.toml (line 7) and setup.py (line 14)
  # Then rebuild:
  rm -rf build dist *.egg-info
  python3 -m build
  python3 -m twine upload dist/*
  ```

## Next Steps After Publishing

1. **Update README** with PyPI badge (optional):
   ```markdown
   [![PyPI version](https://badge.fury.io/py/vietnormalizer.svg)](https://badge.fury.io/py/vietnormalizer)
   ```

2. **Create GitHub repository** (if you haven't):
   - Update URLs in `pyproject.toml` if needed

3. **Announce your package**:
   - Share on social media
   - Add to awesome-python lists
   - Write a blog post

## Updating the Package

To publish a new version:

1. Update version in:
   - `pyproject.toml` (line 7)
   - `setup.py` (line 14)
   - `vietnormalizer/__init__.py` (line 21)

2. Rebuild and upload:
   ```bash
   rm -rf build dist *.egg-info
   python3 -m build
   python3 -m twine upload dist/*
   ```

---

**Ready to publish?** Run:
```bash
./publish.sh
```

Or manually:
```bash
python3 -m twine upload --repository testpypi dist/*  # Test first
python3 -m twine upload dist/*  # Then production
```

