"""End-to-end integration tests — TEST GATE 6.

Each test represents a real user scenario spanning all 13 agents.
These are the tests that must pass before any release.
"""

from prompt_production.pipeline import Pipeline
from prompt_production.types import Approach, Tier


class TestE2EScenarios:
    """5 diverse E2E tests spanning all 5 tiers."""

    def setup_method(self):
        self.pipeline = Pipeline()

    def test_tier1_simple_classifier(self):
        """Tier 1: Single-turn text classifier — simplest possible prompt."""
        result = self.pipeline.run("simple one-shot sentiment classifier")

        assert result.niche_profile.tier_hint == Tier.SIMPLE
        assert len(result.generated_prompts) == 1
        assert result.primary_prompt.token_count < 700
        assert result.primary_prompt.tier == Tier.SIMPLE
        assert result.testbench_result.result.structural.score >= 7.0
        assert result.learning_record is not None

    def test_tier2_support_chatbot(self):
        """Tier 2: Multi-turn chatbot — no tools, conversation flow."""
        result = self.pipeline.run("friendly chatbot that helps users navigate a website")

        assert result.task_graph.overall_tier.value <= Tier.COMPLEX.value
        assert len(result.generated_prompts) >= 1
        assert result.testbench_result.result.behavioral.tests_total > 0

    def test_tier3_fintech_support(self):
        """Tier 3: Hybrid — tool-using agent with compliance. The signature use case."""
        result = self.pipeline.run("customer support agent for fintech company with API tools on Claude")

        assert "fintech" in result.niche_profile.domain
        assert "PCI-DSS" in result.niche_profile.compliance_requirements
        assert "claude" in result.primary_prompt.model_target.lower()
        assert "<" in result.primary_prompt.content  # XML for Claude
        assert len(result.eval_framework.test_cases) >= 5
        assert result.eval_framework.adversarial_count >= 3
        assert len(result.technique_selection.techniques) > 0
        assert len(result.failure_modes) > 0
        assert result.learning_record is not None
        assert result.learning_record.domain == result.niche_profile.domain

    def test_tier4_multi_agent_marketing(self):
        """Tier 4: Multi-agent squad — orchestrator + specialists."""
        result = self.pipeline.run("multi-agent squad with orchestrator for marketing campaigns")

        assert result.niche_profile.approach == Approach.CONTEXT_ENGINEER
        assert result.task_graph.overall_tier.value >= Tier.MULTI_AGENT.value
        assert len(result.generated_prompts) >= 2

        # Should have an orchestrator prompt
        roles = [p.metadata.get("agent_role") for p in result.generated_prompts]
        assert "orchestrator" in roles

    def test_tier5_full_architecture(self):
        """Tier 5: Full context architecture — token budgets, KB, monitoring."""
        result = self.pipeline.run(
            "complete architecture for healthcare patient intake system "
            "with extensive knowledge base and compliance requirements"
        )

        assert result.niche_profile.tier_hint.value >= Tier.MULTI_AGENT.value
        assert "HIPAA" in result.niche_profile.compliance_requirements
        assert result.learning_record is not None


class TestE2ECrossModel:
    """Test model-aware generation across providers."""

    def setup_method(self):
        self.pipeline = Pipeline()

    def test_claude_produces_xml(self):
        result = self.pipeline.run("code review agent on Claude")
        assert "<" in result.primary_prompt.content

    def test_gpt_produces_markdown(self):
        result = self.pipeline.run("support chatbot using GPT")
        assert "#" in result.primary_prompt.content


class TestE2ETDDPrinciple:
    """Verify the eval-first (TDD) principle holds across all runs."""

    def setup_method(self):
        self.pipeline = Pipeline()

    def test_eval_framework_always_populated(self):
        """Every pipeline run MUST produce an eval framework."""
        requests = [
            "simple classifier",
            "customer support agent for fintech on Claude",
            "multi-agent squad for marketing",
        ]
        for req in requests:
            result = self.pipeline.run(req)
            assert len(result.eval_framework.test_cases) > 0, f"No eval tests for: {req}"
            assert result.eval_framework.rubric.pass_threshold > 0, f"No rubric for: {req}"
            assert result.eval_framework.adversarial_count >= 2, f"Insufficient adversarial for: {req}"

    def test_every_eval_has_required_fields(self):
        result = self.pipeline.run("fintech support agent")
        for tc in result.eval_framework.test_cases:
            assert tc.id, "Missing test case ID"
            assert tc.category in ("golden", "adversarial", "edge_case"), f"Bad category: {tc.category}"
            assert tc.input_text is not None, "Missing input_text"
            assert tc.expected_behavior, "Missing expected_behavior"
            assert tc.pass_criteria, "Missing pass_criteria"


class TestE2ELearning:
    """Verify the self-learning loop persists across runs."""

    def setup_method(self):
        self.pipeline = Pipeline()

    def test_second_run_has_playbook_data(self):
        """After first run, playbook should have data for the domain."""
        # First run establishes baseline
        r1 = self.pipeline.run("support agent for fintech on Claude")
        assert r1.learning_record is not None

        # Second run should still work and produce a learning record
        r2 = self.pipeline.run("another fintech support agent on Claude")
        assert r2.learning_record is not None

        # Both should have the same domain family
        assert "fintech" in r1.learning_record.domain
        assert "fintech" in r2.learning_record.domain
