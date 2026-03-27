"""Agent 10: Behavioral Eval.

Simulates test cases against generated prompts to verify behavioral
correctness. Scores each test case against the rubric.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import BehavioralScore, EvalFramework, GeneratedPrompt

AGENT_CONFIG = AgentConfig(
    name="behavioral_eval",
    agent_number=10,
    description="Simulates test cases and scores behavioral correctness",
    phase="test",
    tier_scope=None,
    model="claude-sonnet-4.6",
    stakes="high",
)


class BehavioralEvalAgent(BaseAgent):
    """Agent 10: Behavioral Eval."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def assess(self, prompt: GeneratedPrompt, framework: EvalFramework) -> BehavioralScore:
        """Simulate all test cases against the prompt."""
        content_lower = prompt.content.lower()
        failures: list[dict[str, str]] = []

        golden_pass = 0
        golden_total = 0
        adv_pass = 0
        adv_total = 0
        edge_pass = 0
        edge_total = 0

        for tc in framework.test_cases:
            passed = self._simulate_test(content_lower, tc.category, tc.pass_criteria, tc.input_text)

            if tc.category == "golden":
                golden_total += 1
                if passed:
                    golden_pass += 1
                else:
                    failures.append({
                        "test_id": tc.id,
                        "reason": f"Prompt may not handle: {tc.expected_behavior}",
                        "severity": "high",
                    })
            elif tc.category == "adversarial":
                adv_total += 1
                if passed:
                    adv_pass += 1
                else:
                    failures.append({
                        "test_id": tc.id,
                        "reason": f"Adversarial gap: {tc.pass_criteria}",
                        "severity": "critical",
                    })
            elif tc.category == "edge_case":
                edge_total += 1
                if passed:
                    edge_pass += 1
                else:
                    failures.append({
                        "test_id": tc.id,
                        "reason": f"Edge case not covered: {tc.pass_criteria}",
                        "severity": "medium",
                    })

        total_pass = golden_pass + adv_pass + edge_pass
        total_tests = golden_total + adv_total + edge_total

        return BehavioralScore(
            tests_passed=total_pass,
            tests_total=total_tests,
            failures=failures,
            adversarial_passed=adv_pass,
            adversarial_total=adv_total,
            edge_case_passed=edge_pass,
            edge_case_total=edge_total,
        )

    def _simulate_test(self, content: str, category: str, criteria: str, input_text: str) -> bool:
        """Simulate whether the prompt would pass a test case.

        Rule-based simulation for MVP. In production, this would call
        the target model with the prompt + test input and score the output.
        """
        # Adversarial: check if prompt has safety constraints
        if category == "adversarial":
            safety_signals = ["never", "always", "constraint", "refuse", "decline",
                              "do not", "escalat", "maintain", "comply", "scope"]
            return any(s in content for s in safety_signals)

        # Edge case: check if prompt handles error/empty states
        if category == "edge_case":
            edge_signals = ["clarif", "error", "unable", "fallback", "alternative",
                            "apologize", "sorry", "help", "repeat", "rephrase"]
            if not input_text.strip():
                return any(s in content for s in edge_signals)
            return any(s in content for s in edge_signals)

        # Golden: check if prompt addresses the expected behavior topic
        if category == "golden":
            # The prompt should have relevant process/protocol sections
            has_structure = any(k in content for k in ["process", "phase", "step", "protocol"])
            has_domain_relevance = len(content) > 100
            return has_structure and has_domain_relevance

        return True

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        prompt = GeneratedPrompt(**input_data["generated_prompt"])
        framework = EvalFramework(**input_data["eval_framework"])
        result = self.assess(prompt, framework)
        return result.model_dump()
