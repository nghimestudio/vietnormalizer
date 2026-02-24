# 🚀 Publishing to GitHub - Step by Step

## ✅ Repository Prepared

Your repository is ready! I've:
- ✅ Initialized git repository
- ✅ Created initial commit
- ✅ Added .gitignore
- ✅ Updated README with GitHub links
- ✅ Added GitHub Actions workflow for PyPI publishing

## Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name**: `vietnormalizer`
   - **Description**: `A Python library for normalizing Vietnamese text for TTS and NLP applications`
   - **Visibility**: Public (or Private if you prefer)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click **"Create repository"**

## Step 2: Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote (replace with your actual username if different)
git remote add origin https://github.com/nghimestudio/vietnormalizer.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 3: Verify

Visit your repository:
- https://github.com/nghimestudio/vietnormalizer

You should see all your files!

## Step 4: Update PyPI URLs (Optional)

If your GitHub repo URL is different, update:
- `pyproject.toml` (lines 29-31)
- `setup.py` (line 20)

## Step 5: Publish to PyPI

Now that your code is on GitHub, you can publish to PyPI:

1. **Get PyPI API token**: https://pypi.org/manage/account/token/
2. **Publish**:
   ```bash
   python3 -m twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your API token

Or use the script:
```bash
./publish.sh
```

## 🎉 Done!

Your package is now:
- ✅ On GitHub: https://github.com/nghimestudio/vietnormalizer
- ⏳ Ready for PyPI: https://pypi.org/project/vietnormalizer/

## Future Updates

To update the repository:

```bash
git add .
git commit -m "Your commit message"
git push
```

## GitHub Actions (Automatic PyPI Publishing)

I've set up a GitHub Actions workflow (`.github/workflows/publish.yml`) that will automatically publish to PyPI when you create a release:

1. Go to your GitHub repo
2. Click "Releases" → "Create a new release"
3. Tag version: `v0.1.0`
4. Release title: `v0.1.0`
5. Click "Publish release"

**Note**: You need to add your PyPI API token as a GitHub secret:
- Go to: Settings → Secrets and variables → Actions
- Click "New repository secret"
- Name: `PYPI_API_TOKEN`
- Value: Your PyPI API token (starts with `pypi-`)

