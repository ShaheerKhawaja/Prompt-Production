"""Testbench — orchestrates Agents 9-11 and the fix loop.

Runs structural, behavioral, and regression evals in sequence.
If tests fail, routes failures back to the generator for fixing (max 3 iterations).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from prompt_production.agents.behavioral_eval import BehavioralEvalAgent
from prompt_production.agents.regression_eval import RegressionEvalAgent
from prompt_production.agents.structural_eval import StructuralEvalAgent
from prompt_production.types import (
    BehavioralScore,
    EvalFramework,
    EvalResult,
    GateVerdict,
    GeneratedPrompt,
    RegressionScore,
    StructuralScore,
)

logger = logging.getLogger(__name__)

STRUCTURAL_THRESHOLD = 7.5
BEHAVIORAL_PASS_RATE = 0.8  # 80% of tests must pass
MAX_ITERATIONS = 3


@dataclass
class FixSuggestion:
    """What to fix and why."""

    test_id: str
    reason: str
    severity: str
    prompt_section_hint: str = ""


@dataclass
class TestbenchResult:
    """Complete testbench output."""

    verdict: GateVerdict
    result: EvalResult
    fix_suggestions: list[FixSuggestion] = field(default_factory=list)
    iterations_used: int = 1


class Testbench:
    """Orchestrates the 3 eval agents and the fix loop."""

    def __init__(self) -> None:
        self.structural_eval = StructuralEvalAgent()
        self.behavioral_eval = BehavioralEvalAgent()
        self.regression_eval = RegressionEvalAgent()

    def run(
        self,
        prompt: GeneratedPrompt,
        framework: EvalFramework,
        prompt_id: str = "default",
    ) -> TestbenchResult:
        """Run all 3 eval agents and produce a gate verdict."""
        logger.info("Testbench: running structural assessment")
        structural = self.structural_eval.evaluate(prompt)

        logger.info("Testbench: running behavioral assessment")
        behavioral = self.behavioral_eval.assess(prompt, framework)

        logger.info("Testbench: running regression assessment")
        regression = self.regression_eval.assess(prompt_id, structural, behavioral, prompt.version)

        result = EvalResult(structural=structural, behavioral=behavioral, regression=regression)
        verdict = self._compute_verdict(structural, behavioral, regression, iteration=1)

        fix_suggestions: list[FixSuggestion] = []
        if not verdict.passed:
            fix_suggestions = self._generate_fix_suggestions(structural, behavioral)

        return TestbenchResult(
            verdict=verdict,
            result=result,
            fix_suggestions=fix_suggestions,
            iterations_used=1,
        )

    def _compute_verdict(
        self,
        structural: StructuralScore,
        behavioral: BehavioralScore,
        regression: RegressionScore,
        iteration: int,
    ) -> GateVerdict:
        """Determine pass/fail based on thresholds."""
        struct_pass = structural.score >= STRUCTURAL_THRESHOLD
        behav_rate = behavioral.tests_passed / max(behavioral.tests_total, 1)
        behav_pass = behav_rate >= BEHAVIORAL_PASS_RATE
        regression_ok = not regression.regressions or regression.recommendation != "revert"

        passed = struct_pass and behav_pass and regression_ok

        if not struct_pass:
            logger.warning("Structural score %.1f below threshold %.1f", structural.score, STRUCTURAL_THRESHOLD)
        if not behav_pass:
            logger.warning("Behavioral pass rate %.0f%% below threshold %.0f%%",
                           behav_rate * 100, BEHAVIORAL_PASS_RATE * 100)
        if not regression_ok:
            logger.warning("Regression detected: %s", regression.regressions)

        return GateVerdict(
            passed=passed,
            structural_score=structural.score,
            behavioral_pass_rate=behavioral.tests_passed,
            behavioral_total=behavioral.tests_total,
            regression_delta=regression.score_delta,
            iteration=iteration,
            max_iterations=MAX_ITERATIONS,
        )

    def _generate_fix_suggestions(
        self, structural: StructuralScore, behavioral: BehavioralScore
    ) -> list[FixSuggestion]:
        """Generate actionable fix suggestions from failures."""
        suggestions: list[FixSuggestion] = []

        # Structural fixes
        for ap in structural.antipatterns_found:
            suggestions.append(FixSuggestion(
                test_id=f"structural_{ap}",
                reason=f"Anti-pattern detected: {ap}",
                severity="medium",
                prompt_section_hint="Remove or rewrite the flagged content",
            ))

        for issue in structural.issues:
            suggestions.append(FixSuggestion(
                test_id="structural_issue",
                reason=issue,
                severity="medium",
                prompt_section_hint="Address the structural issue",
            ))

        # Behavioral fixes
        for failure in behavioral.failures:
            suggestions.append(FixSuggestion(
                test_id=failure.get("test_id", "unknown"),
                reason=failure.get("reason", ""),
                severity=failure.get("severity", "medium"),
                prompt_section_hint="Add or strengthen the section addressing this behavior",
            ))

        return suggestions
