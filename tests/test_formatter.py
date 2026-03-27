"""Tests for the DeliveryFormatter."""

from prompt_production.formatter import DeliveryFormatter
from prompt_production.pipeline import Pipeline


class TestDeliveryFormatter:
    def setup_method(self):
        self.pipeline = Pipeline()
        self.formatter = DeliveryFormatter()

    def test_fintech_output_has_all_sections(self):
        result = self.pipeline.run("customer support agent for fintech on Claude")
        output = self.formatter.format(result)

        assert "# Prompt Production Output" in output
        assert "Domain:" in output
        assert "Tier:" in output
        assert "Techniques Selected" in output
        assert "Generated Prompt" in output
        assert "Eval Suite" in output
        assert "Test Results" in output
        assert "Failure Modes" in output
        assert "Compliance" in output  # fintech has PCI-DSS
        assert "```" in output  # Code block for prompt content

    def test_simple_tier_output_is_shorter(self):
        simple = self.pipeline.run("simple text classifier")
        complex_result = self.pipeline.run("fintech support agent on Claude")
        simple_out = self.formatter.format(simple)
        complex_out = self.formatter.format(complex_result)
        # Simple should produce less output than complex
        assert len(simple_out) < len(complex_out)

    def test_multi_agent_shows_multiple_prompts(self):
        result = self.pipeline.run("multi-agent squad orchestrator for marketing")
        output = self.formatter.format(result)
        assert "Prompts" in output  # Plural
        assert "orchestrator" in output.lower()

    def test_output_is_valid_markdown(self):
        result = self.pipeline.run("support chatbot for ecommerce")
        output = self.formatter.format(result)
        # Basic markdown structure checks
        assert output.startswith("#")
        assert "##" in output
        assert "|" in output  # Tables present
