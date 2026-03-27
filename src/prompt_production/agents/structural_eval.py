"""Agent 9: Structural Eval.

Evaluates generated prompts for anti-patterns, token efficiency,
model compatibility, and technique validation.
"""

from __future__ import annotations

import re
from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import GeneratedPrompt, StructuralScore

AGENT_CONFIG = AgentConfig(
    name="structural_eval",
    agent_number=9,
    description="Evaluates prompt structure: anti-patterns, token efficiency, model compatibility",
    phase="test",
    tier_scope=None,
    model="claude-sonnet-4.6",
    stakes="medium",
)

_SUPERLATIVES = [
    "elite", "world-class", "cutting-edge", "state-of-the-art", "revolutionary",
    "groundbreaking", "unparalleled", "best-in-class", "top-tier", "premier",
]

_FRAMEWORK_NAMEDROPS = [
    "chain of thought", "tree of thoughts", "graph of thought",
    "use cot", "use tot", "apply react", "use reflexion",
    "use chain-of-thought", "employ chain of thought",
]

_AGGRESSIVE_PATTERNS = [
    r"CRITICAL[!:]", r"YOU MUST", r"NEVER EVER", r"ABSOLUTELY MUST",
    r"FAILURE IS NOT AN OPTION", r"DO NOT UNDER ANY CIRCUMSTANCES",
]

_CAPABILITY_THEATER = [
    "i can help you", "i am capable of", "my capabilities include",
    "i have the ability", "i am designed to", "i am an expert",
    "i excel at", "i specialize in", "my strengths include",
]


class StructuralEvalAgent(BaseAgent):
    """Agent 9: Structural Eval."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def evaluate(self, prompt: GeneratedPrompt) -> StructuralScore:
        """Evaluate a generated prompt for structural quality."""
        content_lower = prompt.content.lower()
        issues: list[str] = []
        antipatterns: list[str] = []

        # Check 1: Superlatives
        found_superlatives = [s for s in _SUPERLATIVES if s in content_lower]
        if found_superlatives:
            antipatterns.append("superlative_inflation")
            issues.append(f"Superlatives found: {', '.join(found_superlatives)}")

        # Check 2: Capability theater
        found_theater = [c for c in _CAPABILITY_THEATER if c in content_lower]
        if found_theater:
            antipatterns.append("capability_theater")
            issues.append("Capability theater: describes what it IS instead of what it DOES")

        # Check 3: Framework name-dropping
        found_namedrops = [f for f in _FRAMEWORK_NAMEDROPS if f in content_lower]
        if found_namedrops:
            antipatterns.append("framework_namedrop")
            issues.append(f"Framework name-drops: {', '.join(found_namedrops)}. Embed behavior, don't name-drop.")

        # Check 4: Aggressive language
        found_aggressive = [p for p in _AGGRESSIVE_PATTERNS if re.search(p, prompt.content)]
        if found_aggressive:
            antipatterns.append("aggressive_language")
            issues.append("Aggressive language detected. Frontier models respond better to calm, direct instructions.")

        # Check 5: Placeholder sections
        if re.search(r"<\w+>\s*\[?\s*(include|add|insert|todo|placeholder)", content_lower):
            antipatterns.append("placeholder_sections")
            issues.append("Placeholder sections found. Every section must have real content.")

        # Check 6: Token efficiency
        words = prompt.content.split()
        filler_words = {"very", "really", "quite", "somewhat", "actually", "basically", "essentially", "literally"}
        filler_count = sum(1 for w in words if w.lower().strip(".,;:!?") in filler_words)
        token_efficiency = max(0.0, 1.0 - (filler_count / max(len(words), 1)) * 10)

        # Check 7: Model compatibility
        model_compat = self._check_model_compatibility(prompt)

        # Check 8: Technique validation
        technique_valid = 0 < len(prompt.techniques_used) <= 4

        if not technique_valid:
            if len(prompt.techniques_used) > 4:
                issues.append(f"Over-composition: {len(prompt.techniques_used)} techniques (max 4)")
            elif len(prompt.techniques_used) == 0:
                issues.append("No techniques selected")

        # Composite score
        antipattern_penalty = len(antipatterns) * 1.0
        base_score = 10.0 - antipattern_penalty
        if not technique_valid:
            base_score -= 1.0
        base_score = base_score * (0.5 + model_compat * 0.05)
        final_score = max(0.0, min(10.0, base_score))

        return StructuralScore(
            score=round(final_score, 1),
            antipatterns_found=antipatterns,
            token_efficiency=round(token_efficiency, 2),
            model_compatibility=model_compat,
            technique_validation=technique_valid,
            issues=issues,
        )

    def _check_model_compatibility(self, prompt: GeneratedPrompt) -> float:
        """Score how well the prompt format matches the target model."""
        content = prompt.content
        model = prompt.model_target.lower()
        score = 7.0  # Base score

        if "claude" in model:
            if "<" in content and ">" in content:
                score += 2.0  # XML tags present = good for Claude
            if any(s in content.lower() for s in _SUPERLATIVES):
                score -= 1.0  # Superlatives hurt Claude
        elif "gpt" in model:
            if content.count("#") >= 2:
                score += 2.0  # Markdown headers = good for GPT
        elif "gemini" in model:
            word_count = len(content.split())
            if word_count < 2000:
                score += 2.0  # Gemini prefers shorter

        return min(10.0, max(0.0, score))

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        prompt = GeneratedPrompt(**input_data["generated_prompt"])
        result = self.evaluate(prompt)
        return result.model_dump()
