"""The Nuance Engine — routes between prompt engineering and context engineering.

Implements a 5-question decision tree that determines the right tier
and approach for any task. The intellectual core of the framework.

Research basis:
- Anthropic context engineering framework (Sep 2025)
- ACM RecSys 2025: simple prompts often outperform complex ones
- The Prompt Report (arXiv:2406.06608): 58-technique taxonomy
- Anthropic "Building Effective Agents": start simple
"""

from __future__ import annotations

from pydantic import BaseModel

from prompt_production.types import Approach, Tier


class NuanceInput(BaseModel):
    """Input to the Nuance Engine."""

    turns: str  # "single", "multi", "orchestrates"
    tools: int
    compliance: bool
    knowledge_depth: str  # "training_data", "few_docs", "extensive"
    multi_agent: bool


class NuanceResult(BaseModel):
    """Output of the Nuance Engine."""

    tier: Tier
    approach: Approach
    reasoning: str
    questions_answered: dict[str, str]


class NuanceEngine:
    """Routes tasks to the correct tier and approach.

    Q1: TURNS?      Single=PromptEng | Multi=Q2 | Orchestrates=ContextEng
    Q2: TOOLS?      None=PromptEng | 1-3=Hybrid | 4+=ContextEng
    Q3: COMPLIANCE?  Regulated=+1Tier
    Q4: KNOWLEDGE?   TrainingData=stay | FewDocs=+1Tier | Extensive=ContextEng
    Q5: MULTI-AGENT? Yes=ContextEng
    """

    def analyze(self, input_data: NuanceInput) -> NuanceResult:
        tier_value = 1
        approach = Approach.PROMPT_ENGINEER
        questions: dict[str, str] = {}

        # Q1: TURNS
        if input_data.turns == "single":
            tier_value = 1
            approach = Approach.PROMPT_ENGINEER
            questions["Q1"] = "Single turn -> Prompt Engineering (Tier 1)"
        elif input_data.turns == "orchestrates":
            tier_value = 4
            approach = Approach.CONTEXT_ENGINEER
            questions["Q1"] = "Orchestrates agents -> Context Engineering (Tier 4)"
        else:
            tier_value = 2
            questions["Q1"] = "Multi-turn -> Base Tier 2, continue to Q2"

        # Q2: TOOLS (only meaningful for multi-turn)
        if input_data.turns == "multi":
            if input_data.tools == 0:
                approach = Approach.PROMPT_ENGINEER
                questions["Q2"] = "No tools -> Prompt Engineering"
            elif input_data.tools <= 3:
                tier_value = 3
                approach = Approach.HYBRID
                questions["Q2"] = f"{input_data.tools} tools -> Hybrid (Tier 3)"
            else:
                tier_value = 4
                approach = Approach.CONTEXT_ENGINEER
                questions["Q2"] = f"{input_data.tools} tools -> Context Engineering (Tier 4)"

        # Q3: COMPLIANCE modifier
        if input_data.compliance:
            tier_value = min(tier_value + 1, 5)
            questions["Q3"] = "Compliance required -> +1 Tier"
        else:
            questions["Q3"] = "No compliance -> no change"

        # Q4: KNOWLEDGE modifier or override
        if input_data.knowledge_depth == "extensive":
            tier_value = max(tier_value, 4)
            approach = Approach.CONTEXT_ENGINEER
            questions["Q4"] = "Extensive KB (10+ docs) -> Context Engineering"
        elif input_data.knowledge_depth == "few_docs":
            tier_value = min(tier_value + 1, 5)
            questions["Q4"] = "Few docs (1-5) -> +1 Tier"
        else:
            questions["Q4"] = "Training data sufficient -> no change"

        # Q5: MULTI-AGENT override
        if input_data.multi_agent:
            tier_value = max(tier_value, 4)
            approach = Approach.CONTEXT_ENGINEER
            questions["Q5"] = "Multi-agent system -> Context Engineering"
        else:
            questions["Q5"] = "Standalone -> no change"

        # Clamp
        tier_value = max(1, min(tier_value, 5))

        # Auto-upgrade approach when tier reaches 4+
        # Tier 4-5 tasks require context engineering regardless of how they got there
        if tier_value >= 4 and approach != Approach.CONTEXT_ENGINEER:
            approach = Approach.CONTEXT_ENGINEER
            questions["AUTO"] = f"Tier {tier_value} reached -> approach upgraded to Context Engineering"

        reasoning_lines = [f"{k}: {v}" for k, v in questions.items()]
        reasoning = "Nuance Engine Analysis:\n" + "\n".join(reasoning_lines)
        reasoning += f"\nFinal: Tier {tier_value}, Approach: {approach.value}"

        return NuanceResult(
            tier=Tier(tier_value),
            approach=approach,
            reasoning=reasoning,
            questions_answered=questions,
        )
