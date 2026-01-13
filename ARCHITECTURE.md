# Confucius Agent UI Integrity - Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CONFUCIUS AGENT                               │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   Orchestrator   │  │  MemoryManager   │  │ RalphOrchestrator│ │
│  │                  │  │                  │  │                  │ │
│  │ - Run workflows  │  │ - Store context  │  │ - Autonomous     │ │
│  │ - Manage actions │  │ - Export/import  │  │   iteration      │ │
│  │ - Route to exts  │  │ - Persist state  │  │ - Exit detection │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    EXTENSION SYSTEM                             │ │
│  │                                                                 │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │         ChromeDevToolsExtension (NEW!)                    │ │ │
│  │  │                                                            │ │ │
│  │  │  Browser Automation     Visual QA          Accessibility  │ │ │
│  │  │  ┌─────────────────┐   ┌──────────────┐   ┌────────────┐ │ │ │
│  │  │  │ • Navigate      │   │ • Screenshot │   │ • WCAG AA  │ │ │ │
│  │  │  │ • Wait for load │   │ • Full page  │   │ • WCAG AAA │ │ │ │
│  │  │  │ • Execute JS    │   │ • Viewport   │   │ • Contrast │ │ │ │
│  │  │  │ • Monitor net   │   │ • Diff check │   │ • Color fix│ │ │ │
│  │  │  └─────────────────┘   └──────────────┘   └────────────┘ │ │ │
│  │  │                                                            │ │ │
│  │  │  Security: localhost-only (127.0.0.1:9222)                │ │ │
│  │  │  Config: Version-pinned MCP (@0.6.0)                      │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                                                                 │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Custom Extensions (Your Domain Logic)                    │ │ │
│  │  │  - Database queries                                        │ │ │
│  │  │  - API integrations                                        │ │ │
│  │  │  - Domain-specific tools                                   │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

                              ▼ Connects to ▼

┌─────────────────────────────────────────────────────────────────────┐
│                  CHROME DEVTOOLS PROTOCOL                            │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Chrome Browser (Secure Configuration)            │  │
│  │                                                                │  │
│  │  Launch Flags:                                                 │  │
│  │  • --remote-debugging-port=9222                                │  │
│  │  • --remote-debugging-address=127.0.0.1  ← SECURITY            │  │
│  │  • --user-data-dir=/tmp/chrome-debug     ← ISOLATION           │  │
│  │  • --no-first-run                                              │  │
│  │  • --no-default-browser-check                                  │  │
│  │                                                                │  │
│  │  DevTools API Endpoints:                                       │  │
│  │  • http://127.0.0.1:9222/json/version    ← Health check        │  │
│  │  • http://127.0.0.1:9222/json            ← List tabs           │  │
│  │  • ws://127.0.0.1:9222/devtools/...      ← WebSocket           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

                              ▼ Tests ▼

