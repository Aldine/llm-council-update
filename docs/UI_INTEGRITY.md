# UI Integrity Extension - Visual QA & Accessibility Guide

## Overview

The UI Integrity Extension adds browser automation, visual QA, and WCAG accessibility checking to Confucius Agent. It uses Chrome DevTools Protocol for programmatic browser control and includes built-in contrast ratio calculators.

## Quick Start

### 1. Launch Chrome Securely

```bash
# Check if Chrome is ready
python scripts/launch_chrome.py check

# Start Chrome with secure debugging
python scripts/launch_chrome.py start

# Manual launch (if script fails)
# See platform-specific commands below
```

**Platform Commands:**

macOS:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --remote-debugging-address=127.0.0.1 \
  --user-data-dir=/tmp/chrome-debug \
  --no-first-run --no-default-browser-check
```

Windows PowerShell:
```powershell
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
  --remote-debugging-port=9222 `
  --remote-debugging-address=127.0.0.1 `
  --user-data-dir='C:\temp\chrome-debug' `
  --no-first-run --no-default-browser-check
```

Linux:
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --remote-debugging-address=127.0.0.1 \
  --user-data-dir=/tmp/chrome-debug \
  --no-first-run --no-default-browser-check
```

### 2. Initialize Extension

```python
from confucius_agent.orchestrator import Orchestrator
from confucius_agent.ui_integrity import ChromeDevToolsExtension

# Create agent with Chrome DevTools
agent = Orchestrator()
chrome_ext = ChromeDevToolsExtension(
    chrome_port=9222,
    chrome_host="127.0.0.1",  # Security: localhost only
    auto_start_chrome=True     # Auto-launch if not running
)
agent.add_extension(chrome_ext)

# Run visual QA
workflow = """
Navigate to http://localhost:5173
Capture full-page screenshot
Check WCAG contrast for body text, headings, links, buttons
Report AA and AAA compliance
"""
result = agent.run(workflow)
```

## Security Configuration

### Hardened MCP Server Config

The `config/mcp.json` pins the Chrome DevTools MCP version for stability:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-chrome-devtools@0.6.0"
      ],
      "env": {
        "CHROME_PORT": "9222"
      }
    }
  }
}
```

**Security Notes:**
- ✅ Version pinned to 0.6.0 (update intentionally, not automatically)
- ✅ Chrome launches with `--remote-debugging-address=127.0.0.1` (localhost only)
- ✅ Firewall should block port 9222 on external interfaces
- ✅ Unique `user-data-dir` per project to avoid cross-contamination

### Health Check

Before running visual QA, verify Chrome is accessible:

```bash
# Using the script
python scripts/launch_chrome.py check

# Using curl
curl -s http://127.0.0.1:9222/json/version

# Expected output: JSON with Browser, Protocol-Version, webSocketDebuggerUrl
```

## WCAG Contrast Checking

### Programmatic Contrast Calculation

```python
from confucius_agent.ui_integrity import ChromeDevToolsExtension

chrome_ext = ChromeDevToolsExtension()

# Calculate contrast ratio
fg_rgb = (255, 255, 255)  # White text
bg_rgb = (30, 30, 30)     # Dark background
ratio = chrome_ext.calculate_contrast_ratio(fg_rgb, bg_rgb)
print(f"Contrast: {ratio:.2f}:1")  # 12.63:1

# Check WCAG compliance
compliance = chrome_ext.check_wcag_compliance(
    contrast_ratio=ratio,
    font_size=16,      # pixels
    font_weight=400    # normal
)
print(f"AA: {compliance['AA']}")    # True
print(f"AAA: {compliance['AAA']}")  # True
```

### WCAG Thresholds

| Text Type | WCAG AA | WCAG AAA |
|-----------|---------|----------|
| Normal text (< 18pt/24px) | 4.5:1 | 7.0:1 |
| Large text (≥ 18pt/24px or ≥ 14pt bold) | 3.0:1 | 4.5:1 |

### Color Adjustment Suggestions

```python
# Get color recommendations to meet WCAG
suggestions = chrome_ext.suggest_color_adjustment(
    fg_rgb=(100, 100, 100),  # Too low contrast
    bg_rgb=(255, 255, 255),
    target_ratio=4.5
)

# Output:
# {
#   "adjustment_needed": True,
#   "current_ratio": 2.84,
#   "target_ratio": 4.5,
#   "suggestions": [
#     {
#       "type": "lighten_foreground",
#       "color": "rgb(130, 130, 130)",
#       "ratio": 4.53
#     }
#   ]
# }
```

