"""Tests for core data types."""

import pytest

from prompt_production.types import (
    Approach,
    EvalFramework,
    EvalTestCase,
    GateVerdict,
    GeneratedPrompt,
    NicheProfile,
    ScoringRubric,
    Subtask,
    TaskGraph,
    Tier,
)


class TestTier:
    def test_tier_values(self):
        assert Tier.SIMPLE.value == 1
        assert Tier.MODERATE.value == 2
        assert Tier.COMPLEX.value == 3
        assert Tier.MULTI_AGENT.value == 4
        assert Tier.FULL_ARCHITECTURE.value == 5

    def test_approach_values(self):
        assert Approach.PROMPT_ENGINEER.value == "prompt_engineer"
        assert Approach.HYBRID.value == "hybrid"
        assert Approach.CONTEXT_ENGINEER.value == "context_engineer"


class TestNicheProfile:
    def test_valid_profile(self):
        profile = NicheProfile(
            domain="fintech/customer_support",
            model_recommendation="claude-sonnet-4.6",
            tier_hint=Tier.COMPLEX,
            approach=Approach.HYBRID,
            constraints=["PCI", "regulated_language"],
            domain_antipatterns=["policy_hallucination"],
            compliance_requirements=["PCI-DSS"],
            deployment_target="api",
            confidence=0.85,
        )
        assert profile.domain == "fintech/customer_support"
        assert profile.tier_hint == Tier.COMPLEX

    def test_confidence_bounds(self):
        with pytest.raises(ValueError):
            NicheProfile(
                domain="test",
                model_recommendation="claude-sonnet-4.6",
                tier_hint=Tier.SIMPLE,
                approach=Approach.PROMPT_ENGINEER,
                constraints=[],
                domain_antipatterns=[],
                compliance_requirements=[],
                deployment_target="api",
                confidence=1.5,
            )


class TestTaskGraph:
    def test_valid_task_graph(self):
        subtask = Subtask(
            id="A",
            description="Core conversation handler",
            tier=Tier.COMPLEX,
            dependencies=[],
            technique_candidates=["ReAct", "Constitutional AI"],
        )
        graph = TaskGraph(
            subtasks=[subtask],
            overall_tier=Tier.COMPLEX,
            execution_order=["A"],
        )
        assert len(graph.subtasks) == 1
        assert graph.overall_tier == Tier.COMPLEX

    def test_max_subtasks_enforced(self):
        subtasks = [
            Subtask(
                id=str(i),
                description=f"Task {i}",
                tier=Tier.SIMPLE,
                dependencies=[],
                technique_candidates=[],
            )
            for i in range(6)
        ]
        with pytest.raises(ValueError, match="max 5"):
            TaskGraph(
                subtasks=subtasks,
                overall_tier=Tier.COMPLEX,
                execution_order=[str(i) for i in range(6)],
            )


class TestEvalFramework:
    def test_valid_framework(self):
        test_case = EvalTestCase(
            id="golden_1",
            category="golden",
            input_text="What is my account balance?",
            expected_behavior="Call account_lookup tool",
            pass_criteria="Contains balance amount",
        )
        rubric = ScoringRubric(
            dimensions={"accuracy": 10, "compliance": 10, "tone": 10},
            weights={"accuracy": 0.4, "compliance": 0.3, "tone": 0.3},
            pass_threshold=8.0,
        )
        framework = EvalFramework(
            test_cases=[test_case],
            rubric=rubric,
            adversarial_count=3,
            edge_case_count=2,
        )
        assert len(framework.test_cases) == 1
        assert framework.rubric.pass_threshold == 8.0


class TestGeneratedPrompt:
    def test_valid_prompt(self):
        prompt = GeneratedPrompt(
            content="You are a customer support agent...",
            tier=Tier.COMPLEX,
            model_target="claude-sonnet-4.6",
            token_count=2100,
            techniques_used=["ReAct", "Constitutional AI"],
            version="1.0.0",
        )
        assert prompt.token_count == 2100
        assert prompt.tier == Tier.COMPLEX


class TestGateVerdict:
    def test_pass_verdict(self):
        verdict = GateVerdict(
            passed=True,
            structural_score=9.2,
            behavioral_pass_count=11,
            behavioral_total=11,
            regression_delta=0.0,
            iteration=1,
        )
        assert verdict.passed is True

    def test_can_retry_when_failed(self):
        verdict = GateVerdict(
            passed=False,
            structural_score=6.5,
            behavioral_pass_count=7,
            behavioral_total=11,
            regression_delta=-0.5,
            iteration=1,
        )
        assert verdict.can_retry is True

    def test_cannot_retry_at_max(self):
        verdict = GateVerdict(
            passed=False,
            structural_score=6.5,
            behavioral_pass_count=7,
            behavioral_total=11,
            regression_delta=-0.5,
            iteration=3,
        )
        assert verdict.can_retry is False
