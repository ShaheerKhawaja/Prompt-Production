"""Tests for the Nuance Engine — 5-question tier routing."""

from prompt_production.engine.nuance import NuanceEngine, NuanceInput
from prompt_production.types import Approach, Tier


class TestNuanceEngine:
    def setup_method(self):
        self.engine = NuanceEngine()

    def test_single_turn_routes_to_prompt_eng(self):
        result = self.engine.analyze(
            NuanceInput(turns="single", tools=0, compliance=False, knowledge_depth="training_data", multi_agent=False)
        )
        assert result.approach == Approach.PROMPT_ENGINEER
        assert result.tier == Tier.SIMPLE

    def test_orchestrator_routes_to_context_eng(self):
        result = self.engine.analyze(
            NuanceInput(
                turns="orchestrates", tools=0, compliance=False, knowledge_depth="training_data", multi_agent=False
            )
        )
        assert result.approach == Approach.CONTEXT_ENGINEER
        assert result.tier.value >= Tier.MULTI_AGENT.value

    def test_multi_turn_no_tools_stays_prompt_eng(self):
        result = self.engine.analyze(
            NuanceInput(turns="multi", tools=0, compliance=False, knowledge_depth="training_data", multi_agent=False)
        )
        assert result.approach == Approach.PROMPT_ENGINEER

    def test_multi_turn_few_tools_goes_hybrid(self):
        result = self.engine.analyze(
            NuanceInput(turns="multi", tools=2, compliance=False, knowledge_depth="training_data", multi_agent=False)
        )
        assert result.approach == Approach.HYBRID
        assert result.tier == Tier.COMPLEX

    def test_multi_turn_many_tools_goes_context_eng(self):
        result = self.engine.analyze(
            NuanceInput(turns="multi", tools=5, compliance=False, knowledge_depth="training_data", multi_agent=False)
        )
        assert result.approach == Approach.CONTEXT_ENGINEER

    def test_compliance_bumps_tier(self):
        base = self.engine.analyze(
            NuanceInput(turns="multi", tools=2, compliance=False, knowledge_depth="training_data", multi_agent=False)
        )
        with_compliance = self.engine.analyze(
            NuanceInput(turns="multi", tools=2, compliance=True, knowledge_depth="training_data", multi_agent=False)
        )
        assert with_compliance.tier.value == base.tier.value + 1

    def test_extensive_kb_forces_context_eng(self):
        result = self.engine.analyze(
            NuanceInput(turns="multi", tools=1, compliance=False, knowledge_depth="extensive", multi_agent=False)
        )
        assert result.approach == Approach.CONTEXT_ENGINEER

    def test_few_docs_bumps_tier(self):
        base = self.engine.analyze(
            NuanceInput(turns="multi", tools=0, compliance=False, knowledge_depth="training_data", multi_agent=False)
        )
        with_docs = self.engine.analyze(
            NuanceInput(turns="multi", tools=0, compliance=False, knowledge_depth="few_docs", multi_agent=False)
        )
        assert with_docs.tier.value >= base.tier.value + 1

    def test_multi_agent_forces_context_eng(self):
        result = self.engine.analyze(
            NuanceInput(turns="single", tools=0, compliance=False, knowledge_depth="training_data", multi_agent=True)
        )
        assert result.approach == Approach.CONTEXT_ENGINEER

    def test_fintech_support_composite(self):
        result = self.engine.analyze(
            NuanceInput(turns="multi", tools=2, compliance=True, knowledge_depth="few_docs", multi_agent=False)
        )
        assert result.tier == Tier.FULL_ARCHITECTURE
        assert result.approach == Approach.CONTEXT_ENGINEER

    def test_simple_chatbot_composite(self):
        result = self.engine.analyze(
            NuanceInput(turns="multi", tools=0, compliance=False, knowledge_depth="training_data", multi_agent=False)
        )
        assert result.tier == Tier.MODERATE
        assert result.approach == Approach.PROMPT_ENGINEER

    def test_reasoning_included(self):
        result = self.engine.analyze(
            NuanceInput(turns="multi", tools=2, compliance=True, knowledge_depth="training_data", multi_agent=False)
        )
        assert result.reasoning != ""
        assert "Q1" in result.questions_answered

    def test_tier_never_exceeds_5(self):
        result = self.engine.analyze(
            NuanceInput(turns="orchestrates", tools=10, compliance=True, knowledge_depth="extensive", multi_agent=True)
        )
        assert result.tier == Tier.FULL_ARCHITECTURE
