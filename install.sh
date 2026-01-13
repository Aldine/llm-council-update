#!/bin/bash
# Install Confucius Agent globally

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKIP_VSCODE=false
DEV_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-vscode) SKIP_VSCODE=true; shift ;;
        --dev) DEV_MODE=true; shift ;;
        *) shift ;;
    esac
done

echo "🎭 Installing Confucius Agent..."
echo "============================================================"

# Check Python
echo -e "\n[1/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3.10+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"

# Install package
echo -e "\n[2/4] Installing confucius-agent package..."
if [ "$DEV_MODE" = true ]; then
    echo "  (Development mode - editable install)"
    pip3 install -e "$SCRIPT_DIR[dev]"
else
    pip3 install "$SCRIPT_DIR"
fi
echo "✓ Package installed successfully"

# Verify CLI tools
echo -e "\n[3/4] Verifying CLI tools..."
for tool in confucius ralph-loop cca; do
    if command -v $tool &> /dev/null; then
        echo "  ✓ $tool"
    else
        echo "  ⚠ $tool not found in PATH"
    fi
done

# VS Code integration
if [ "$SKIP_VSCODE" = false ]; then
    echo -e "\n[4/4] Setting up VS Code integration..."
    
    # Determine VS Code user directory
    if [[ "$OSTYPE" == "darwin"* ]]; then
        VSCODE_USER_DIR="$HOME/Library/Application Support/Code/User"
    else
        VSCODE_USER_DIR="$HOME/.config/Code/User"
    fi
    
    mkdir -p "$VSCODE_USER_DIR"
    
    # Copy global tasks
    TASKS_SOURCE="$SCRIPT_DIR/global-tasks.json"
    TASKS_DEST="$VSCODE_USER_DIR/tasks.json"
    
    if [ -f "$TASKS_SOURCE" ]; then
        if [ -f "$TASKS_DEST" ]; then
            echo "  User tasks.json exists - please merge manually"
            echo "  Source: $TASKS_SOURCE"
        else
            cp "$TASKS_SOURCE" "$TASKS_DEST"
            echo "  ✓ Installed global VS Code tasks"
        fi
    fi
    
    # Build extension if npm available
    EXTENSION_DIR="$SCRIPT_DIR/vscode-extension"
    if [ -d "$EXTENSION_DIR" ] && command -v npm &> /dev/null; then
        echo "  Building VS Code extension..."
        cd "$EXTENSION_DIR"
        npm install
        npm run compile
        
        if command -v vsce &> /dev/null; then
            vsce package
            VSIX=$(ls *.vsix 2>/dev/null | head -1)
            if [ -n "$VSIX" ]; then
                code --install-extension "$VSIX"
                echo "  ✓ VS Code extension installed"
            fi
        else
            echo "  ⚠ vsce not found - skipping extension packaging"
            echo "    Run: npm install -g @vscode/vsce"
        fi
        cd "$SCRIPT_DIR"
    fi
else
    echo -e "\n[4/4] Skipping VS Code integration (--skip-vscode)"
fi

echo -e "\n============================================================"
echo "🎉 Installation complete!"
echo -e "\nAvailable commands:"
echo "  confucius run \"<task>\"     - Run AI agent on a task"
echo "  ralph-loop \"<cmd>\"         - Run command until completion"
echo "  confucius notes             - Search past notes"
echo "  confucius init              - Initialize in current workspace"
echo -e "\nVS Code:"
echo "  Ctrl+Shift+P → 'Tasks: Run Task' → Look for 🎭 tasks"
