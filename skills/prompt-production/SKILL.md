---
name: prompt-production
description: Use when creating, evaluating, debugging, or architecting prompts and context systems. Triggers on system prompt design, multi-agent orchestration, prompt quality review, technique selection, or context architecture planning.
---

# Prompt Production

13-agent test-driven context engineering framework. Routes between prompt engineering and context engineering based on task complexity.

## When to Use
- Creating a new system prompt or agent prompt
- Evaluating an existing prompt for quality
- Debugging a prompt that produces bad output
- Designing a multi-agent system with handoff protocols
- Deciding between prompt engineering and context engineering
- Selecting techniques for a specific task type

## Commands
- `/pp:generate "description"` — Full 6-phase pipeline
- `/pp:analyze "task"` — Nuance Engine (prompt vs context decision)
- `/pp:debug` — Diagnose and fix broken prompts
- `/pp:evaluate` — Score prompts against rubrics

## Core Principle
Context engineering vs prompt engineering is a spectrum. The right approach depends on task complexity, domain, model, and deployment target. This framework makes that decision automatically via the Nuance Engine.
