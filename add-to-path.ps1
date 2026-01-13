<# 
.SYNOPSIS
    Add Confucius Agent to system PATH for global access
.DESCRIPTION
    Adds the Python virtual environment Scripts folder to PATH
    so confucius and ralph-loop commands work from any terminal
#>

$ScriptsPath = "C:\Users\chapm\Downloads\.venv\Scripts"

# Check if already in PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -like "*$ScriptsPath*") {
    Write-Host "✓ Already in PATH" -ForegroundColor Green
} else {
    # Add to user PATH
    $newPath = "$currentPath;$ScriptsPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "✓ Added to PATH: $ScriptsPath" -ForegroundColor Green
    Write-Host "`nPlease restart your terminal for changes to take effect." -ForegroundColor Yellow
}

Write-Host "`nAvailable commands:" -ForegroundColor Cyan
Write-Host "  confucius --help"
Write-Host "  ralph-loop --help"
Write-Host "  cca --help"
