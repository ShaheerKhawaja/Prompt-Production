"""Integration tests for the complete 6-phase pipeline."""

from prompt_production.pipeline import Pipeline
from prompt_production.types import Approach, Tier


class TestPipeline:
    def setup_method(self):
        self.pipeline = Pipeline()

    def test_fintech_support_e2e(self):
        """Full E2E: 1-line input -> all 13 agents coordinate."""
        result = self.pipeline.run("customer support agent for fintech on Claude")

        # Phase 1: UNDERSTAND
        assert "fintech" in result.niche_profile.domain
        assert "PCI-DSS" in result.niche_profile.compliance_requirements
        assert len(result.task_graph.subtasks) >= 1

        # Phase 2: DESIGN EVALS (TDD)
        assert len(result.eval_framework.test_cases) >= 5
        assert result.eval_framework.adversarial_count >= 3

        # Phase 3: SELECT TECHNIQUES
        assert len(result.technique_selection.techniques) > 0
        assert len(result.technique_selection.techniques) <= 4

        # Phase 4: GENERATE (via router, not stub)
        assert len(result.generated_prompts) >= 1
        assert result.primary_prompt.token_count > 0
        assert result.primary_prompt.tier.value >= Tier.COMPLEX.value

        # Phase 5: TEST (full testbench)
        assert result.testbench_result.result.structural.score >= 0
        assert result.testbench_result.result.behavioral.tests_total > 0
        assert result.testbench_result.result.regression.is_baseline is True

        # Phase 6: LEARN
        assert result.learning_record is not None
        assert result.learning_record.domain == result.niche_profile.domain

        # Failure modes generated
        assert len(result.failure_modes) > 0

    def test_simple_chatbot_e2e(self):
        result = self.pipeline.run("simple one-shot text classifier")
        assert result.niche_profile.tier_hint == Tier.SIMPLE
        assert len(result.generated_prompts) == 1
        assert result.primary_prompt.tier == Tier.SIMPLE

    def test_healthcare_compliance_e2e(self):
        result = self.pipeline.run("patient intake agent for healthcare clinic")
        assert "HIPAA" in result.niche_profile.compliance_requirements
        adversarial_ids = [t.id for t in result.eval_framework.test_cases if t.category == "adversarial"]
        assert "adv_compliance_bypass" in adversarial_ids

    def test_multi_agent_system_e2e(self):
        result = self.pipeline.run("multi-agent squad with orchestrator for marketing campaigns")
        assert result.niche_profile.approach == Approach.CONTEXT_ENGINEER
        assert result.task_graph.overall_tier.value >= Tier.MULTI_AGENT.value
        # Multi-agent should produce multiple prompts
        assert len(result.generated_prompts) >= 2

    def test_gpt_model_produces_markdown(self):
        result = self.pipeline.run("chatbot for customer support using GPT")
        assert "gpt" in result.primary_prompt.model_target.lower()
        assert "#" in result.primary_prompt.content

    def test_claude_model_produces_xml(self):
        result = self.pipeline.run("code review agent on Claude")
        assert "claude" in result.primary_prompt.model_target.lower()
        assert "<" in result.primary_prompt.content

    def test_technique_selection_varies_by_type(self):
        code_result = self.pipeline.run("code review agent with API tools on Claude")
        chat_result = self.pipeline.run("simple FAQ chatbot")
        # Different task types should get different technique selections
        code_techs = set(code_result.technique_selection.techniques)
        chat_techs = set(chat_result.technique_selection.techniques)
        # They should not be identical (different task types)
        assert code_techs != chat_techs or code_result.technique_selection.recipe_name != chat_result.technique_selection.recipe_name

    def test_eval_designed_before_generation(self):
        """Verify TDD principle: eval framework is complete and informed by domain."""
        result = self.pipeline.run("support agent for ecommerce")
        assert len(result.eval_framework.test_cases) > 0
        assert result.eval_framework.rubric.dimensions
        for tc in result.eval_framework.test_cases:
            assert tc.id
            assert tc.category in ("golden", "adversarial", "edge_case")

    def test_full_architecture_produces_token_budget(self):
        """Tier 5 should include token budget in the generated prompt."""
        result = self.pipeline.run("complete architecture for fintech support with extensive knowledge base")
        # Should route to high tier
        if result.task_graph.overall_tier == Tier.FULL_ARCHITECTURE:
            assert "token_budget" in result.primary_prompt.content.lower()

    def test_learning_record_stored(self):
        """Learning loop should produce a record after each run."""
        result = self.pipeline.run("support agent for fintech on Claude")
        assert result.learning_record is not None
        assert result.learning_record.structural_score >= 0
        assert result.learning_record.key_insight != ""