## Visual QA Workflows

### Basic Screenshot & Audit

```python
agent = Orchestrator()
agent.add_extension(ChromeDevToolsExtension(auto_start_chrome=True))

workflow = """
1. Navigate to http://localhost:5173
2. Wait for network idle
3. Capture full-page screenshot
4. Capture viewport screenshot at 100% zoom
5. Check contrast for:
   - Body text
   - Headings (h1, h2, h3)
   - Links (normal, hover)
   - Primary buttons
   - Error text
6. Report pass/fail for AA and AAA
7. If failures, suggest color fixes
"""

result = agent.run(workflow)
# Screenshots saved to artifacts
# Contrast data in result.context.artifacts
```

### Dark Mode Validation

```python
# Define your dark mode palette
dark_palette = {
    "background": (24, 24, 27),      # zinc-900
    "text": (250, 250, 250),         # zinc-50
    "text_muted": (161, 161, 170),   # zinc-400
    "primary": (59, 130, 246),       # blue-500
    "success": (34, 197, 94),        # green-500
    "error": (239, 68, 68),          # red-500
}

chrome_ext = ChromeDevToolsExtension()

# Check each color against background
for label, fg_color in dark_palette.items():
    if label == "background":
        continue
    
    ratio = chrome_ext.calculate_contrast_ratio(
        fg_color, 
        dark_palette["background"]
    )
    compliance = chrome_ext.check_wcag_compliance(ratio, 16, 400)
    
    status = "✓" if compliance["AA"] else "✗"
    print(f"{status} {label}: {ratio:.2f}:1")
```

### Ralph Loop Visual Regression

```python
# Continuous visual testing with autonomous iteration
memory = MemoryManager()
agent = Orchestrator()
agent.add_extension(ChromeDevToolsExtension(auto_start_chrome=True))

ralph_workflow = """
Ralph Loop: Continuous Visual Regression Testing

Initial Setup:
1. Navigate to test environment
2. Capture baseline screenshots for all key pages
3. Run accessibility audit and store in memory
4. Export memory state as baseline

Loop (autonomous iteration):
1. Wait for file changes or manual trigger
2. Navigate to each key page
3. Capture current screenshots
4. Compare with baseline (pixel diff)
5. Re-run accessibility audit
6. If differences detected:
   a. Generate visual diff report
   b. Check if contrast ratios changed
   c. Alert if WCAG compliance degraded
   d. Store results in memory
7. Update baseline if changes approved
8. Export memory state for history

Success Criteria:
- No WCAG AA failures introduced
- Visual changes intentional and approved
- Contrast maintained or improved

Exit Conditions:
- Manual stop signal
- Critical accessibility failure (auto-revert)
"""

result = agent.run(ralph_workflow)
# Loop executes until exit condition
# Full history stored in memory
```

## In-Browser Contrast Script

Inject this JavaScript into pages via Chrome DevTools to measure live contrast ratios:

```javascript
(() => {
  function srgbToLin(c) {
    c /= 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  }
  
  function luminance(rgb) {
    const [r, g, b] = rgb;
    return 0.2126 * srgbToLin(r) + 0.7152 * srgbToLin(g) + 0.0722 * srgbToLin(b);
  }
  
  function parseRgb(str) {
    const m = str.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
    return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
  }
  
  function contrastRatio(fg, bg) {
    const L1 = luminance(fg);
    const L2 = luminance(bg);
    const light = Math.max(L1, L2);
    const dark = Math.min(L1, L2);
    return (light + 0.05) / (dark + 0.05);
  }
  
  function effectiveBackground(el) {
    let node = el;
    while (node && node !== document.documentElement) {
      const bg = getComputedStyle(node).backgroundColor;
      if (bg && !bg.includes("rgba(0, 0, 0, 0)")) return bg;
      node = node.parentElement;
    }
    return getComputedStyle(document.documentElement).backgroundColor || "rgb(255,255,255)";
  }

  // Check specific element (update selector as needed)
  const el = document.querySelector("main p") || document.body;
  const cs = getComputedStyle(el);
  const fg = parseRgb(cs.color);
  const bg = parseRgb(effectiveBackground(el));
  const ratio = (fg && bg) ? contrastRatio(fg, bg) : null;

  return {
    selector: el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ')[0] : ''),
    textSample: (el.textContent || "").trim().slice(0, 80),
    color: cs.color,
    background: effectiveBackground(el),
    fontSize: cs.fontSize,
    fontWeight: cs.fontWeight,
    contrastRatio: ratio ? Number(ratio.toFixed(2)) : null
  };
})();
```

