---
name: pp:help
description: Show available Prompt Production commands and usage guide
---

# Prompt Production — Help

A 13-agent test-driven context engineering framework.

## Commands

| Command | Description |
|---------|-------------|
| `/pp:generate "description"` | Generate a complete, tested prompt system from a 1-line description |
| `/pp:analyze "task"` | Analyze whether to prompt engineer or context engineer |
| `/pp:debug` | Diagnose a broken prompt and propose surgical fixes |
| `/pp:evaluate` | Score an existing prompt against quality rubrics |
| `/pp:help` | Show this help message |

## Quick Start

**Generate a prompt:**
```
/pp:generate "customer support agent for fintech on Claude"
```

**Check your approach:**
```
/pp:analyze "should I use a simple prompt or full context architecture for my chatbot?"
```

**Debug a broken prompt:**
```
/pp:debug
```
Then paste your prompt and describe the bad output.

## The 7-Tier Complexity Spectrum

| Tier | Approach | When |
|------|----------|------|
| 1 | Prompt Engineer (simple) | Single-turn, no tools, no compliance |
| 2 | Prompt Engineer (moderate) | Multi-turn, no tools |
| 3 | Hybrid | Multi-turn + 1-3 tools |
| 4 | Context Engineer (multi-agent) | Orchestrates agents, 4+ tools |
| 5 | Context Engineer (full arch) | Extensive KB, token budgets, monitoring |

The framework routes automatically. You don't need to choose.
