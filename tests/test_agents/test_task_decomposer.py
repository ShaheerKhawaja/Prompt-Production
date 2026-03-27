"""Tests for Agent 2: Task Decomposer."""

from prompt_production.agents.task_decomposer import TaskDecomposerAgent
from prompt_production.types import Approach, NicheProfile, Tier


def _make_profile(tier: Tier, approach: Approach = Approach.PROMPT_ENGINEER, compliance: list[str] | None = None):
    return NicheProfile(
        domain="fintech/support",
        model_recommendation="claude-sonnet-4.6",
        tier_hint=tier,
        approach=approach,
        constraints=[],
        domain_antipatterns=["policy_hallucination"],
        compliance_requirements=compliance or [],
        deployment_target="api",
        confidence=0.8,
    )


class TestTaskDecomposerAgent:
    def setup_method(self):
        self.agent = TaskDecomposerAgent()

    def test_simple_tier_returns_single_subtask(self):
        profile = _make_profile(Tier.SIMPLE)
        graph = self.agent.decompose(profile, "simple FAQ chatbot")
        assert len(graph.subtasks) == 1
        assert graph.overall_tier == Tier.SIMPLE

    def test_moderate_tier_returns_single_subtask(self):
        profile = _make_profile(Tier.MODERATE)
        graph = self.agent.decompose(profile, "moderate conversation agent")
        assert len(graph.subtasks) == 1
        assert graph.overall_tier == Tier.MODERATE

    def test_complex_tier_decomposes_to_multiple(self):
        profile = _make_profile(Tier.COMPLEX, Approach.HYBRID)
        graph = self.agent.decompose(profile, "fintech support with tools")
        assert len(graph.subtasks) >= 2
        assert graph.overall_tier == Tier.COMPLEX

    def test_complex_with_compliance_adds_subtask(self):
        profile = _make_profile(Tier.COMPLEX, Approach.HYBRID, compliance=["PCI-DSS"])
        graph = self.agent.decompose(profile, "fintech support")
        compliance_tasks = [s for s in graph.subtasks if "compliance" in s.description.lower()]
        assert len(compliance_tasks) >= 1

    def test_multi_agent_has_orchestrator(self):
        profile = _make_profile(Tier.MULTI_AGENT, Approach.CONTEXT_ENGINEER)
        graph = self.agent.decompose(profile, "marketing squad")
        orchestrator_tasks = [s for s in graph.subtasks if "orchestrator" in s.description.lower()]
        assert len(orchestrator_tasks) >= 1
        assert graph.overall_tier == Tier.MULTI_AGENT

    def test_full_architecture_has_kb_and_budget(self):
        profile = _make_profile(Tier.FULL_ARCHITECTURE, Approach.CONTEXT_ENGINEER)
        graph = self.agent.decompose(profile, "complete system")
        descriptions = " ".join(s.description.lower() for s in graph.subtasks)
        assert "knowledge base" in descriptions
        assert "token budget" in descriptions or "context" in descriptions

    def test_max_five_subtasks(self):
        profile = _make_profile(Tier.FULL_ARCHITECTURE, Approach.CONTEXT_ENGINEER)
        graph = self.agent.decompose(profile, "very complex system")
        assert len(graph.subtasks) <= 5

    def test_execution_order_respects_dependencies(self):
        profile = _make_profile(Tier.FULL_ARCHITECTURE, Approach.CONTEXT_ENGINEER)
        graph = self.agent.decompose(profile, "full system")
        order_index = {sid: i for i, sid in enumerate(graph.execution_order)}
        for subtask in graph.subtasks:
            for dep in subtask.dependencies:
                assert order_index[dep] < order_index[subtask.id], (
                    f"{subtask.id} depends on {dep} but {dep} comes later"
                )

    def test_every_subtask_has_techniques(self):
        profile = _make_profile(Tier.COMPLEX, Approach.HYBRID)
        graph = self.agent.decompose(profile, "tool-using agent")
        for subtask in graph.subtasks:
            assert len(subtask.technique_candidates) > 0
