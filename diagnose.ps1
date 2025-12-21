# ============================================
# LLM Council - End-to-End Diagnostic Script
# ============================================

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  LLM Council - System Diagnostic Check    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$errors = @()
$warnings = @()

# 1. Check Python Backend
Write-Host "[1/7] Checking Backend (Python/FastAPI)..." -ForegroundColor Yellow

# Check if backend process is running
$backendRunning = netstat -ano | Select-String ":8001"
if ($backendRunning) {
    Write-Host "  ✓ Backend is listening on port 8001" -ForegroundColor Green
    $procId = ($backendRunning[0] -split '\s+')[5]
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    Write-Host "    Process: $($proc.ProcessName) (PID: $procId)" -ForegroundColor Gray
} else {
    $errors += "Backend is NOT running on port 8001"
    Write-Host "  ✗ Backend is NOT running on port 8001" -ForegroundColor Red
}

# Test backend API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Backend API is responsive (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    $errors += "Backend API is not responsive: $_"
    Write-Host "  ✗ Backend API is not responsive" -ForegroundColor Red
}

# Check BFF routes
try {
    $bffRoutes = Invoke-RestMethod -Uri "http://localhost:8001/openapi.json" -ErrorAction Stop
    $bffEndpoints = $bffRoutes.paths.PSObject.Properties.Name | Where-Object { $_ -like "/bff/*" }
    if ($bffEndpoints) {
        Write-Host "  ✓ BFF routes registered: $($bffEndpoints.Count) endpoints" -ForegroundColor Green
        $bffEndpoints | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
    } else {
        $warnings += "No BFF routes found"
        Write-Host "  ! No BFF routes found" -ForegroundColor Yellow
    }
} catch {
    $warnings += "Could not check BFF routes: $_"
}

# 2. Check Frontend (Original - JWT-based)
Write-Host "`n[2/7] Checking Frontend (React/Vite - Port 5173)..." -ForegroundColor Yellow

$frontendRunning = netstat -ano | Select-String ":5173"
if ($frontendRunning) {
    Write-Host "  ✓ Frontend is listening on port 5173" -ForegroundColor Green
} else {
    $warnings += "Original frontend (port 5173) is not running"
    Write-Host "  ! Frontend is NOT running on port 5173" -ForegroundColor Yellow
}

# Check if frontend files exist
if (Test-Path "frontend/src/App.jsx") {
    Write-Host "  ✓ Frontend source files exist" -ForegroundColor Green
} else {
    $errors += "Frontend source files not found"
    Write-Host "  ✗ Frontend source files not found" -ForegroundColor Red
}

# 3. Check BFF Frontend Demo
Write-Host "`n[3/7] Checking BFF Frontend Demo (Port 5174)..." -ForegroundColor Yellow

$bffFrontendRunning = netstat -ano | Select-String ":5174"
if ($bffFrontendRunning) {
    Write-Host "  ✓ BFF Frontend is listening on port 5174" -ForegroundColor Green
} else {
    $warnings += "BFF frontend (port 5174) is not running"
    Write-Host "  ! BFF Frontend is NOT running on port 5174" -ForegroundColor Yellow
}

# Check if BFF frontend files exist
if (Test-Path "frontend-bff/src/App.jsx") {
    Write-Host "  ✓ BFF Frontend source files exist" -ForegroundColor Green
    
    # Check if built
    if (Test-Path "frontend-bff/dist/index.html") {
        Write-Host "  ✓ BFF Frontend is built (dist/ exists)" -ForegroundColor Green
    } else {
        Write-Host "  ! BFF Frontend is not built" -ForegroundColor Yellow
    }
} else {
    $errors += "BFF Frontend source files not found"
    Write-Host "  ✗ BFF Frontend source files not found" -ForegroundColor Red
}

# 4. Check Mobile App
Write-Host "`n[4/7] Checking Mobile App (Expo)..." -ForegroundColor Yellow

