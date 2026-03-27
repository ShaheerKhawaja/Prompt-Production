# Prompt Production

## What This Is
13-agent test-driven context engineering framework. Takes 1-line input,
delivers tested prompt systems. Routes between prompt engineering and
context engineering based on task complexity via Nuance Engine.

## Code Standards
- Python 3.12+, ruff format (line-length=120), mypy strict
- pytest with 80%+ coverage, TDD always
- Pydantic v2 for all data models
- uv for dependency management
- Atomic commits, imperative mood, no secrets

## Architecture
- `src/prompt_production/` -- Main package
- `src/prompt_production/engine/` -- Core: nuance, router, composer, testbench, learner
- `src/prompt_production/agents/` -- 13 agent implementations
- `src/prompt_production/prompts/` -- Agent system prompts (Markdown)
- `techniques/` -- 58 technique definitions (YAML)
- `templates/` -- 5 tier delivery templates
- `playbook/` -- Self-learning storage (gitignored in prod)
- `tests/` -- Pytest suite with fixtures

## Key Patterns
- Nuance Engine: Q1-Q5 decision tree routes to tier 1-5
- TDD for prompts: eval designed BEFORE prompt generated
- Technique composition: select 2-4 from 58, never over-compose
- Test gate: structural (Agent 9) + behavioral (Agent 10) + regression (Agent 11)
- Self-learning: ACE Generate->Reflect->Curate after every generation
- Max 5 subtasks per task graph
- Max 3 fix iterations in test gate loop
- Max 4 techniques composed per prompt

## Agent Index
| # | Name | Phase | Tier |
|---|------|-------|------|
| 1 | Niche Analyzer | Understand | All |
| 2 | Task Decomposer | Understand | All |
| 3 | Eval Architect | Eval (TDD) | All |
| 4 | Simple Engineer | Generate | 1 |
| 5 | Moderate Engineer | Generate | 2 |
| 6 | Complex Engineer | Generate | 3 |
| 7 | Multi-Agent Architect | Generate | 4 |
| 8 | Context Architect | Generate | 5 |
| 9 | Structural Eval | Test | All |
| 10 | Behavioral Eval | Test | All |
| 11 | Regression Eval | Test | All |
| 12 | Debugger | Cross-cutting | All |
| 13 | Observatory | Cross-cutting | All |
