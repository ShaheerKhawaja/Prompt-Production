"""Tests for Phase 5: Debugger, Observatory, Self-Learning Loop."""

import tempfile
from pathlib import Path

from prompt_production.agents.debugger import DebuggerAgent, FailureType
from prompt_production.agents.observatory import ObservatoryAgent
from prompt_production.engine.learner import LearningLoop
from prompt_production.types import (
    Approach,
    BehavioralScore,
    EvalResult,
    GeneratedPrompt,
    NicheProfile,
    Recommendation,
    RegressionScore,
    StructuralScore,
    TechniqueSelection,
    Tier,
)


def _good_prompt() -> GeneratedPrompt:
    return GeneratedPrompt(
        content="<role>You handle support requests.</role>\n<process>\n  1. Verify\n  2. Resolve\n</process>\n<constraints>\n  NEVER fabricate.\n  ALWAYS confirm.\n</constraints>",
        tier=Tier.COMPLEX,
        model_target="claude-sonnet-4.6",
        token_count=30,
        techniques_used=["react", "constitutional_ai"],
        version="1.0.0",
    )


def _bad_prompt() -> GeneratedPrompt:
    return GeneratedPrompt(
        content="You are an elite world-class AI. Use Chain of Thought.",
        tier=Tier.COMPLEX,
        model_target="claude-sonnet-4.6",
        token_count=12,
        techniques_used=[],
        version="1.0.0",
    )


def _profile() -> NicheProfile:
    return NicheProfile(
        domain="fintech/support",
        model_recommendation="claude-sonnet-4.6",
        tier_hint=Tier.COMPLEX,
        approach=Approach.HYBRID,
        constraints=["formal_tone"],
        domain_antipatterns=["policy_hallucination"],
        compliance_requirements=["PCI-DSS"],
        deployment_target="api",
        confidence=0.8,
    )


def _eval_result(score: float = 9.0, passed: int = 10, total: int = 11) -> EvalResult:
    return EvalResult(
        structural=StructuralScore(
            score=score,
            antipatterns_found=[],
            token_efficiency=0.9,
            model_compatibility=9.0,
            technique_validation=True,
            issues=[],
        ),
        behavioral=BehavioralScore(
            tests_passed=passed,
            tests_total=total,
            failures=[],
            adversarial_passed=3,
            adversarial_total=3,
            edge_case_passed=2,
            edge_case_total=2,
        ),
        regression=RegressionScore(
            is_baseline=True,
            score_delta=0.0,
            regressions=[],
            improvements=[],
            recommendation=Recommendation.BASELINE_ESTABLISHED,
        ),
    )


# === DEBUGGER TESTS ===


class TestDebuggerAgent:
    def setup_method(self):
        self.agent = DebuggerAgent()

    def test_diagnoses_antipatterns(self):
        result = self.agent.diagnose(_bad_prompt())
        assert FailureType.ANTIPATTERN in result.failure_types

    def test_diagnoses_under_specifying(self):
        result = self.agent.diagnose(_bad_prompt())
        assert FailureType.UNDER_SPECIFYING in result.failure_types

    def test_diagnoses_technique_mismatch(self):
        result = self.agent.diagnose(_bad_prompt())
        assert FailureType.TECHNIQUE_MISMATCH in result.failure_types

    def test_good_prompt_fewer_issues(self):
        good = self.agent.diagnose(_good_prompt())
        bad = self.agent.diagnose(_bad_prompt())
        assert len(good.failure_types) <= len(bad.failure_types)

    def test_model_incompatibility_detected(self):
        gpt_prompt = GeneratedPrompt(
            content="<role>stuff</role>",  # XML on GPT = mismatch
            tier=Tier.COMPLEX,
            model_target="gpt-5.4",
            token_count=5,
            techniques_used=["react"],
            version="1.0.0",
        )
        result = self.agent.diagnose(gpt_prompt)
        assert FailureType.MODEL_INCOMPATIBILITY in result.failure_types

    def test_bad_output_detected(self):
        result = self.agent.diagnose(_good_prompt(), bad_output="I don't have access to that information")
        assert FailureType.KNOWLEDGE_GAP in result.failure_types
        assert result.confidence == 0.7

    def test_context_rot_detected(self):
        result = self.agent.diagnose(_good_prompt(), bad_output="As I mentioned earlier in our conversation previously")
        assert FailureType.CONTEXT_ROT in result.failure_types

    def test_fix_suggestions_provided(self):
        result = self.agent.diagnose(_bad_prompt())
        assert len(result.fix_suggestions) > 0

    def test_severity_escalates(self):
        result = self.agent.diagnose(_bad_prompt())
        assert result.severity in ("critical", "high")


