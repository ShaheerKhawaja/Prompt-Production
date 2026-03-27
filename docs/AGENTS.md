# Agents

13 agents organized into 6 phases.

## Phase 1: UNDERSTAND

| # | Agent | Role | Input | Output |
|---|-------|------|-------|--------|
| 1 | Niche Analyzer | Domain detection, model recommendation, constraint/compliance discovery | User request (string) | NicheProfile |
| 2 | Task Decomposer | Complexity scoring, subtask split, dependency graph, technique candidates | NicheProfile + request | TaskGraph |

## Phase 2: DESIGN EVALS (TDD)

| # | Agent | Role | Input | Output |
|---|-------|------|-------|--------|
| 3 | Eval Architect | Golden tests, adversarial probes, edge cases, scoring rubric | NicheProfile + TaskGraph | EvalFramework |

## Phase 3: GENERATE (routed by tier)

| # | Agent | Tier | Token Target | Specialization |
|---|-------|------|-------------|---------------|
| 4 | Simple Engineer | 1 | ~500 | Role + rules + format |
| 5 | Moderate Engineer | 2 | ~1,500 | Phase-based conversation flow |
| 6 | Complex Engineer | 3 | ~2,500 | Tool integration + compliance |
| 7 | Multi-Agent Architect | 4 | 3+ prompts | Orchestrator + specialists + handoffs |
| 8 | Context Architect | 5 | Full system | Token budgets + KB + compression + monitoring |

## Phase 4: TEST

| # | Agent | Role | What It Checks |
|---|-------|------|---------------|
| 9 | Structural Eval | Anti-pattern detection | 10-point checklist, token efficiency, model compatibility |
| 10 | Behavioral Eval | Test case simulation | Golden, adversarial, edge case pass rates |
| 11 | Regression Eval | Version comparison | Score delta, regressions, recommendation (keep/revert/review) |

## Phase 5: CROSS-CUTTING

| # | Agent | Role | When Used |
|---|-------|------|-----------|
| 12 | Debugger | Diagnose broken prompts | On-demand via /pp:debug |
| 13 | Observatory | Generate monitoring specs | After generation for production prompts |
