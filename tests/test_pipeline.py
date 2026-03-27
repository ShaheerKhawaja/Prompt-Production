"""Integration tests for the pipeline orchestrator."""

from prompt_production.pipeline import Pipeline
from prompt_production.types import Approach, Tier


class TestPipeline:
    def setup_method(self):
        self.pipeline = Pipeline()

    def test_fintech_support_e2e(self):
        """TEST GATE 1: Full pipeline for a Tier 3 fintech support prompt."""
        result = self.pipeline.run("customer support agent for fintech on Claude")

        # Phase 1 checks
        assert "fintech" in result.niche_profile.domain
        assert "PCI-DSS" in result.niche_profile.compliance_requirements
        assert "claude" in result.niche_profile.model_recommendation.lower()

        # Phase 2 checks
        assert len(result.task_graph.subtasks) >= 1
        assert result.task_graph.overall_tier.value >= Tier.COMPLEX.value

        # Phase 3 checks (assessment framework designed BEFORE prompt)
        assert len(result.eval_framework.test_cases) >= 5
        assert result.eval_framework.adversarial_count >= 3
        assert result.eval_framework.edge_case_count >= 2
        assert result.eval_framework.rubric.pass_threshold == 8.0

        # Phase 4 checks (prompt generated)
        assert result.generated_prompt.token_count > 0
        assert len(result.generated_prompt.techniques_used) > 0
        assert len(result.generated_prompt.techniques_used) <= 4

        # Phase 5 checks (structural assessment)
        assert result.structural_score.score >= 0.0
        assert len(result.structural_score.antipatterns_found) == 0  # Clean prompt

    def test_simple_chatbot_e2e(self):
        """Simple chatbot should produce a smaller, simpler output."""
        result = self.pipeline.run("simple one-shot text classifier")

        assert result.niche_profile.tier_hint == Tier.SIMPLE
        assert result.task_graph.overall_tier == Tier.SIMPLE
        assert len(result.task_graph.subtasks) == 1

    def test_healthcare_compliance_e2e(self):
        """Healthcare should trigger HIPAA compliance."""
        result = self.pipeline.run("patient intake agent for healthcare clinic")

        assert "HIPAA" in result.niche_profile.compliance_requirements
        assert "healthcare" in result.niche_profile.domain

        # Assessment should include compliance-bypass adversarial test
        adversarial_ids = [t.id for t in result.eval_framework.test_cases if t.category == "adversarial"]
        assert "adv_compliance_bypass" in adversarial_ids

    def test_multi_agent_system_e2e(self):
        """Multi-agent request should decompose into orchestrator + specialists."""
        result = self.pipeline.run("multi-agent squad with orchestrator for marketing campaigns")

        assert result.niche_profile.approach == Approach.CONTEXT_ENGINEER
        assert result.task_graph.overall_tier.value >= Tier.MULTI_AGENT.value
        assert len(result.task_graph.subtasks) >= 2

    def test_gpt_model_produces_markdown(self):
        """GPT target should produce markdown, not XML."""
        result = self.pipeline.run("chatbot for customer support using GPT")

        assert "gpt" in result.generated_prompt.model_target.lower()
        assert "#" in result.generated_prompt.content  # Markdown headers

    def test_claude_model_produces_xml(self):
        """Claude target should produce XML tags."""
        result = self.pipeline.run("code review agent on Claude")

        assert "claude" in result.generated_prompt.model_target.lower()
        assert "<" in result.generated_prompt.content  # XML tags

    def test_pipeline_passes_gate_for_clean_prompt(self):
        """Clean pipeline output should pass the structural gate."""
        result = self.pipeline.run("customer support agent for fintech on Claude")
        # The stub generator produces clean prompts, so should pass
        assert result.passed_gate is True or result.structural_score.score >= 7.0

    def test_assessment_designed_before_prompt(self):
        """Verify the TDD principle: assessment framework exists and is complete."""
        result = self.pipeline.run("support agent for ecommerce")

        # Assessment framework has content
        assert len(result.eval_framework.test_cases) > 0
        assert result.eval_framework.rubric.dimensions

        # Every test case has required fields
        for tc in result.eval_framework.test_cases:
            assert tc.id
            assert tc.category in ("golden", "adversarial", "edge_case")
            assert tc.expected_behavior
            assert tc.pass_criteria