# === OBSERVATORY TESTS ===


class TestObservatoryAgent:
    def setup_method(self):
        self.agent = ObservatoryAgent()

    def test_generates_metrics(self):
        spec = self.agent.generate_monitoring(_good_prompt(), _profile())
        assert len(spec.metrics) >= 4
        metric_names = [m["name"] for m in spec.metrics]
        assert "resolution_rate" in metric_names

    def test_compliance_alert_for_fintech(self):
        spec = self.agent.generate_monitoring(_good_prompt(), _profile())
        alert_conditions = [a["condition"] for a in spec.alerts]
        assert any("compliance" in c for c in alert_conditions)

    def test_runbook_has_steps(self):
        spec = self.agent.generate_monitoring(_good_prompt(), _profile())
        assert len(spec.runbook_steps) >= 5

    def test_drift_signals_include_model_change(self):
        spec = self.agent.generate_monitoring(_good_prompt(), _profile())
        assert any("model" in s.lower() for s in spec.drift_signals)

    def test_regression_schedule_defined(self):
        spec = self.agent.generate_monitoring(_good_prompt(), _profile())
        assert "weekly" in spec.regression_schedule.lower()


# === SELF-LEARNING LOOP TESTS ===


class TestLearningLoop:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.loop = LearningLoop(playbook_dir=Path(self._tmpdir))

    def test_stores_learning_record(self):
        selection = TechniqueSelection(
            techniques=["react", "constitutional_ai"],
            recipe_name="bulletproof_agent",
            reasoning="Test",
        )
        record = self.loop.reflect_and_curate(_profile(), selection, _eval_result())
        assert record.domain == "fintech/support"
        assert record.structural_score == 9.0

        # Verify stored to disk
        files = list(Path(self._tmpdir).glob("*.jsonl"))
        assert len(files) == 1

    def test_consult_returns_records(self):
        selection = TechniqueSelection(
            techniques=["react"],
            recipe_name=None,
            reasoning="Test",
        )
        self.loop.reflect_and_curate(_profile(), selection, _eval_result())
        records = self.loop.consult("fintech/support", "claude-sonnet-4.6")
        assert len(records) == 1
        assert records[0].domain == "fintech/support"

    def test_consult_empty_domain(self):
        records = self.loop.consult("nonexistent/domain", "claude-sonnet-4.6")
        assert len(records) == 0

    def test_high_score_stores_best_techniques(self):
        selection = TechniqueSelection(
            techniques=["react", "constitutional_ai"],
            reasoning="Test",
        )
        record = self.loop.reflect_and_curate(_profile(), selection, _eval_result(score=9.5))
        assert "react" in record.best_techniques

    def test_low_score_stores_avoid_techniques(self):
        selection = TechniqueSelection(
            techniques=["chain_of_thought"],
            reasoning="Test",
        )
        record = self.loop.reflect_and_curate(_profile(), selection, _eval_result(score=5.0))
        assert len(record.avoid_techniques) > 0

    def test_multiple_records_accumulate(self):
        selection = TechniqueSelection(techniques=["react"], reasoning="Test")
        self.loop.reflect_and_curate(_profile(), selection, _eval_result())
        self.loop.reflect_and_curate(_profile(), selection, _eval_result(score=8.5))
        records = self.loop.consult("fintech/support", "claude-sonnet-4.6")
        assert len(records) == 2
