# Prompt Production v0.0

A 13-agent test-driven context engineering framework.

Takes a 1-line description. Delivers a complete, tested prompt system.

## The Core Insight

Context engineering vs prompt engineering is a **spectrum**, not a switch.
The right approach depends on task complexity, domain, model, and deployment target.

The framework routes every request through a **Nuance Engine** that determines
whether to prompt engineer (simple), context engineer (complex), or both (hybrid).

## Architecture

```
User Input
    |
    v
[Agent 1: Niche Analyzer] --> [Agent 2: Task Decomposer]
    |
    v
[Agent 3: Eval Architect]  <-- eval designed FIRST (TDD for prompts)
    |
    v
[Complexity Router] --> Agents 4-8 (Tier 1-5 specialists)
    |
    v
[Testbench: Agents 9-11] --> Structural + Behavioral + Regression eval
    |
    v
[Test Gate] --> Pass? Ship. Fail? Fix (max 3 loops). --> Deliver
    |
    v
[Agent 12: Debugger]  [Agent 13: Observatory]  [Self-Learning Loop]
```

13 agents. 7-tier complexity routing. 58 composable techniques. Self-learning.

## Quick Start

```bash
uv sync
pp generate "customer support agent for fintech on Claude"
pp analyze "should I prompt engineer or context engineer this?"
pp debug --prompt existing_prompt.md --output bad_output.txt
pp evaluate --prompt my_prompt.md
```

## The 7-Tier Complexity Spectrum

| Tier | Approach | Token Budget | Agent |
|------|----------|-------------|-------|
| 1 | Prompt Engineer (simple) | ~500 | Agent 4 |
| 2 | Prompt Engineer (moderate) | ~1,500 | Agent 5 |
| 3 | Hybrid | ~2,500 | Agent 6 |
| 4 | Context Engineer (multi-agent) | 3+ prompts | Agent 7 |
| 5 | Context Engineer (full architecture) | Full system | Agent 8 |

## Research Foundation

Built on 80+ arxiv papers, 40+ GitHub repos. Key references:
- ACE: Agentic Context Engineering (ICLR 2026, +10.6%)
- GEPA: Reflective Prompt Evolution (ICLR 2026 Oral, +20% over RL)
- MetaClaw: Failure-to-Skill Learning (+18.3% robustness)
- RLM: Recursive Language Models (MIT 2025, 100x context)
- The Prompt Report: 58-technique taxonomy

See [docs/RESEARCH.md](docs/RESEARCH.md) for the complete bibliography.

## Status

- [x] Phase 0: Scaffold
- [ ] Phase 1: Core Pipeline (Agents 1, 2, 3, 6, 9)
- [ ] Phase 2: Full Tier Routing (Agents 4, 5, 7, 8)
- [ ] Phase 3: Technique Composition Engine
- [ ] Phase 4: Full Testbench (Agents 10, 11 + gate)
- [ ] Phase 5: Cross-Cutting (Agents 12, 13 + learning)
- [ ] Phase 6: Integration + E2E

## License

MIT
