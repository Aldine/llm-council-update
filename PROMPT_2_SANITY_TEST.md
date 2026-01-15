# PROMPT 2: Extension/Subagent Sanity Test

## Goal
Verify that extension routing OR subagent delegation works and produces traceable logs.

## Rules
1. Create a 5-step plan
2. Use at least 3 different capabilities (file reading, searching, thinking)
3. Return an execution trace with:
   - Tool/extension/agent name
   - Input summary
   - Output summary
   - Step/iteration number
4. If tools fail to execute, return: "Extensions unavailable" and stop

## Task
Read the file `README.md` in the current workspace, search for the keyword "install", and output the first 3 matches with their line numbers.

## Expected Output Format

```markdown
## Plan
1. Read README.md file
2. Search for keyword "install"
3. Extract first 3 matches with line numbers
4. Format results
5. Return findings

## Execution Trace

### If using Extensions (default):
[1] FileReadExtension
    Input: README.md
    Output: 311 lines read successfully
    Iteration: 1
    Status: ✓

[2] FileSearchExtension  
    Input: pattern="install", file=README.md
    Output: Found 8 matches
    Iteration: 2
    Status: ✓

[3] ThinkingExtension
    Input: Filter to first 3 matches
    Output: Lines 12, 45, 89
    Iteration: 2
    Status: ✓

### If using Subagents (if SubagentExtension is available):
[1] Scout
    Task: "Read README.md and find all occurrences of 'install'"
    Actions: [FileReadExtension, FileSearchExtension]
    Output: "Found 8 matches in README.md at lines 12, 45, 89, 102, 156, 203, 287, 299"
    Timestamp: 1736898765.234
    Duration: 145ms
    Status: ✓

[2] Builder  
    Task: "Format the first 3 matches as a numbered list"
    Actions: [ThinkingExtension]
    Output: "1. Line 12: npm install confucius-agent\n2. Line 45: pip install confucius-agent[all]\n3. Line 89: install.ps1"
    Timestamp: 1736898765.389
    Duration: 82ms
    Status: ✓

## Results
1. Line 12: `npm install confucius-agent`
2. Line 45: `pip install confucius-agent[all]`
3. Line 89: `install.ps1`
```

## Success Criteria
- ✓ Plan has 5 steps
- ✓ At least 3 tools/extensions/subagents used
- ✓ Trace shows real tool names (not invented)
- ✓ Output includes actual line numbers from file
- ✓ Results are verifiable (can manually check README.md)

## Failure Conditions
- ✗ No trace section
- ✗ Invented tool names not in SDK
- ✗ No line numbers or vague "around line X"
- ✗ Output doesn't match actual file content
