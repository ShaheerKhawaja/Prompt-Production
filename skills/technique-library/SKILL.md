---
name: technique-library
description: Use when selecting prompting techniques for a task, composing multiple techniques, or understanding which techniques work for which task types. Triggers on technique selection, composition, or research questions.
---

# Technique Library

28 techniques across 6 categories. 8 composite recipes. Composition rules with bad-combo filtering.

## Quick Selection Guide

| Task Type | Recipe | Techniques |
|-----------|--------|-----------|
| Complex analysis | Deep Reasoning | Meta-Prompting + CoT + Self-Consistency |
| Creative/design | Creative Exploration | EmotionPrompt + ToT + Self-Refine |
| Production agents | Bulletproof Agent | ReAct + Constitutional AI + Recursive Verification |
| Research synthesis | Knowledge Synthesis | GoT + Cumulative Reasoning + Chain of Density |
| Code generation | Code Generation | Self-Debugging + Contrastive CoT |
| Agent squads | Multi-Agent Orchestration | PEER + GoT + Handoff Schemas |
| Full context design | Context Architecture | Step-Back + Recursive Summarization + Token Budget |
| Domain-specific | Domain-Specific | Step-Back + Few-Shot + NEVER/ALWAYS Rules |

## Composition Rules
- Max 4 techniques per prompt
- BAD combos: CoT + ToT, CoT + LATS, GoT + ReAct, Self-Refine + Self-Debugging
- GOOD combos: ReAct + Constitutional AI, Meta-Prompting + CoT, Few-Shot + NEVER/ALWAYS

## Key Principle
Embed techniques as structural scaffolding. NEVER name-drop them in the prompt.
