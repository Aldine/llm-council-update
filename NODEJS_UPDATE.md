# Node.js v25.2.0 Update Instructions

## ✅ What We've Updated So Far:

1. ✅ **uv**: 0.8.15 → **0.9.18** (latest!)
2. ✅ **pip**: 25.2 → **25.3** (latest!)
3. ✅ **Python Packages Updated:**
   - FastAPI: 0.121.3 → **0.124.4**
   - Pydantic: 2.12.4 → **2.12.5**
   - anyio: 4.11.0 → **4.12.0**
   - httpx: **0.28.1** (already latest)
   - uvicorn: **0.38.0** (already latest)

4. ✅ **Frontend Packages Updated:**
   - React: 19.2.0 → **19.2.3**
   - React-DOM: 19.2.0 → **19.2.3**
   - Vite: 7.2.4 → **7.3.0**
   - ESLint: 9.39.1 → **9.39.2**
   - + 18 other dependency updates

---

## 🎯 Next: Update Node.js to v25.2.0

You currently have: **Node.js v24.4.0**
Target: **Node.js v25.2.0**

### Method 1: Using NVM for Windows (RECOMMENDED)

This allows you to switch between Node versions easily.

#### Install NVM-Windows:

1. **Download NVM for Windows:**
   - Visit: https://github.com/coreybutler/nvm-windows/releases/latest
   - Download: `nvm-setup.exe`
   - Run the installer

2. **Restart your terminal** (required for nvm commands to work)

3. **Install Node.js 25.2.0:**
   ```powershell
   nvm install 25.2.0
   nvm use 25.2.0
   ```

4. **Verify:**
   ```powershell
   node --version
   # Should show: v25.2.0
   ```

5. **Optional - Set as default:**
   ```powershell
   nvm alias default 25.2.0
   ```

#### Benefits of NVM:
- Keep both v24.4.0 and v25.2.0 installed
- Switch between versions anytime: `nvm use 24.4.0` or `nvm use 25.2.0`
- Easy to test compatibility

---

### Method 2: Direct Installation

If you prefer a direct upgrade:

1. **Download Node.js 25.2.0:**
   - Visit: https://nodejs.org/en/download/
   - Select: **Windows Installer (.msi)** for your system (64-bit)
   - Download and run installer

2. **Restart your terminal**

3. **Verify:**
   ```powershell
   node --version
   # Should show: v25.2.0
   ```

4. **Reinstall frontend dependencies:**
   ```powershell
   cd frontend
   rm -r node_modules
   rm package-lock.json
   npm install
   ```

---

## After Node.js Update: Test Everything

### Test Backend:
```powershell
cd C:\Users\chapm\Downloads\llm-council-master\llm-council-master
uv run python -m backend.main
```

Should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Test Frontend:
```powershell
# In a new terminal
cd frontend
npm run dev
```

Should see:
```
VITE v7.3.0  ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Test Application:
1. Open http://localhost:5173
2. Click "New Conversation"
3. Send a test query
4. Verify all 3 stages work

---

## 📊 Current Status Summary

| Component | Before | After | Status |
|-----------|--------|-------|--------|
| Node.js | v24.4.0 | v24.4.0 | ⏳ Manual update needed |
| Python | 3.13.5 | 3.13.5 | ✅ Already latest |
| uv | 0.8.15 | **0.9.18** | ✅ Updated |
| pip | 25.2 | **25.3** | ✅ Updated |
| FastAPI | 0.121.3 | **0.124.4** | ✅ Updated |
| Pydantic | 2.12.4 | **2.12.5** | ✅ Updated |
| React | 19.2.0 | **19.2.3** | ✅ Updated |
| Vite | 7.2.4 | **7.3.0** | ✅ Updated |

---

## 🔄 If You Need to Rollback

### Rollback to Node.js 24.4.0:
```powershell
# If using nvm:
nvm use 24.4.0

# Otherwise, reinstall from nodejs.org
```

### Rollback Python packages:
```powershell
uv sync --reinstall
```

### Rollback frontend:
```powershell
cd frontend
rm -r node_modules
npm ci
```

---

## 💡 Next Steps

1. **Update Node.js to v25.2.0** using Method 1 or Method 2 above
2. **Reinstall frontend dependencies** if needed
3. **Test the application** thoroughly
4. **Done!** 🎉

All other updates are complete!
