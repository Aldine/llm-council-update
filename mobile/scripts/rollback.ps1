# Rollback to previous update
# Usage: ./scripts/rollback.ps1 -Channel preview -GroupId <group-id>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("preview", "production")]
    [string]$Channel,
    
    [Parameter(Mandatory=$true)]
    [string]$GroupId
)

Write-Host "⏮️ Rolling back $Channel channel to group $GroupId..." -ForegroundColor Yellow

# Republish previous update group
eas channel:edit $Channel --branch $GroupId

Write-Host "✅ Rollback complete!" -ForegroundColor Green
Write-Host "To find group IDs, run: eas update:list --channel $Channel" -ForegroundColor Cyan
