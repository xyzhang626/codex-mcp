---
name: discuss-with-multi-codex
description: |
  Use this skill for read-only design discussion tasks such as:
  - New feature architecture/design proposals
  - Bug fix strategy and root cause analysis
  - Code refactoring approach evaluation
  - API design review
  - Trade-off analysis between multiple approaches
  Do NOT use this for tasks that require writing or modifying code directly.
  Trigger when the user asks for opinions, design ideas, or wants to discuss approaches.
argument-hint: [topic or question to discuss]
allowed-tools: mcp__codex__codex_async, mcp__codex__codex_poll, mcp__codex__codex_list_tasks, Read, Grep, Glob
---

# Discuss with Multi-Codex

You are facilitating a design discussion by consulting multiple Codex instances in parallel to gather diverse perspectives.

## Workflow

### Step 1: Understand the Context

Before launching Codex discussions, gather necessary context:
- Read relevant source files if the user references specific code
- Understand the codebase structure if needed
- Formulate clear, specific prompts for each Codex instance

### Step 2: Launch Multiple Codex Instances in Parallel

Use `mcp__codex__codex_async` to launch **3 Codex instances** simultaneously, each with a different perspective/role. Send all 3 calls in a **single message** to maximize parallelism.

**Instance roles:**

1. **Architect** - Focuses on system design, scalability, maintainability, and architectural patterns. Prompt prefix: "You are a senior software architect. "
2. **Pragmatist** - Focuses on practical implementation, simplicity, time-to-ship, and avoiding over-engineering. Prompt prefix: "You are a pragmatic senior engineer who values simplicity and shipping fast. "
3. **Critic** - Focuses on edge cases, failure modes, security concerns, and potential pitfalls. Prompt prefix: "You are a thorough code reviewer and devil's advocate. "

Each prompt should include:
- The role prefix above
- The full question/topic from the user (use `$ARGUMENTS` if provided, otherwise use the context from conversation)
- Any relevant code snippets or file contents you gathered in Step 1
- Ask each to provide: their recommendation, key reasoning (2-3 points), and potential risks

### Step 3: Poll for Results

Use `mcp__codex__codex_poll` to check on each task. Poll all 3 tasks. If any are not yet complete, wait briefly and poll again.

### Step 4: Synthesize and Present

Present the results in a structured format:

```
## Discussion Summary: [Topic]

### Architect's View
[Summary of architect perspective]

### Pragmatist's View
[Summary of pragmatist perspective]

### Critic's View
[Summary of critic perspective]

### Consensus & Conflicts
- **Agreement**: Points where all 3 agree
- **Disagreement**: Points of divergence and why
- **Key risks**: Risks identified across perspectives

### Recommended Approach
[Your synthesized recommendation based on all 3 perspectives, weighing the trade-offs]
```

## Important Rules

- Always launch all 3 Codex instances in a **single message** (parallel async calls)
- Include sufficient context in each prompt (don't assume Codex knows the codebase)
- If the user references specific files, read them first and include relevant snippets in the Codex prompts
- Keep each Codex prompt focused and under 2000 words
- The final synthesis should be your own balanced analysis, not just a copy-paste of responses
- This is a **read-only** skill - do NOT modify any files
