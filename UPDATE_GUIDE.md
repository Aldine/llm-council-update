# Step-by-Step Update Guide

## Current Versions
- ✅ Node.js: v24.4.0
- ✅ Python: 3.13.5
- ✅ uv: 0.8.15

## Target Versions
- 🎯 Node.js: v25.2.0
- 🎯 Python: 3.13.5 (already latest)
- 🎯 uv: 0.8.15+ (check for latest)
- 🎯 Python packages: Latest compatible versions

---

## Step 1: Update Node.js to v25.2.0

### Option A: Using Node Version Manager (nvm-windows) - RECOMMENDED

1. **Install nvm-windows if you don't have it:**
   - Download from: https://github.com/coreybutler/nvm-windows/releases
   - Get `nvm-setup.exe` (latest version)
   - Run installer

2. **Install Node.js 25.2.0:**
   ```powershell
   nvm install 25.2.0
   nvm use 25.2.0
   ```

3. **Verify installation:**
   ```powershell
   node --version
   # Should show: v25.2.0
   ```

### Option B: Direct Download

1. Visit: https://nodejs.org/en/download/
2. Download Node.js v25.2.0 for Windows
3. Run installer (will replace current version)
4. Restart your terminal
5. Verify: `node --version`

---

## Step 2: Update uv Package Manager

```powershell
# Update uv to latest version
pip install --upgrade uv

# OR if that doesn't work, use:
python -m pip install --upgrade uv

# Verify new version
uv --version
```

---

## Step 3: Update Python Packages

### Update pyproject.toml (Optional - for specific versions)

Current dependencies in `pyproject.toml`:
```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.9.0",
]
```

### Sync with latest versions:

```powershell
# Update all packages to latest compatible versions
uv sync --upgrade

# This will update:
# - FastAPI to latest
# - uvicorn to latest
# - httpx to latest
# - pydantic to latest
# - python-dotenv to latest
```

---

## Step 4: Update Frontend Dependencies

```powershell
cd frontend

# Check for outdated packages
npm outdated

# Update all packages to latest versions
npm update

# OR for major version updates:
npm install react@latest react-dom@latest
npm install vite@latest

# Verify updates
npm list --depth=0
```

---

## Step 5: Test Everything

```powershell
# Terminal 1 - Start backend
cd C:\Users\chapm\Downloads\llm-council-master\llm-council-master
uv run python -m backend.main

# Terminal 2 - Start frontend
cd frontend
npm run dev
```

Open http://localhost:5173 (or 5174) and test with a query.

---

## Potential Issues & Solutions

### Issue: Node.js not updating
**Solution:** Uninstall old version first via Windows Settings → Apps, then install new version

### Issue: uv upgrade fails
**Solution:** 
```powershell
# Try with python -m pip
python -m pip install --upgrade uv --force-reinstall
```

### Issue: Package conflicts after update
**Solution:**
```powershell
# Delete virtual environment and reinstall
rm -r .venv
uv sync
```

### Issue: Frontend won't start after update
**Solution:**
```powershell
cd frontend
rm -r node_modules
rm package-lock.json
npm install
```

---

## Check Current Package Versions

### Python packages:
```powershell
uv pip list
```

### Frontend packages:
```powershell
cd frontend
npm list --depth=0
```

---

## After Updates Checklist

- [ ] Node.js shows v25.2.0
- [ ] uv shows latest version
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can create new conversation
- [ ] Can send query and get responses
- [ ] All 3 stages display correctly

---

## Rollback Instructions (If Needed)

### Rollback Node.js:
```powershell
# If using nvm:
nvm use 24.4.0

# Otherwise, reinstall Node 24.4.0 from nodejs.org
```

### Rollback Python packages:
```powershell
# Restore from pyproject.toml
uv sync --reinstall
```

### Rollback frontend:
```powershell
cd frontend
rm -r node_modules
npm ci  # Installs exact versions from package-lock.json
```
