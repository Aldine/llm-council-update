# Build native shell for preview channel
# Usage: ./scripts/release-preview.ps1

Write-Host "🚀 Building preview shell with EAS..." -ForegroundColor Cyan

# Build for both platforms
eas build --profile preview --platform all --non-interactive

Write-Host "✅ Preview build submitted!" -ForegroundColor Green
Write-Host "Check build status: eas build:list" -ForegroundColor Yellow
