# PROMPT 1: Full Accessibility Audit with Planning & Delegation

## Goal
Prove planning + tool coordination works in Confucius Agent SDK. Produce measurable accessibility audit with computed contrast ratios, code patches, and execution trace.

## Rules

### 1. Plan Section
List 6-10 steps. Mark delegation strategy:
- `[MAIN]` = Main agent handles directly
- `[SCOUT]` = Delegate to Scout (if subagents available) for analysis/measurement
- `[BUILD]` = Delegate to Builder (if subagents available) for code edits/verification

### 2. Execution Trace
Choose format based on SDK capabilities:

**Option A: Extension Trace** (works with base SDK)
```
[1] BashExtension
    Command: curl http://localhost:3000
    Output: HTML retrieved (2.4KB)
    Iteration: 1
    Status: ✓

[2] FileReadExtension
    File: src/styles.css
    Output: CSS file read (128 lines)
    Iteration: 2
    Status: ✓
```

**Option B: Subagent Trace** (requires SubagentExtension)
```
[1] Scout
    Task: "Extract computed colors from 6 UI elements"
    Actions: [BashExtension, FileReadExtension]
    Output: "Found 6 elements:\n- body: #333 on #fff\n- h1: #000 on #fff\n..."
    Timestamp: 1736898765.234
    Duration: 287ms
    Status: ✓

[2] Builder
    Task: "Generate CSS fixes for failing contrast ratios"
    Actions: [ThinkingExtension, FileEditExtension]
    Output: "Created patch for src/styles.css with 4 color adjustments"
    Timestamp: 1736898765.621
    Duration: 195ms
    Status: ✓
```

### 3. Computed Values Required
All color contrast must use **real math**, not estimates:
- Relative luminance: `L = 0.2126*R + 0.7152*G + 0.0722*B` (where R,G,B are sRGB normalized)
- Contrast ratio: `(L1 + 0.05) / (L2 + 0.05)` where L1 > L2
- No "approximately 4.2:1" - give exact decimal

---

## Task

### Context
You have a local web app running at `http://localhost:3000` with:
- A dark mode toggle button
- Multiple UI elements (text, headings, links, buttons)
- Suspected WCAG AA contrast failures
- Missing focus ring indicators on some interactive elements

### Deliverables

#### 1. Audit Report
Analyze **minimum 6 UI elements**:
- Body text
- H1 heading
- Hyperlink (default state)
- Primary button
- Secondary button  
- Disabled text or muted caption