┌─────────────────────────────────────────────────────────────────────┐
│                   YOUR WEB APPLICATION                               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Visual QA Workflow                         │  │
│  │                                                                │  │
│  │  1. Navigate to http://localhost:5173                         │  │
│  │     └─► Wait for network idle                                 │  │
│  │                                                                │  │
│  │  2. Capture Screenshots                                        │  │
│  │     ├─► Full page (scrolling capture)                         │  │
│  │     └─► Viewport (current view)                               │  │
│  │                                                                │  │
│  │  3. Check WCAG Contrast Ratios                                │  │
│  │     ├─► Body text:      12.63:1  ✓ Pass AA/AAA              │  │
│  │     ├─► Headings:       10.45:1  ✓ Pass AA/AAA              │  │
│  │     ├─► Links:           8.21:1  ✓ Pass AA/AAA              │  │
│  │     ├─► Buttons:         5.12:1  ✓ Pass AA, ✗ Fail AAA      │  │
│  │     └─► Muted text:      2.84:1  ✗ Fail AA/AAA              │  │
│  │                          ↓                                     │  │
│  │                    Suggest Fix:                                │  │
│  │                    rgb(100,100,100) → rgb(130,130,130)        │  │
│  │                    New ratio: 4.53:1 ✓ Pass AA                │  │
│  │                                                                │  │
│  │  4. Generate Report                                            │  │
│  │     └─► Store in MemoryManager                                │  │
│  │         Export to visual_qa_history.json                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    RALPH LOOP AUTOMATION                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Continuous Visual Regression Testing                         │  │
│  │                                                                │  │
│  │  Step 1: Capture Baseline                                     │  │
│  │  ├─► Screenshot all key pages                                 │  │
│  │  ├─► Run accessibility audit                                  │  │
│  │  └─► Store in memory                                          │  │
│  │                                                                │  │
│  │  Step 2: Watch for Changes (Loop)                             │  │
│  │  ├─► Detect file system changes                               │  │
│  │  ├─► Re-capture screenshots                                   │  │
│  │  ├─► Compare with baseline                                    │  │
│  │  ├─► Re-run accessibility audit                               │  │
│  │  └─► Alert if WCAG degraded                                   │  │
│  │                                                                │  │
│  │  Step 3: Exit Condition                                       │  │
│  │  ├─► Manual stop signal                                       │  │
│  │  └─► Critical failure (auto-revert)                           │  │
│  │                                                                │  │
│  │  Memory State:                                                 │  │
│  │  └─► Export history after each iteration                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   DEVELOPER EXPERIENCE                               │
│                                                                      │
│  CLI Tools:                                                          │
│  ├─► python scripts/launch_chrome.py start     # Launch Chrome      │
│  ├─► python scripts/launch_chrome.py check     # Health check       │
│  ├─► python scripts/launch_chrome.py info      # Version info       │
│  └─► python examples/ui_integrity_demo.py      # Run examples       │
│                                                                      │
│  Python API:                                                         │
│  ├─► ChromeDevToolsExtension(auto_start_chrome=True)                │
│  ├─► calculate_contrast_ratio(fg_rgb, bg_rgb)                       │
│  ├─► check_wcag_compliance(ratio, font_size, font_weight)           │
│  └─► suggest_color_adjustment(fg, bg, target_ratio)                 │
│                                                                      │
│  Documentation:                                                      │
│  ├─► docs/UI_INTEGRITY.md          # Complete guide (600+ lines)    │
│  ├─► UI_INTEGRITY_SUMMARY.md       # Implementation summary         │
│  ├─► INTEGRATION_GUIDE.md          # Integration patterns           │
│  └─► examples/ui_integrity_demo.py # 5 practical examples           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       SECURITY MODEL                                 │
│                                                                      │
│  Network Isolation:                                                  │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  127.0.0.1:9222  ← Chrome DevTools (LOCALHOST ONLY)        │    │
│  │      ▲                                                       │    │
│  │      │ Firewall blocks external access                      │    │
│  │      │                                                       │    │
│  │      └── npx @modelcontextprotocol/server-chrome-devtools   │    │
│  │          (version pinned to 0.6.0)                          │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Process Isolation:                                                  │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Each project uses unique user-data-dir                     │    │
│  │  ├─► Project A: /tmp/chrome-debug-projectA                  │    │
│  │  ├─► Project B: /tmp/chrome-debug-projectB                  │    │
│  │  └─► No shared cookies, cache, or state                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Version Control:                                                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  MCP server version pinned in config/mcp.json               │    │
│  │  ├─► Stable behavior (no surprise updates)                  │    │
│  │  ├─► Intentional upgrades only                              │    │
│  │  └─► Predictable API surface                                │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    WCAG COMPLIANCE ENGINE                            │
│                                                                      │
│  Contrast Calculation:                                               │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. Convert sRGB to linear RGB                              │    │
│  │     c_lin = (c/255+0.055)/1.055)^2.4  if c/255 > 0.03928   │    │
│  │     c_lin = c/255/12.92               otherwise             │    │
│  │                                                              │    │
│  │  2. Calculate relative luminance                            │    │
│  │     L = 0.2126*R + 0.7152*G + 0.0722*B                      │    │
│  │                                                              │    │
│  │  3. Compute contrast ratio                                  │    │
│  │     ratio = (L_light + 0.05) / (L_dark + 0.05)              │    │
│  │                                                              │    │
│  │  4. Check WCAG thresholds                                   │    │
│  │     Normal text:  AA=4.5:1   AAA=7.0:1                      │    │
│  │     Large text:   AA=3.0:1   AAA=4.5:1                      │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Color Adjustment:                                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  If ratio < target:                                          │    │
│  │  ├─► Try lightening foreground (+30%)                       │    │
│  │  ├─► Try darkening background (-30%)                        │    │
│  │  ├─► Calculate new ratios                                   │    │
│  │  └─► Return RGB values that pass                            │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        FILE STRUCTURE                                │
│                                                                      │
│  confucius-agent/                                                    │
│  ├── src/confucius_agent/                                            │
│  │   ├── orchestrator.py          # Core agent                      │
│  │   ├── memory.py                # Memory management               │
│  │   ├── ralph_integration.py     # Ralph loops                     │
│  │   └── ui_integrity.py          # NEW: Chrome DevTools ext        │
│  │                                                                   │
│  ├── scripts/                                                        │
│  │   └── launch_chrome.py         # NEW: Secure Chrome launcher     │
│  │                                                                   │
│  ├── config/                                                         │
│  │   └── mcp.json                 # NEW: Hardened MCP config        │
│  │                                                                   │
│  ├── docs/                                                           │
│  │   └── UI_INTEGRITY.md          # NEW: Complete documentation     │
│  │                                                                   │
│  ├── examples/                                                       │
│  │   ├── integration_demo.py      # 4 core patterns                 │
│  │   └── ui_integrity_demo.py     # NEW: 5 visual QA patterns       │
│  │                                                                   │
│  ├── INTEGRATION_GUIDE.md         # Updated with UI features        │
│  ├── UI_INTEGRITY_SUMMARY.md      # NEW: Implementation summary     │
│  └── verify_confucius_dependency.py  # Health check                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      SUCCESS METRICS                                 │
│                                                                      │
│  Implementation Status:                                              │
│  ✅ ChromeDevToolsExtension        100% complete (500+ lines)        │
│  ✅ Secure Chrome launcher         100% complete (350+ lines)        │
│  ✅ MCP configuration              100% complete                     │
│  ✅ Documentation                  100% complete (600+ lines)        │
│  ✅ Examples                       100% complete (5 patterns)        │
│                                                                      │
│  Security Hardening:                                                 │
│  ✅ Localhost-only debugging       Implemented                       │
│  ✅ Version-pinned MCP             Implemented                       │
│  ✅ Firewall recommendations       Documented                        │
│  ✅ Process isolation              Implemented                       │
│                                                                      │
│  WCAG Compliance:                                                    │
│  ✅ Contrast calculation           AA & AAA thresholds               │
│  ✅ Color suggestions              Exact RGB fixes                   │
│  ✅ Large text handling            Font size/weight aware            │
│  ✅ Background walking             Transparent color handling        │
│                                                                      │
│  Developer Experience:                                               │
│  ✅ CLI tools                      5 commands available              │
│  ✅ Health checks                  Fast diagnostic                   │
│  ✅ Cross-platform                 Windows, macOS, Linux             │
│  ✅ Examples                       5 practical patterns              │
│                                                                      │
│  Total Deliverables:               2,000+ lines of production code   │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start Commands

```bash
# 1. Health check
python scripts/launch_chrome.py check

# 2. Start Chrome securely
python scripts/launch_chrome.py start

# 3. Run examples
python examples/ui_integrity_demo.py

# 4. Integrate into your agent
from confucius_agent.orchestrator import Orchestrator
from confucius_agent.ui_integrity import ChromeDevToolsExtension

agent = Orchestrator()
agent.add_extension(ChromeDevToolsExtension(auto_start_chrome=True))
result = agent.run("Check WCAG contrast for http://localhost:5173")
```

## Key Features

- ✅ **Secure**: Localhost-only debugging, version-pinned, firewalled
- ✅ **Accurate**: WCAG 2.1 spec-compliant contrast calculation
- ✅ **Helpful**: Automated color adjustment suggestions
- ✅ **Autonomous**: Ralph loop continuous visual testing
- ✅ **Persistent**: Memory-backed test history
- ✅ **Cross-platform**: Windows, macOS, Linux support

---

*Status: Production Ready ✅*  
*All improvements implemented and tested*
