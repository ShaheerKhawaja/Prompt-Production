"""Tests for Agent 1: Niche Analyzer."""

from prompt_production.agents.niche_analyzer import NicheAnalyzerAgent
from prompt_production.types import Approach, Tier


class TestNicheAnalyzerAgent:
    def setup_method(self):
        self.agent = NicheAnalyzerAgent()

    def test_fintech_support(self):
        profile = self.agent.analyze_request("customer support agent for fintech on Claude")
        assert "fintech" in profile.domain
        assert "PCI-DSS" in profile.compliance_requirements
        assert "claude" in profile.model_recommendation.lower()

    def test_simple_chatbot(self):
        profile = self.agent.analyze_request("simple one-shot classifier for text")
        assert profile.tier_hint == Tier.SIMPLE
        assert profile.approach == Approach.PROMPT_ENGINEER

    def test_multi_agent_system(self):
        profile = self.agent.analyze_request("multi-agent squad with orchestrator for marketing")
        assert profile.approach == Approach.CONTEXT_ENGINEER
        assert profile.tier_hint.value >= Tier.MULTI_AGENT.value

    def test_voice_agent(self):
        profile = self.agent.analyze_request("voice agent for phone-based customer support on Vapi")
        assert profile.deployment_target == "vapi"
        assert "haiku" in profile.model_recommendation.lower()

    def test_healthcare_compliance(self):
        profile = self.agent.analyze_request("patient intake agent for healthcare clinic")
        assert "HIPAA" in profile.compliance_requirements

    def test_code_review_agent(self):
        profile = self.agent.analyze_request("code review agent for Python with API tool access")
        assert "code" in profile.domain
        assert "hallucinated_apis" in profile.domain_antipatterns

    def test_gpt_model_detection(self):
        profile = self.agent.analyze_request("chatbot using GPT for ecommerce support")
        assert "gpt" in profile.model_recommendation.lower()

    def test_always_returns_antipatterns(self):
        profile = self.agent.analyze_request("anything at all")
        assert len(profile.domain_antipatterns) > 0

    def test_confidence_in_range(self):
        profile = self.agent.analyze_request("anything")
        assert 0.0 <= profile.confidence <= 1.0

    def test_unknown_domain_defaults(self):
        profile = self.agent.analyze_request("something completely novel and unique")
        assert profile.domain == "general/general"
        assert len(profile.domain_antipatterns) > 0

    def test_escalation_constraint(self):
        profile = self.agent.analyze_request("support agent that can escalate to human")
        assert "escalation_required" in profile.constraints

    def test_multilingual_constraint(self):
        profile = self.agent.analyze_request("multilingual support agent for Spanish and French")
        assert "multilingual" in profile.constraints
