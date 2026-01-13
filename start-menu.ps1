# ============================================
# LLM Council - Quick Start Script (PowerShell)
# ============================================

function Show-Menu {
    Clear-Host
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   LLM Council - Quick Start" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "1. " -NoNewline -ForegroundColor Yellow
    Write-Host "Start EVERYTHING (Backend + Frontend + BFF Demo)"
    
    Write-Host "2. " -NoNewline -ForegroundColor Yellow
    Write-Host "Start Backend only (Port 8002)"
    
    Write-Host "3. " -NoNewline -ForegroundColor Yellow
    Write-Host "Start Frontend only (JWT-based, Port 5173)"
    
    Write-Host "4. " -NoNewline -ForegroundColor Yellow
    Write-Host "Start BFF Demo only (Port 5174)"
    
    Write-Host "5. " -NoNewline -ForegroundColor Yellow
    Write-Host "Open Applications in Browser"
    
    Write-Host "6. " -NoNewline -ForegroundColor Yellow
    Write-Host "Stop ALL servers"
    
    Write-Host "7. " -NoNewline -ForegroundColor Yellow
    Write-Host "Run Diagnostics"
    
    Write-Host "8. " -NoNewline -ForegroundColor Yellow
    Write-Host "Exit`n"
}

function Start-AllServices {
    Write-Host "`nStarting all services..." -ForegroundColor Green
    
    # Start backend
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; Write-Host 'Backend starting on port 8002...' -ForegroundColor Green; uv run python -m backend.main" -WindowStyle Normal
    Start-Sleep -Seconds 3
    
    # Start frontend
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; Write-Host 'Frontend starting on port 5173...' -ForegroundColor Green; npm run dev" -WindowStyle Normal
    Start-Sleep -Seconds 2
    
    # Start BFF demo
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend-bff'; Write-Host 'BFF Demo starting on port 5174...' -ForegroundColor Green; npm run dev" -WindowStyle Normal
    
    Write-Host "`nAll services started in separate windows!" -ForegroundColor Green
    Write-Host "`n- Backend:  http://localhost:8002" -ForegroundColor White
    Write-Host "- Frontend: http://localhost:5173" -ForegroundColor White
    Write-Host "- BFF Demo: http://localhost:5174" -ForegroundColor White
    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Start-Backend {
    Write-Host "`nStarting backend on port 8002..." -ForegroundColor Green
    cd $PSScriptRoot
    uv run python -m backend.main
}

function Start-Frontend {
    Write-Host "`nStarting frontend on port 5173..." -ForegroundColor Green
    cd "$PSScriptRoot\frontend"
    npm run dev
}

function Start-BFF {
    Write-Host "`nStarting BFF demo on port 5174..." -ForegroundColor Green
    cd "$PSScriptRoot\frontend-bff"
    npm run dev
}

function Open-Browser {
    Write-Host "`nOpening applications in browser..." -ForegroundColor Green
    Start-Process "http://localhost:8002/docs"
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:5173"
    Start-Sleep -Seconds 1
    Start-Process "http://localhost:5174"
    
    Write-Host "`nOpened:" -ForegroundColor Green
    Write-Host "- API Docs:  http://localhost:8002/docs" -ForegroundColor White
    Write-Host "- Frontend:  http://localhost:5173" -ForegroundColor White
    Write-Host "- BFF Demo:  http://localhost:5174" -ForegroundColor White
    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Stop-AllServers {
    Write-Host "`nStopping all servers..." -ForegroundColor Yellow
    Stop-Process -Name python,node -Force -ErrorAction SilentlyContinue
    Write-Host "All servers stopped!" -ForegroundColor Green
    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Run-Diagnostics {
    Write-Host "`nRunning diagnostics..." -ForegroundColor Yellow
    & "$PSScriptRoot\diagnose.ps1"
    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "`nEnter your choice (1-8)"
    
    switch ($choice) {
        '1' { Start-AllServices }
        '2' { Start-Backend }
        '3' { Start-Frontend }
        '4' { Start-BFF }
        '5' { Open-Browser }
        '6' { Stop-AllServers }
        '7' { Run-Diagnostics }
        '8' { 
            Write-Host "`nGoodbye!" -ForegroundColor Cyan
            exit 
        }
        default {
            Write-Host "`nInvalid choice. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
} while ($true)
