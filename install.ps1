<# 
.SYNOPSIS
    Install Confucius Agent globally
.DESCRIPTION
    Installs the confucius-agent Python package globally and sets up VS Code integration
#>

param(
    [switch]$SkipVSCode,
    [switch]$Dev
)

$ErrorActionPreference = "Stop"

Write-Host "🎭 Installing Confucius Agent..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}

# Check Python
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green

# Install package
Write-Host "`n[2/4] Installing confucius-agent package..." -ForegroundColor Yellow
if ($Dev) {
    Write-Host "  (Development mode - editable install)" -ForegroundColor Gray
    pip install -e "$ScriptDir[dev]"
} else {
    pip install "$ScriptDir"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Package installation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Package installed successfully" -ForegroundColor Green

# Verify CLI tools
Write-Host "`n[3/4] Verifying CLI tools..." -ForegroundColor Yellow
$tools = @("confucius", "ralph-loop", "cca")
foreach ($tool in $tools) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "  ✓ $tool" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $tool not found in PATH" -ForegroundColor Yellow
    }
}

# Install VS Code extension (optional)
if (-not $SkipVSCode) {
    Write-Host "`n[4/4] Setting up VS Code integration..." -ForegroundColor Yellow
    
    # Copy user tasks
    $userTasksPath = "$env:APPDATA\Code\User\tasks.json"
    $globalTasksSource = "$ScriptDir\global-tasks.json"
    
    if (Test-Path $globalTasksSource) {
        if (Test-Path $userTasksPath) {
            Write-Host "  User tasks.json already exists - merging..." -ForegroundColor Gray
            # Read existing and new tasks
            $existing = Get-Content $userTasksPath | ConvertFrom-Json
            $new = Get-Content $globalTasksSource | ConvertFrom-Json
            
            # Add new tasks that don't exist
            foreach ($task in $new.tasks) {
                $exists = $existing.tasks | Where-Object { $_.label -eq $task.label }
                if (-not $exists) {
                    $existing.tasks += $task
                    Write-Host "  + Added task: $($task.label)" -ForegroundColor Green
                }
            }
            
            # Add new inputs
            foreach ($input in $new.inputs) {
                $exists = $existing.inputs | Where-Object { $_.id -eq $input.id }
                if (-not $exists) {
                    if (-not $existing.inputs) { $existing.inputs = @() }
                    $existing.inputs += $input
                }
            }
            
            $existing | ConvertTo-Json -Depth 10 | Set-Content $userTasksPath
        } else {
            Copy-Item $globalTasksSource $userTasksPath
            Write-Host "  ✓ Installed global VS Code tasks" -ForegroundColor Green
        }
    }
    
    # Build and install VS Code extension
    $extensionDir = "$ScriptDir\vscode-extension"
    if (Test-Path $extensionDir) {
        Write-Host "  Building VS Code extension..." -ForegroundColor Gray
        Push-Location $extensionDir
        
        if (Get-Command npm -ErrorAction SilentlyContinue) {
            npm install
            npm run compile
            
            if (Get-Command vsce -ErrorAction SilentlyContinue) {
                vsce package
                $vsix = Get-ChildItem *.vsix | Select-Object -First 1
                if ($vsix) {
                    code --install-extension $vsix.FullName
                    Write-Host "  ✓ VS Code extension installed" -ForegroundColor Green
                }
            } else {
                Write-Host "  ⚠ vsce not found - skipping extension packaging" -ForegroundColor Yellow
                Write-Host "    Run: npm install -g @vscode/vsce" -ForegroundColor Gray
            }
        } else {
            Write-Host "  ⚠ npm not found - skipping extension build" -ForegroundColor Yellow
        }
        
        Pop-Location
    }
} else {
    Write-Host "`n[4/4] Skipping VS Code integration (--SkipVSCode)" -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 60 -ForegroundColor Gray
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "`nAvailable commands:" -ForegroundColor Cyan
Write-Host "  confucius run `"<task>`"     - Run AI agent on a task"
Write-Host "  ralph-loop `"<cmd>`"         - Run command until completion"
Write-Host "  confucius notes             - Search past notes"
Write-Host "  confucius init              - Initialize in current workspace"
Write-Host "`nVS Code:" -ForegroundColor Cyan
Write-Host "  Ctrl+Shift+P → 'Tasks: Run Task' → Look for 🎭 tasks"
Write-Host "  Or use Ctrl+Shift+C for quick agent access`n"
