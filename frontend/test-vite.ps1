# Test script to diagnose Vite/node.exe startup issue
Write-Host "Starting Vite..." -ForegroundColor Green
$viteJob = Start-Job -ScriptBlock {
    Set-Location "c:\Users\chapm\Downloads\llm-council-master\llm-council-master\frontend"
    npm run dev
}

Start-Sleep -Seconds 2

Write-Host "`nChecking if node.exe is running..." -ForegroundColor Yellow
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "✓ node.exe found:" -ForegroundColor Green
    $nodeProcesses | Select-Object Id, ProcessName, Path, StartTime | Format-Table
} else {
    Write-Host "✗ node.exe NOT FOUND" -ForegroundColor Red
}

Write-Host "`nChecking port 5173..." -ForegroundColor Yellow
$portCheck = netstat -aon | Select-String ":5173"
if ($portCheck) {
    Write-Host "✓ Port 5173 is listening:" -ForegroundColor Green
    $portCheck
} else {
    Write-Host "✗ Port 5173 is NOT listening" -ForegroundColor Red
}

Write-Host "`nVite job output:" -ForegroundColor Yellow
Receive-Job -Job $viteJob

Write-Host "`nPress Ctrl+C to stop, or wait 30s..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

Stop-Job -Job $viteJob
Remove-Job -Job $viteJob
