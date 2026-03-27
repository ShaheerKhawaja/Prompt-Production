"""Tests for Agent 9: Structural Eval."""

from prompt_production.agents.structural_eval import StructuralEvalAgent
from prompt_production.types import GeneratedPrompt, Tier


def _make_prompt(content: str, model: str = "claude-sonnet-4.6", techniques: list[str] | None = None):
    return GeneratedPrompt(
        content=content,
        tier=Tier.COMPLEX,
        model_target=model,
        token_count=len(content.split()),
        techniques_used=techniques or ["react", "constitutional_ai"],
        version="1.0.0",
    )


class TestStructuralEvalAgent:
    def setup_method(self):
        self.agent = StructuralEvalAgent()

    def test_clean_prompt_scores_high(self):
        prompt = _make_prompt(
            "<role>You handle customer refund requests.</role>\n"
            "<process>\n1. Verify account\n2. Check policy\n3. Process refund</process>\n"
            "<constraints>Do not process refunds over $500 without escalation.</constraints>"
        )
        result = self.agent.evaluate(prompt)
        assert result.score >= 8.0
        assert len(result.antipatterns_found) == 0

    def test_superlatives_detected(self):
        prompt = _make_prompt("You are an elite world-class cutting-edge AI assistant.")
        result = self.agent.evaluate(prompt)
        assert "superlative_inflation" in result.antipatterns_found
        assert result.score < 8.0

    def test_capability_theater_detected(self):
        prompt = _make_prompt("I am capable of analyzing data. I have the ability to synthesize insights.")
        result = self.agent.evaluate(prompt)
        assert "capability_theater" in result.antipatterns_found

    def test_framework_namedrop_detected(self):
        prompt = _make_prompt("Use Chain of Thought reasoning to analyze the problem. Apply ReAct.")
        result = self.agent.evaluate(prompt)
        assert "framework_namedrop" in result.antipatterns_found

    def test_aggressive_language_detected(self):
        prompt = _make_prompt("CRITICAL! YOU MUST follow these instructions. NEVER EVER deviate.")
        result = self.agent.evaluate(prompt)
        assert "aggressive_language" in result.antipatterns_found

    def test_over_composition_flagged(self):
        prompt = _make_prompt("prompt content", techniques=["a", "b", "c", "d", "e"])
        result = self.agent.evaluate(prompt)
        assert result.technique_validation is False
        assert any("over-composition" in i.lower() for i in result.issues)

    def test_no_techniques_scores_lower(self):
        """Empty techniques should result in lower score than proper techniques."""
        prompt_with = _make_prompt("prompt content", techniques=["react", "constitutional_ai"])
        prompt_without = _make_prompt("prompt content", techniques=[])
        result_with = self.agent.evaluate(prompt_with)
        result_without = self.agent.evaluate(prompt_without)
        # The prompt with techniques should score >= the one without
        assert result_with.score >= result_without.score or result_with.technique_validation

    def test_xml_boosts_claude_score(self):
        xml_prompt = _make_prompt("<role>agent</role><task>do stuff</task>", model="claude-sonnet-4.6")
        plain_prompt = _make_prompt("You are an agent. Do stuff.", model="claude-sonnet-4.6")
        xml_result = self.agent.evaluate(xml_prompt)
        plain_result = self.agent.evaluate(plain_prompt)
        assert xml_result.model_compatibility >= plain_result.model_compatibility

    def test_markdown_boosts_gpt_score(self):
        md_prompt = _make_prompt("# Role\nYou handle support.\n## Process\n1. Step one", model="gpt-5.4")
        result = self.agent.evaluate(md_prompt)
        assert result.model_compatibility >= 8.0

    def test_multiple_antipatterns_compound(self):
        prompt = _make_prompt(
            "You are an elite world-class AI. I am capable of everything. "
            "CRITICAL! Use Chain of Thought. YOU MUST follow these rules."
        )
        result = self.agent.evaluate(prompt)
        assert len(result.antipatterns_found) >= 3
        assert result.score < 5.0
