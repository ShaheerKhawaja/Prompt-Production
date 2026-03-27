---
name: nuance-engine
description: Use when deciding whether to prompt engineer, context engineer, or use a hybrid approach for a task. Triggers on questions about prompt complexity, technique selection, or architecture decisions.
---

# Nuance Engine

Routes tasks to the right tier via 5 questions. The intellectual core of Prompt Production.

## The Decision Tree

Q1: TURNS — Single = Tier 1 | Multi = Q2 | Orchestrates = Tier 4+
Q2: TOOLS — None = Prompt Eng | 1-3 = Hybrid (Tier 3) | 4+ = Context Eng (Tier 4)
Q3: COMPLIANCE — Regulated domain = +1 tier
Q4: KNOWLEDGE — Training data OK = stay | 1-5 docs = +1 tier | 10+ = Context Eng
Q5: MULTI-AGENT — Part of squad = Context Eng (Tier 4+)

## Tier Map

| Tier | Approach | Tokens | What You Get |
|------|----------|--------|-------------|
| 1 | Prompt eng (simple) | ~500 | Role + rules + format |
| 2 | Prompt eng (moderate) | ~1,500 | Phase-based workflow |
| 3 | Hybrid | ~2,500 | Prompt + tool integration |
| 4 | Context eng (multi-agent) | 3+ prompts | Squad with handoffs |
| 5 | Context eng (full arch) | Full system | Token budgets + KB + monitoring |

## Key Insight
Most over-engineering happens because people default to Tier 5 when Tier 2 would suffice. This engine prevents that.