## Accessibility Alternatives

### Option A: axe-core Integration

**Pros:**
- Catches more than just contrast (ARIA, keyboard nav, semantics)
- Fast automated signal
- Industry standard

**Cons:**
- More setup complexity
- Noisy without tuning
- May miss custom UI states

### Option B: Lighthouse

**Pros:**
- Standardized scoring (0-100)
- Easy to explain to stakeholders
- CI/CD friendly

**Cons:**
- Flaky across runs
- Misses some dynamic UI states
- Heavier weight

### Option C: Manual + Strict (Current Approach)

**Pros:**
- Accurate for real UI states
- Full control over what's checked
- No false positives

**Cons:**
- Slower than automated tools
- Depends on targeting discipline
- Manual test case maintenance

## Troubleshooting

### Chrome Won't Start

```bash
# Check if already running
python scripts/launch_chrome.py check

# Check Chrome path
which google-chrome  # Linux
where chrome.exe     # Windows

# Try manual launch with verbose output
google-chrome --version
```

### Port 9222 Already in Use

```bash
# Find process using port
# Linux/macOS
lsof -i :9222

# Windows
netstat -ano | findstr :9222

# Kill existing Chrome
pkill -f "remote-debugging-port=9222"
```

### Connection Refused

1. Verify Chrome launched with correct flags
2. Check firewall isn't blocking localhost
3. Ensure `--remote-debugging-address=127.0.0.1` is set
4. Try `curl http://127.0.0.1:9222/json/version`

### Contrast Calculation Issues

- RGB values must be 0-255 (not 0.0-1.0)
- Background must be opaque (walk up DOM for transparent elements)
- Font size in pixels, not points (1pt ≈ 1.33px)

## Examples

See `examples/ui_integrity_demo.py` for:
1. Basic visual QA workflow
2. Contrast ratio analysis
3. Dark mode palette validation
4. Ralph loop autonomous testing
5. Multi-viewport responsive testing

Run examples:
```bash
# Start Chrome
python scripts/launch_chrome.py start

# Run examples
python examples/ui_integrity_demo.py
```

## Best Practices

✅ **DO:**
- Pin MCP version in config/mcp.json
- Launch Chrome with `--remote-debugging-address=127.0.0.1`
- Run health check before visual QA
- Store baseline screenshots in memory
- Check contrast for all text elements
- Test dark mode separately

❌ **DON'T:**
- Pull latest MCP version on every run
- Expose port 9222 to external network
- Skip health checks
- Rely on visual inspection alone
- Ignore large text thresholds
- Test only in one viewport

## Integration Checklist

- [ ] Pin Chrome DevTools MCP version in `config/mcp.json`
- [ ] Add `--remote-debugging-address=127.0.0.1` to Chrome launch
- [ ] Configure firewall to block external access to port 9222
- [ ] Create unique `user-data-dir` per project
- [ ] Add health check to CI/CD pipeline (`python scripts/launch_chrome.py check`)
- [ ] Document color palette with expected contrast ratios
- [ ] Create baseline screenshots for visual regression
- [ ] Set up Ralph loop for continuous testing
- [ ] Export memory state after each test run

## Metrics

**Current Capabilities:**
- ✅ Secure Chrome launch (localhost-only)
- ✅ WCAG contrast calculation (AA & AAA)
- ✅ Color adjustment suggestions
- ✅ Screenshot capture (full & viewport)
- ✅ Memory-backed test history
- ✅ Ralph loop autonomous iteration
- ✅ Health check utilities

**Coming Soon:**
- [ ] Pixel diff comparison
- [ ] Focus ring visibility checks
- [ ] Keyboard navigation testing
- [ ] axe-core integration
- [ ] CI/CD pipeline templates
