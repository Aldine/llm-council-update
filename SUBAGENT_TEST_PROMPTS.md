# Subagent Planning & Delegation Test Prompts

## SDK Runtime Analysis

**Current State:** The Confucius Agent SDK uses a **single-agent orchestrator** with:
- `MemoryManager`: Hierarchical context with session/entry/runnable scopes
- `Orchestrator`: Main loop (max iterations, action parsing, extension routing)
- `Extensions`: Modular tools (Bash, FileEdit, FileRead, FileSearch, Planning, Thinking)
- `RalphOrchestrator`: Wrapper adding Ralph loop pattern (iterate until completion promise)

**Missing:** True subagent spawning. The SDK has no mechanism to:
- Create isolated agent instances
- Delegate tasks to named subagents
- Track subagent call traces
- Merge subagent results

---

## Subagent Implementation Plan

To make subagents work, we need:

```python
@dataclass
class SubagentCall:
    """Traceable subagent invocation"""
    name: str                    # "Scout", "Builder", etc.
    input_summary: str           # Task delegated
    output_summary: str          # Result returned
    timestamp: float
    call_index: int
    actions_taken: List[str]     # Extension calls made
    memory_snapshot: Dict[str, Any]

class SubagentExtension(Extension):
    """Extension that spawns isolated subagents"""
    
    def __init__(self, llm_client, max_depth=2):
        super().__init__("subagent")
        self.llm_client = llm_client
        self.max_depth = max_depth
        self.call_trace: List[SubagentCall] = []
    
    def spawn(self, name: str, task: str, context: RunContext) -> SubagentCall:
        """Spawn isolated subagent, return call record"""
        # Create isolated memory
        sub_memory = MemoryManager()
        sub_orchestrator = Orchestrator(
            llm_client=self.llm_client,
            extensions=self._get_subagent_extensions(),
            memory_manager=sub_memory,
            max_iterations=10
        )
        
        # Run subagent
        result = sub_orchestrator.run(task)
        
        # Record call
        call = SubagentCall(
            name=name,
            input_summary=task[:100],
            output_summary=result['final_output'][:200],
            timestamp=time.time(),
            call_index=len(self.call_trace),
            actions_taken=[a['type'] for a in result['actions']],
            memory_snapshot={'iterations': result['iterations']}
        )
        self.call_trace.append(call)
        return call
```

---

## PROMPT 1: Full Subagent Planning Test (REVISED)

### Goal
Prove planning + extension coordination works inside Confucius Agent SDK. Produce measurable output with computed values, code patches, and execution trace.

### Rules

1. **Plan Section**
   - List 6-10 steps
   - Mark steps as:
     - `[MAIN]` = Main agent handles
     - `[SCOUT]` = Delegate to Scout agent (analysis/measurement)
     - `[BUILD]` = Delegate to Builder agent (code edits/verification)

2. **Extension Trace** (Not "Subagent Trace" - match SDK reality)
   - For each action:
     - Extension name (BashExtension, FileReadExtension, etc.)
     - Input parameters
     - Output summary
     - Timestamp or iteration index
     - Success/failure status

3. **Verification Format**
   ```
   Extension Trace:
   [1] BashExtension
       Input: {"command": "curl http://localhost:3000"}
       Output: "HTML retrieved (2.4KB)"
       Iteration: 1
       Status: ✓
   
   [2] FileReadExtension
       Input: {"path": "src/styles.css"}
       Output: "CSS file read (128 lines)"
       Iteration: 2
       Status: ✓
   ```

4. **If using actual subagents** (requires SubagentExtension):
   ```
   Subagent Trace:
   [1] Scout
       Task: "Extract computed colors from 6 UI elements"
       Actions: [BashExtension, FileReadExtension]
       Output: "Found 6 elements with contrast ratios..."
       Timestamp: 1736898765.234
       Status: ✓
   ```

### Task

**Context:**  
Local app at `http://localhost:3000` with dark mode toggle. Suspect contrast issues and missing focus rings.

**Deliverables:**

1. **Audit Report** (6 UI elements minimum)
   - Element type (body text, heading, link, button primary, button secondary, caption)
   - Computed foreground color (hex)
   - Computed background color (hex)
   - Font size (px)
   - Font weight
   - **Contrast ratio** (computed with formula)
   - WCAG AA status (pass/fail for 4.5:1 text, 3:1 large text)

2. **Fix Proposal**
   - Color values before → after
   - Reason for each change

3. **Patch Output**
   - CSS or Tailwind token edits as diff

