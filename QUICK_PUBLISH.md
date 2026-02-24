# Quick Publishing Guide

## ✅ Package is Ready!

The package has been built successfully. Distribution files are in `dist/`:
- `vietnormalizer-0.1.0.tar.gz` (source distribution)
- `vietnormalizer-0.1.0-py3-none-any.whl` (wheel)

## Before Publishing

1. **Update your information** in:
   - `setup.py` (lines 18-20)
   - `pyproject.toml` (lines 13-14, 30-32)

2. **Check package name availability**:
   - Visit: https://pypi.org/project/vietnormalizer/
   - If taken, choose a different name and update both config files

3. **Create PyPI account**:
   - Sign up at: https://pypi.org/account/register/

## Publish to PyPI

### Step 1: Install tools
```bash
pip3 install --upgrade build twine
```

### Step 2: Build (already done, but you can rebuild)
```bash
./build_and_publish.sh
# or manually:
rm -rf build dist
python3 -m build
```

### Step 3: Test on TestPyPI (recommended)
```bash
python3 -m twine upload --repository testpypi dist/*
# Then test: pip install --index-url https://test.pypi.org/simple/ vietnormalizer
```

### Step 4: Publish to PyPI
```bash
python3 -m twine upload dist/*
```

You'll be prompted for:
- **Username**: Your PyPI username
- **Password**: Your PyPI password or API token

### Using API Token (Recommended)
1. Go to: https://pypi.org/manage/account/token/
2. Create an API token
3. Use `__token__` as username
4. Use the token (starts with `pypi-`) as password

## After Publishing

Verify installation:
```bash
pip install vietnormalizer
python3 -c "from vietnormalizer import VietnameseNormalizer; print('✅ Success!')"
```

## Updating Versions

To publish a new version:
1. Update version in:
   - `setup.py` (line 14)
   - `pyproject.toml` (line 7)
   - `vietnormalizer/__init__.py` (line 18)
2. Rebuild and upload:
   ```bash
   ./build_and_publish.sh
   python3 -m twine upload dist/*
   ```

## Files Included

✅ All necessary files are included:
- Package code (`vietnormalizer/`)
- CSV dictionaries (`data/`)
- README.md
- LICENSE
- Configuration files

## Need Help?

See `PUBLISHING.md` for detailed instructions and troubleshooting.

