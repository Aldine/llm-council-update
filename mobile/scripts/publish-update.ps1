# Publish OTA update to channel
# Usage: ./scripts/publish-update.ps1 -Channel preview -Message "Fix login bug"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("preview", "production")]
    [string]$Channel,
    
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Write-Host "📦 Publishing update to $Channel channel..." -ForegroundColor Cyan

# Publish update
eas update --channel $Channel --message $Message

Write-Host "✅ Update published to $Channel!" -ForegroundColor Green
Write-Host "Users with matching runtime version will download on next launch" -ForegroundColor Yellow
