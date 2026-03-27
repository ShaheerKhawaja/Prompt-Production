# Architecture

## 6-Phase Pipeline

```
User Input ("customer support agent for fintech on Claude")
    |
    v
Phase 1: UNDERSTAND
  Agent 1 (Niche Analyzer) -> NicheProfile
  Agent 2 (Task Decomposer) -> TaskGraph + Nuance Engine tier routing
    |
    v
Phase 2: DESIGN EVALS (TDD)
  Agent 3 (Eval Architect) -> EvalFramework (golden + adversarial + edge cases)
    |
    v
Phase 3: SELECT TECHNIQUES
  Composer Engine -> TechniqueSelection (2-4 from 28 techniques, 8 recipes)
    |
    v
Phase 4: GENERATE
  Complexity Router -> Agent 4-8 (dispatched by tier)
    Tier 1: Simple Engineer (~500 tokens)
    Tier 2: Moderate Engineer (~1,500 tokens)
    Tier 3: Complex Engineer (~2,500 tokens)
    Tier 4: Multi-Agent Architect (3+ prompts)
    Tier 5: Context Architect (token budgets + KB + monitoring)
    |
    v
Phase 5: TEST
  Agent 9 (Structural Eval) -> anti-patterns, token efficiency
  Agent 10 (Behavioral Eval) -> test case simulation
  Agent 11 (Regression Eval) -> version comparison
  Test Gate: structural >= 7.5 AND behavioral >= 80%
    |
    v
Phase 6: LEARN + DELIVER
  Learning Loop -> JSONL playbook (ACE-inspired reflect + curate)
  Delivery -> prompts + eval suite + failure modes + version info
```

## The Nuance Engine

Routes between prompt engineering and context engineering:

```
Q1: TURNS?      Single = Tier 1 | Multi = Q2 | Orchestrates = Tier 4+
Q2: TOOLS?      None = Prompt Eng | 1-3 = Hybrid | 4+ = Context Eng
Q3: COMPLIANCE?  Regulated = +1 Tier
Q4: KNOWLEDGE?   Training data = stay | 1-5 docs = +1 | 10+ = Context Eng
Q5: MULTI-AGENT? Squad = Context Eng
```

## File Structure

```
src/prompt_production/
  types.py          15 Pydantic models (NicheProfile, TaskGraph, etc.)
  pipeline.py       6-phase orchestrator
  engine/
    nuance.py       Nuance Engine (5-question tier routing)
    router.py       Complexity Router (dispatches to Agents 4-8)
    composer.py     Technique Composition Engine (28 techniques, 8 recipes)
    testbench.py    Test Gate (orchestrates Agents 9-11)
    learner.py      Self-Learning Loop (ACE-inspired)
  agents/
    13 agent implementations (niche_analyzer.py through observatory.py)
  prompts/
    13 agent system prompts (Markdown)
```

## Claude Code Plugin Structure

```
.claude-plugin/plugin.json   Plugin manifest
agents/                      13 agent definitions (Markdown + YAML frontmatter)
commands/                    5 slash commands (/pp:generate, /pp:analyze, etc.)
skills/                      4 skills (prompt-production, nuance-engine, etc.)
techniques/                  28 techniques + 8 recipes + composition rules (YAML)
playbook/                    Self-learning storage (JSONL)
```