if (Test-Path "mobile/package.json") {
    Write-Host "  ✓ Mobile app files exist" -ForegroundColor Green
    
    # Check if node_modules installed
    if (Test-Path "mobile/node_modules") {
        Write-Host "  ✓ Mobile dependencies installed" -ForegroundColor Green
    } else {
        $warnings += "Mobile dependencies not installed"
        Write-Host "  ! Mobile dependencies not installed" -ForegroundColor Yellow
    }
} else {
    $warnings += "Mobile app not found"
    Write-Host "  ! Mobile app not found" -ForegroundColor Yellow
}

# 5. Check Configuration Files
Write-Host "`n[5/7] Checking Configuration..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
    
    # Check for required keys
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENROUTER_API_KEY") {
        Write-Host "  ✓ OPENROUTER_API_KEY is configured" -ForegroundColor Green
    } else {
        $errors += "OPENROUTER_API_KEY not found in .env"
        Write-Host "  ✗ OPENROUTER_API_KEY not configured" -ForegroundColor Red
    }
    
    if ($envContent -match "OAUTH_CLIENT_ID") {
        Write-Host "  ✓ OAuth is configured (OAUTH_CLIENT_ID found)" -ForegroundColor Green
    } else {
        Write-Host "  ! OAuth not configured (optional)" -ForegroundColor Yellow
    }
} else {
    $warnings += ".env file not found"
    Write-Host "  ! .env file not found" -ForegroundColor Yellow
}

# 6. Check for Port Conflicts
Write-Host "`n[6/7] Checking for Port Conflicts..." -ForegroundColor Yellow

$ports = @{
    "8001" = "Backend API"
    "5173" = "Frontend (JWT)"
    "5174" = "Frontend (BFF Demo)"
    "19000" = "Expo Metro Bundler"
    "19001" = "Expo DevTools"
}

foreach ($port in $ports.Keys) {
    $listening = netstat -ano | Select-String ":$port.*LISTENING"
    if ($listening) {
        $procId = ($listening[0] -split '\s+')[5]
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        Write-Host "  Port $port ($($ports[$port])): $($proc.ProcessName) (PID: $procId)" -ForegroundColor Green
    } else {
        Write-Host "  Port $port ($($ports[$port])): Not in use" -ForegroundColor Gray
    }
}

# 7. Check Node/Python Processes
Write-Host "`n[7/7] Checking Running Processes..." -ForegroundColor Yellow

$pythonProcs = Get-Process -Name python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "  Python processes: $($pythonProcs.Count)" -ForegroundColor Green
    $pythonProcs | ForEach-Object { 
        Write-Host "    - PID $($_.Id): $($_.Path -replace '.*\\', '')" -ForegroundColor Gray 
    }
} else {
    Write-Host "  ! No Python processes running" -ForegroundColor Yellow
}

$nodeProcs = Get-Process -Name node -ErrorAction SilentlyContinue
if ($nodeProcs) {
    Write-Host "  Node processes: $($nodeProcs.Count)" -ForegroundColor Green
    $nodeProcs | ForEach-Object { 
        Write-Host "    - PID $($_.Id)" -ForegroundColor Gray 
    }
} else {
    Write-Host "  ! No Node processes running" -ForegroundColor Yellow
}

# Summary
Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           Diagnostic Summary               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✓ All checks passed! System is healthy." -ForegroundColor Green
} else {
    if ($errors.Count -gt 0) {
        Write-Host "ERRORS ($($errors.Count)):" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "  ✗ $_" -ForegroundColor Red }
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "`nWARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "  ! $_" -ForegroundColor Yellow }
    }
}

# Quick Actions
Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           Quick Actions                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Start Backend:        cd . && uv run python -m backend.main" -ForegroundColor White
Write-Host "Start Frontend:       cd frontend && npm run dev" -ForegroundColor White
Write-Host "Start BFF Demo:       cd frontend-bff && npm run dev" -ForegroundColor White
Write-Host "Build BFF Demo:       cd frontend-bff && npm run build" -ForegroundColor White
Write-Host "Serve BFF Demo:       cd frontend-bff && npx serve dist -l 5174" -ForegroundColor White
Write-Host "Test Backend:         curl http://localhost:8001/docs" -ForegroundColor White
Write-Host "Test BFF Auth:        curl http://localhost:8001/bff/me" -ForegroundColor White

Write-Host "`n" -ForegroundColor White
