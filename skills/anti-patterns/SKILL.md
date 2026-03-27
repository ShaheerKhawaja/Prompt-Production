---
name: anti-patterns
description: Use when reviewing prompt quality, before shipping a prompt, or when a prompt produces unexpectedly bad output. Triggers on prompt review, quality check, or anti-pattern detection.
---

# Prompt Anti-Patterns

10-point checklist. Score = 10 minus anti-patterns found.

## The Checklist

1. **Superlative inflation** — "elite", "world-class", "cutting-edge" (triggers over-engineering on frontier models)
2. **Capability theater** — Lists what it IS instead of what it DOES (no behavioral change)
3. **Knowledge dumping** — Explains SHAP, LIME, Six Sigma to a model that already knows them
4. **Framework name-dropping** — "Use Chain of Thought" instead of embedding step-by-step structure
5. **Placeholder sections** — XML tags with "[include details here]"
6. **Non-functional commands** — /role_play, /customize that don't work in any deployment
7. **Platform coupling** — Names specific SaaS tools without API access
8. **Aggressive language** — "CRITICAL!", "YOU MUST", "NEVER EVER" (hurts frontier models)
9. **Teaching known concepts** — Explaining what CoT is to a model that invented it
10. **Monolithic design** — Single massive prompt when composition would serve better

## Research Basis
- Anthropic Claude 4 Best Practices (2026): superlatives cause overtriggering
- The Prompt Report (arXiv:2406.06608): 58 techniques, most need behavioral embedding not naming
- Portfolio audit: procedural prompts outperform descriptive prompts (Callback Scheduler vs VC Advisor)