For each element, extract:
- **Element selector** (CSS selector or description)
- **Foreground color** (hex, e.g., #1a1a1a)
- **Background color** (hex, e.g., #ffffff)
- **Font size** (px)
- **Font weight** (numeric)
- **Computed contrast ratio** (exact decimal, e.g., 4.73:1)
- **WCAG AA status** (Pass/Fail based on: 4.5:1 for normal text, 3:1 for large text ≥18px or bold ≥14px)

#### 2. Focus Ring Audit
Test keyboard navigation on 3 interactive elements:
- Primary button
- Link
- Form input (if present)

For each:
- Describe current focus indicator (color, style, thickness)
- Measure focus indicator contrast vs background
- Flag if contrast < 3:1 (WCAG 2.1 Level AA requirement)

#### 3. Fix Proposal
For each failing element:
- **Before**: Original color values
- **After**: Proposed color values
- **Reason**: Why this change fixes the issue
- **New contrast ratio**: Exact value after fix

#### 4. Patch Output
Provide code changes as diff-style blocks:
```diff
/* src/styles.css */
- --color-text-muted: #999999;
+ --color-text-muted: #767676;

- --color-link: #6ba3ff;
+ --color-link: #4a8fdb;
```

Or Tailwind config:
```diff
// tailwind.config.js
colors: {
-  'gray-600': '#718096',
+  'gray-600': '#5a6b7f',
}
```

#### 5. Verification
Re-check the same 6 elements **after** applying fixes:
- Updated foreground/background colors
- Updated contrast ratios
- Confirmation all now pass WCAG AA

#### 6. Execution Trace
See "Rules" section above for format options.

---

## Execution Steps

### Phase 1: Inspection
1. Open `http://localhost:3000` in browser or via curl
2. Extract base HTML structure
3. Toggle dark mode (if present)
4. Read CSS files (src/styles.css, tailwind.config.js, etc.)
5. Compute colors for 6 target elements

### Phase 2: Analysis
6. Calculate exact contrast ratios using luminance formula
7. Compare against WCAG AA thresholds
8. Flag failures

### Phase 3: Focus Ring Check
9. Simulate keyboard navigation (Tab key)
10. Inspect focus styles for 3 interactive elements
11. Measure focus indicator contrast

### Phase 4: Fixes
12. Generate color adjustments (darken/lighten as needed)
13. Verify new ratios pass WCAG AA
14. Create patch diffs

### Phase 5: Verification
15. Apply patches to files
16. Re-extract computed colors
17. Re-calculate contrast ratios
18. Confirm all pass

---

## Available Tools/Extensions

### Base SDK (always available):
- **BashExtension**: Run commands (curl, node scripts, grep, etc.)
- **FileReadExtension**: Read CSS, HTML, config files
- **FileEditExtension**: Apply patches to files
- **FileSearchExtension**: Find token definitions, color variables
- **ThinkingExtension**: Perform calculations (luminance, contrast)
- **PlanningExtension**: Break down complex tasks

### With SubagentExtension (optional):
- **Scout**: Specialized agent for analysis/measurement
- **Builder**: Specialized agent for code generation/verification

---

## Output Format

```markdown
## Plan
1. [MAIN] Open http://localhost:3000 and extract HTML
2. [SCOUT] Read CSS files and extract color definitions
3. [SCOUT] Compute colors for 6 UI elements
4. [MAIN] Calculate contrast ratios with formula
5. [SCOUT] Test keyboard focus on 3 interactive elements
6. [MAIN] Generate fix proposal
7. [BUILD] Create patch diffs
8. [BUILD] Apply patches to files
9. [SCOUT] Re-verify contrast ratios
10. [MAIN] Compile final report

## Audit Findings

| Element | Foreground | Background | Size | Weight | Contrast | WCAG AA |
|---------|-----------|------------|------|--------|----------|---------|
| Body text | #333333 | #ffffff | 16px | 400 | 12.63:1 | ✓ Pass |
| H1 heading | #1a1a1a | #ffffff | 32px | 700 | 16.05:1 | ✓ Pass |
| Link | #6ba3ff | #ffffff | 16px | 400 | 2.89:1 | ✗ Fail (need 4.5:1) |
| Primary button | #ffffff | #0066cc | 16px | 600 | 4.54:1 | ✓ Pass |
| Secondary button | #0066cc | #e6f2ff | 16px | 600 | 3.12:1 | ✗ Fail (need 4.5:1) |
| Muted caption | #999999 | #ffffff | 14px | 400 | 2.85:1 | ✗ Fail (need 4.5:1) |

### Focus Ring Audit
1. **Primary button**: 2px solid #0066cc on #ffffff background → Contrast: 4.54:1 ✓ Pass
2. **Link**: 1px dotted #6ba3ff on #ffffff background → Contrast: 2.89:1 ✗ Fail (need 3:1)
3. **Form input**: No visible focus indicator ✗ Fail

## Fix Proposal

### Link Color
- **Before**: #6ba3ff (contrast 2.89:1)
- **After**: #0056b3 (contrast 5.02:1)
- **Reason**: Original too light, fails WCAG AA for normal text

### Secondary Button
- **Before**: #0066cc on #e6f2ff (contrast 3.12:1)
- **After**: #004a99 on #e6f2ff (contrast 4.73:1)
- **Reason**: Darken text to meet 4.5:1 threshold

### Muted Caption
- **Before**: #999999 (contrast 2.85:1)
- **After**: #767676 (contrast 4.54:1)
- **Reason**: Darken gray to meet minimum contrast

### Link Focus Ring
- **Before**: 1px dotted #6ba3ff (contrast 2.89:1)
- **After**: 2px solid #0056b3 (contrast 5.02:1)
- **Reason**: Match link color and increase thickness

### Form Input Focus
- **Before**: No visible indicator
- **After**: 2px solid #0056b3 outline
- **Reason**: Add missing focus indicator

## Patch

```diff
/* src/styles.css */

/* Links */
a {
-  color: #6ba3ff;
+  color: #0056b3;
}

a:focus {
-  outline: 1px dotted #6ba3ff;
+  outline: 2px solid #0056b3;
+  outline-offset: 2px;
}

/* Buttons */
.btn-secondary {
-  color: #0066cc;
+  color: #004a99;
   background: #e6f2ff;
}

/* Typography */
.text-muted {
-  color: #999999;
+  color: #767676;
}

/* Form inputs */
input:focus,
textarea:focus,
select:focus {
+  outline: 2px solid #0056b3;
+  outline-offset: 2px;
}
```

## Verification Results

| Element | Foreground | Background | Contrast | WCAG AA |
|---------|-----------|------------|----------|---------|
| Body text | #333333 | #ffffff | 12.63:1 | ✓ Pass |
| H1 heading | #1a1a1a | #ffffff | 16.05:1 | ✓ Pass |
| Link | #0056b3 | #ffffff | 5.02:1 | ✓ Pass ⬆ |
| Primary button | #ffffff | #0066cc | 4.54:1 | ✓ Pass |
| Secondary button | #004a99 | #e6f2ff | 4.73:1 | ✓ Pass ⬆ |
| Muted caption | #767676 | #ffffff | 4.54:1 | ✓ Pass ⬆ |

### Focus Verification
1. **Primary button**: 2px solid #0066cc → 4.54:1 ✓ Pass
2. **Link**: 2px solid #0056b3 → 5.02:1 ✓ Pass ⬆
3. **Form input**: 2px solid #0056b3 → 5.02:1 ✓ Pass ⬆

**Summary**: All 6 elements + 3 focus states now pass WCAG AA. 5 issues fixed.

## Execution Trace

[Select format based on SDK capabilities - see Rules section]
```

---

## Success Criteria

- ✓ Plan has 6-10 steps with clear delegation markers
- ✓ Audit covers exactly 6 UI elements minimum
- ✓ All contrast ratios are **computed with math**, not guessed
- ✓ Contrast values are exact decimals (e.g., 4.73:1, not "~4.7:1")
- ✓ Patch diffs reference real files with real selectors
- ✓ Verification shows updated ratios after applying patches
- ✓ Execution trace shows real tool/extension/subagent names from SDK
- ✓ Trace includes timestamps or iteration numbers
- ✓ Focus ring audit covers 3 interactive elements

## Failure Conditions

- ✗ No execution trace section
- ✗ Contrast ratios are estimates ("approximately 4:1")
- ✗ Colors are invented (not extracted from actual files)
- ✗ Patch diffs reference non-existent files
- ✗ Verification section identical to findings (no changes applied)
- ✗ Trace uses invented tool names not in SDK
- ✗ Less than 6 elements audited
- ✗ No focus ring testing

---

## Testing This Prompt

```bash
# With base SDK (Extension Trace mode)
cd llm-council-update-new
confucius run "$(cat PROMPT_1_FULL_AUDIT.md)" -w ../test-webapp -v

# With SubagentExtension enabled
python -c "
from confucius_agent import create_subagent_enabled_agent, create_llm_client

agent = create_subagent_enabled_agent(
    llm_client=create_llm_client('gpt-4'),
    workspace='../test-webapp',
    enable_subagents=True,
    verbose=True
)

result = agent.run_ralph_loop(open('PROMPT_1_FULL_AUDIT.md').read())

# Print subagent trace
for ext in agent.orchestrator.extensions:
    if hasattr(ext, 'get_trace_summary'):
        print('\\n' + ext.get_trace_summary())
"
```

---

## Notes

This prompt is designed to:
1. **Force real computation**: Requires exact contrast math, catches LLM hallucinations
2. **Enable verification**: Trace format allows checking if tools actually executed
3. **Test coordination**: Multi-phase workflow tests planning → execution → validation loop
4. **Adapt to SDK**: Works with base extensions OR subagents if available
5. **Produce artifacts**: Generates verifiable patches that can be applied and tested