4. **Verification**
   - Re-check same 6 elements
   - Updated contrast ratios

5. **Extension Trace** OR **Subagent Trace**

### Execution Steps

1. Open `http://localhost:3000`
2. Toggle dark mode
3. Use browser inspection or file read to get computed styles
4. Compute contrast ratios with formula: `(L1 + 0.05) / (L2 + 0.05)` where L = relative luminance
5. Check focus ring visibility via keyboard navigation (3 interactive elements)
6. Generate fixes
7. Apply patches
8. Re-verify

### Extension Usage (Without Subagents)

**Available Extensions:**
- `BashExtension`: Run curl, grep, node scripts for browser inspection
- `FileReadExtension`: Read CSS/Tailwind config files
- `FileEditExtension`: Apply color fixes to stylesheets
- `FileSearchExtension`: Find color token definitions
- `ThinkingExtension`: Compute contrast ratios
- `PlanningExtension`: Break down audit into steps

### Output Format

```markdown
## Plan
1. [MAIN] Open page and toggle dark mode
2. [MAIN] Extract computed colors (BashExtension + FileReadExtension)
3. [MAIN] Compute contrast ratios (ThinkingExtension)
4. [MAIN] Generate fix proposal
5. [MAIN] Apply patches (FileEditExtension)
6. [MAIN] Re-verify contrast ratios

## Audit Findings
[Table with 6 elements, colors, ratios, pass/fail]

## Fix Proposal
[Before → After with reasons]

## Patch
```diff
- --color-text: #666;
+ --color-text: #4a4a4a;
```

## Verification Results
[Re-checked table]

## Extension Trace
[1] BashExtension...
[2] FileReadExtension...
...
```

---

## PROMPT 2: Extension Trace Sanity Test (Simplified)

**Goal:** Verify extension routing works and produces traceable logs.

**Rules:**
1. Create 5-step plan
2. Use at least 3 different extensions
3. Return extension trace with:
   - Extension name
   - Input summary
   - Output summary
   - Iteration number
4. If extensions fail to execute, return: "Extensions unavailable"

**Task:**
Read `README.md`, search for "install" keyword, output first 3 matches.

**Expected Trace Format:**
```
Extension Trace:
[1] FileReadExtension
    Input: README.md
    Output: 311 lines read
    Iteration: 1
    
[2] FileSearchExtension
    Input: pattern="install"
    Output: 3 matches found at lines 12, 45, 89
    Iteration: 2
```

---

## Action Plan for Implementation

### Phase 1: Verify Current SDK (5 min)
Run PROMPT 2 with Confucius Agent CLI:
```bash
confucius run "$(cat PROMPT_2.txt)" -w ./llm-council-update -v
```

Check output for:
- ✓ Extension names appear
- ✓ Actions are logged
- ✓ Iteration numbers are visible
- ❌ No subagent trace (expected)

### Phase 2: Add SubagentExtension (30 min)
Create `src/confucius_agent/subagent_extension.py`:
```python
from .orchestrator import Extension, Orchestrator
from .extensions import get_default_extensions
# ... (SubagentCall and SubagentExtension code above)
```

### Phase 3: Test Refactored PROMPT 1 (10 min)
```bash
confucius run "$(cat PROMPT_1_REVISED.txt)" -w ./test-app -v
```

Verify:
- ✓ Extension trace shows real computed colors (not invented)
- ✓ Contrast ratios use actual math
- ✓ Patch diffs reference real files
- ✓ Re-verification shows updated ratios

### Phase 4: Add Subagent Support (if needed)
Update `ralph_integration.py`:
```python
def create_coding_agent(..., enable_subagents=False):
    extensions = get_default_extensions(workspace)
    
    if enable_subagents:
        extensions.append(SubagentExtension(llm_client))
    
    return RalphOrchestrator(...)
```

---

## Prompt Refactoring Summary

**Before:** Assumed SDK had subagents (it doesn't)  
**After:** Two-track prompts:
1. **Extension Trace Mode** (works now): Tests orchestrator + extension system
2. **Subagent Trace Mode** (requires implementation): Tests isolated agent spawning

**Key Changes:**
- Replaced "Subagent Trace" with "Extension Trace" for current SDK
- Added explicit extension names matching SDK code
- Added verification that computed values are real (not LLM hallucinations)
- Made trace format match actual SDK logs (iteration, status, extension name)

**Next Step:**  
Tell me if you want:
1. Code to implement SubagentExtension (30 min)
2. Just use Extension Trace mode with current SDK (works now)
3. Both: Add subagents as optional feature flag
