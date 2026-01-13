# Start both backend and frontend in background jobs
Write-Host "Starting LLM Council development servers..." -ForegroundColor Green

# Start backend
Write-Host "`n[1/2] Starting Backend (FastAPI on port 8002)..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "c:\Users\chapm\Downloads\llm-council-master\llm-council-master"
    uv run python -m backend.main
}

Start-Sleep -Seconds 2

# Start frontend
Write-Host "[2/2] Starting Frontend (Vite on port 5173)..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "c:\Users\chapm\Downloads\llm-council-master\llm-council-master\frontend"
    npm run dev
}

Start-Sleep -Seconds 3

# Check status
Write-Host "`n" -NoNewline
Write-Host "=== Status Check ===" -ForegroundColor Cyan

$nodeCheck = Get-Process node -ErrorAction SilentlyContinue
if ($nodeCheck) {
    Write-Host "✓ Frontend (node.exe) is running - PID: $($nodeCheck.Id -join ', ')" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend NOT running" -ForegroundColor Red
}

$portCheck = Test-NetConnection 127.0.0.1 -Port 5173 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($portCheck) {
    Write-Host "✓ Port 5173 is reachable" -ForegroundColor Green
} else {
    Write-Host "✗ Port 5173 is NOT reachable" -ForegroundColor Red
}

$backendCheck = Test-NetConnection 127.0.0.1 -Port 8002 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($backendCheck) {
    Write-Host "✓ Port 8002 (backend) is reachable" -ForegroundColor Green
} else {
    Write-Host "✗ Port 8002 (backend) is NOT reachable" -ForegroundColor Red
}

Write-Host "`n" -NoNewline
Write-Host "=== Output Samples ===" -ForegroundColor Cyan
Write-Host "`nBackend output:" -ForegroundColor Yellow
Receive-Job -Job $backendJob | Select-Object -Last 5

Write-Host "`nFrontend output:" -ForegroundColor Yellow
Receive-Job -Job $frontendJob | Select-Object -Last 5

Write-Host "`n" -NoNewline
Write-Host "=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Open http://localhost:5173 in your browser"
Write-Host "2. Press Ctrl+Shift+R for a hard refresh"
Write-Host "3. Check DevTools Console (F12) for errors"
Write-Host "`nTo stop servers: Stop-Job $($backendJob.Id),$($frontendJob.Id); Remove-Job $($backendJob.Id),$($frontendJob.Id)"

Write-Host "`nServers are running in background jobs. Keep this window open!" -ForegroundColor Cyan
Write-Host "Press any key to view live logs (Ctrl+C to exit)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stream logs
while ($true) {
    Clear-Host
    Write-Host "=== Live Logs (Ctrl+C to exit) ===" -ForegroundColor Cyan
    Write-Host "`nBackend:" -ForegroundColor Yellow
    Receive-Job -Job $backendJob | Select-Object -Last 10
    Write-Host "`nFrontend:" -ForegroundColor Yellow
    Receive-Job -Job $frontendJob | Select-Object -Last 10
    Start-Sleep -Seconds 2
}
