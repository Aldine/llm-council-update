# Promote preview update to production
# Usage: ./scripts/promote-production.ps1 -GroupId <preview-group-id>

param(
    [Parameter(Mandatory=$true)]
    [string]$GroupId
)

Write-Host "⬆️ Promoting preview update $GroupId to production..." -ForegroundColor Magenta

# Get confirmation
$confirm = Read-Host "Are you sure you want to promote to PRODUCTION? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "❌ Aborted" -ForegroundColor Red
    exit 1
}

# Republish to production channel
eas channel:edit production --branch $GroupId

Write-Host "✅ Promoted to production!" -ForegroundColor Green
Write-Host "All production users will receive this update on next launch" -ForegroundColor Yellow
