"""Agent 12: Prompt Debugger.

Accepts broken prompts + bad output examples. Diagnoses via the eval pipeline.
Classifies failure type and proposes surgical fixes.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.agents.structural_eval import StructuralEvalAgent
from prompt_production.types import GeneratedPrompt

AGENT_CONFIG = AgentConfig(
    name="debugger",
    agent_number=12,
    description="Diagnoses broken prompts, classifies failure type, proposes fixes",
    phase="cross_cutting",
    tier_scope=None,
    model="claude-opus-4.6",
    stakes="high",
)


class FailureType(StrEnum):
    OVER_CONSTRAINING = "over_constraining"
    UNDER_SPECIFYING = "under_specifying"
    TECHNIQUE_MISMATCH = "technique_mismatch"
    MODEL_INCOMPATIBILITY = "model_incompatibility"
    CONTEXT_ROT = "context_rot"
    KNOWLEDGE_GAP = "knowledge_gap"
    ANTIPATTERN = "antipattern"
    STRUCTURAL = "structural"


class DebugDiagnosis(BaseModel):
    failure_types: list[FailureType]
    root_cause: str
    affected_sections: list[str]
    fix_suggestions: list[str]
    severity: str  # "critical", "high", "medium", "low"
    confidence: float


class DebuggerAgent(BaseAgent):
    """Agent 12: Prompt Debugger."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)
        self._structural_eval = StructuralEvalAgent()

    def diagnose(self, prompt: GeneratedPrompt, bad_output: str = "") -> DebugDiagnosis:
        """Diagnose why a prompt produces bad output."""
        content = prompt.content.lower()
        failure_types: list[FailureType] = []
        affected: list[str] = []
        fixes: list[str] = []

        # Run structural eval first
        structural = self._structural_eval.evaluate(prompt)
        if structural.antipatterns_found:
            failure_types.append(FailureType.ANTIPATTERN)
            affected.extend(structural.antipatterns_found)
            for ap in structural.antipatterns_found:
                fixes.append(f"Remove anti-pattern: {ap}")

        # Check for over-constraining
        constraint_count = content.count("never") + content.count("always") + content.count("must")
        if constraint_count > 10:
            failure_types.append(FailureType.OVER_CONSTRAINING)
            affected.append("constraints section")
            fixes.append(
                f"Reduce hard constraints from {constraint_count} to 5-7 max. Prioritize safety-critical ones."
            )

        # Check for under-specifying
        word_count = len(prompt.content.split())
        has_process = any(k in content for k in ["process", "step", "phase", "protocol"])
        has_constraints = any(k in content for k in ["never", "always", "constraint", "rule"])
        if word_count < 100 and prompt.tier.value >= 3:
            failure_types.append(FailureType.UNDER_SPECIFYING)
            affected.append("overall prompt length")
            fixes.append(
                f"Prompt is {word_count} words for Tier {prompt.tier.value}. Expected ~{prompt.tier.value * 500}."
            )
        if not has_process and prompt.tier.value >= 2:
            failure_types.append(FailureType.UNDER_SPECIFYING)
            affected.append("process/protocol section")
            fixes.append("Add a step-by-step process section. Tier 2+ needs structured flow.")
        if not has_constraints and prompt.tier.value >= 2:
            failure_types.append(FailureType.UNDER_SPECIFYING)
            affected.append("constraints section")
            fixes.append("Add NEVER/ALWAYS rules for critical behaviors.")

        # Check model compatibility
        model = prompt.model_target.lower()
        if "claude" in model and "<" not in prompt.content:
            failure_types.append(FailureType.MODEL_INCOMPATIBILITY)
            affected.append("formatting")
            fixes.append("Claude models perform better with XML-tagged sections. Add <role>, <process>, <constraints>.")
        if "gpt" in model and "#" not in prompt.content:
            failure_types.append(FailureType.MODEL_INCOMPATIBILITY)
            affected.append("formatting")
            fixes.append("GPT models perform better with markdown headers. Add # Role, ## Process, ## Rules.")

        # Check technique mismatch
        if not prompt.techniques_used:
            failure_types.append(FailureType.TECHNIQUE_MISMATCH)
            affected.append("technique selection")
            fixes.append("No techniques selected. Run through the composition engine to select appropriate techniques.")
        if len(prompt.techniques_used) > 4:
            failure_types.append(FailureType.TECHNIQUE_MISMATCH)
            affected.append("technique composition")
            fixes.append(
                f"Over-composed: {len(prompt.techniques_used)} techniques. Max 4. Drop the lowest-priority ones."
            )

        # Analyze bad output for context rot signals
        if bad_output:
            bad_lower = bad_output.lower()
            if any(s in bad_lower for s in ["i don't have", "as an ai", "i cannot", "i'm not sure"]):
                failure_types.append(FailureType.KNOWLEDGE_GAP)
                affected.append("knowledge/context")
                fixes.append("The model lacks domain knowledge. Add a knowledge base section or few-shot examples.")
            if any(s in bad_lower for s in ["previously", "earlier", "as mentioned", "you said"]):
                failure_types.append(FailureType.CONTEXT_ROT)
                affected.append("conversation management")
                fixes.append(
                    "Context rot detected. Add conversation summarization protocol or reduce context window usage."
                )

        if not failure_types:
            failure_types.append(FailureType.STRUCTURAL)
            fixes.append("No obvious issues found. Consider running with real test cases for deeper diagnosis.")

        # Determine severity
        severity = "low"
        if FailureType.ANTIPATTERN in failure_types or FailureType.MODEL_INCOMPATIBILITY in failure_types:
            severity = "high"
        if FailureType.KNOWLEDGE_GAP in failure_types or FailureType.CONTEXT_ROT in failure_types:
            severity = "medium"
        if len(failure_types) >= 3:
            severity = "critical"

        return DebugDiagnosis(
            failure_types=list(dict.fromkeys(failure_types)),
            root_cause=fixes[0] if fixes else "No issues identified",
            affected_sections=list(dict.fromkeys(affected)),
            fix_suggestions=fixes,
            severity=severity,
            confidence=0.7 if bad_output else 0.5,
        )

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        prompt = GeneratedPrompt(**input_data["prompt"])
        bad_output = input_data.get("bad_output", "")
        result = self.diagnose(prompt, bad_output)
        return result.model_dump()
