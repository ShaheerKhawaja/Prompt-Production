"""Agent 11: Regression Eval.

Compares prompt versions. Establishes baselines for v1, detects regressions for v2+.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import BehavioralScore, Recommendation, RegressionScore, StructuralScore

AGENT_CONFIG = AgentConfig(
    name="regression_eval",
    agent_number=11,
    description="Compares prompt versions, detects regressions and drift",
    phase="test",
    tier_scope=None,
    model="claude-sonnet-4.6",
    stakes="medium",
)


class RegressionEvalAgent(BaseAgent):
    """Agent 11: Regression Eval."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)
        self._baselines: dict[str, dict[str, float]] = {}

    def assess(
        self,
        prompt_id: str,
        structural: StructuralScore,
        behavioral: BehavioralScore,
        version: str = "1.0.0",
    ) -> RegressionScore:
        """Compare against baseline or establish one."""
        current_scores = {
            "structural": structural.score,
            "behavioral_rate": behavioral.tests_passed / max(behavioral.tests_total, 1),
            "adversarial_rate": behavioral.adversarial_passed / max(behavioral.adversarial_total, 1),
        }

        baseline = self._baselines.get(prompt_id)

        if baseline is None:
            # First version — establish baseline
            self._baselines[prompt_id] = current_scores
            return RegressionScore(
                is_baseline=True,
                score_delta=0.0,
                regressions=[],
                improvements=[],
                recommendation=Recommendation.BASELINE_ESTABLISHED,
            )

        # Compare against baseline
        regressions: list[str] = []
        improvements: list[str] = []
        total_delta = 0.0

        for dim, current_val in current_scores.items():
            baseline_val = baseline.get(dim, 0.0)
            delta = current_val - baseline_val

            if delta < -0.1:
                regressions.append(f"{dim}: {baseline_val:.2f} -> {current_val:.2f} ({delta:+.2f})")
            elif delta > 0.1:
                improvements.append(f"{dim}: {baseline_val:.2f} -> {current_val:.2f} ({delta:+.2f})")

            total_delta += delta

        # Determine recommendation
        if regressions and not improvements:
            recommendation = Recommendation.REVERT
        elif regressions and improvements:
            recommendation = Recommendation.REVIEW
        elif improvements:
            recommendation = Recommendation.KEEP
            self._baselines[prompt_id] = current_scores
        else:
            recommendation = Recommendation.KEEP

        return RegressionScore(
            is_baseline=False,
            score_delta=round(total_delta, 2),
            regressions=regressions,
            improvements=improvements,
            recommendation=recommendation,
        )

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        structural = StructuralScore(**input_data["structural_score"])
        behavioral = BehavioralScore(**input_data["behavioral_score"])
        prompt_id = input_data.get("prompt_id", "default")
        version = input_data.get("version", "1.0.0")
        result = self.assess(prompt_id, structural, behavioral, version)
        return result.model_dump()
