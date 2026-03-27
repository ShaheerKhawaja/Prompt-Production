"""Tests for the Complexity Router + all tier specialists."""


from prompt_production.agents.eval_architect import EvalArchitectAgent
from prompt_production.agents.niche_analyzer import NicheAnalyzerAgent
from prompt_production.agents.task_decomposer import TaskDecomposerAgent
from prompt_production.engine.router import ComplexityRouter
from prompt_production.types import NicheProfile, Tier


def _profile_for(request: str) -> NicheProfile:
    return NicheAnalyzerAgent().analyze_request(request)


def _full_pipeline(request: str):
    """Run understand + design_evals, return (profile, graph, framework)."""
    analyzer = NicheAnalyzerAgent()
    decomposer = TaskDecomposerAgent()
    architect = EvalArchitectAgent()

    profile = analyzer.analyze_request(request)
    graph = decomposer.decompose(profile, request)
    framework = architect.design_framework(profile, graph)
    return profile, graph, framework


class TestComplexityRouter:
    def setup_method(self):
        self.router = ComplexityRouter()

    def test_tier1_routes_to_simple(self):
        profile, graph, framework = _full_pipeline("simple one-shot text classifier")
        results = self.router.route(profile, graph, framework)
        assert len(results) == 1
        assert results[0].tier == Tier.SIMPLE
        assert results[0].token_count < 700

    def test_tier2_routes_to_moderate(self):
        profile, graph, framework = _full_pipeline("chatbot for answering general questions")
        # Force tier 2
        graph.overall_tier = Tier.MODERATE
        results = self.router.route(profile, graph, framework)
        assert len(results) == 1
        assert results[0].tier == Tier.MODERATE

    def test_tier3_routes_to_complex(self):
        profile, graph, framework = _full_pipeline("customer support agent with API tool access on Claude")
        graph.overall_tier = Tier.COMPLEX
        results = self.router.route(profile, graph, framework)
        assert len(results) == 1
        assert results[0].tier == Tier.COMPLEX
        assert "<" in results[0].content  # XML for Claude

    def test_tier4_routes_to_multiagent(self):
        profile, graph, framework = _full_pipeline("multi-agent squad with orchestrator for marketing")
        graph.overall_tier = Tier.MULTI_AGENT
        results = self.router.route(profile, graph, framework)
        assert len(results) >= 2  # Orchestrator + at least 1 specialist
        roles = [r.metadata.get("agent_role") for r in results]
        assert "orchestrator" in roles

    def test_tier5_routes_to_context_architect(self):
        profile, graph, framework = _full_pipeline("complete architecture for fintech support system")
        graph.overall_tier = Tier.FULL_ARCHITECTURE
        results = self.router.route(profile, graph, framework)
        assert len(results) == 1
        assert results[0].tier == Tier.FULL_ARCHITECTURE
        assert "token_budget" in results[0].content.lower()
        assert "knowledge_base" in results[0].content.lower()
        assert "monitoring" in results[0].content.lower()

    def test_claude_gets_xml(self):
        profile, graph, framework = _full_pipeline("support agent on Claude")
        graph.overall_tier = Tier.SIMPLE
        results = self.router.route(profile, graph, framework)
        assert "<role>" in results[0].content or "<" in results[0].content

    def test_gpt_gets_markdown(self):
        profile, graph, framework = _full_pipeline("support agent using GPT")
        graph.overall_tier = Tier.SIMPLE
        results = self.router.route(profile, graph, framework)
        assert "#" in results[0].content

    def test_all_prompts_have_techniques(self):
        for request in [
            "simple classifier",
            "chatbot for general questions",
            "fintech support with tools on Claude",
            "multi-agent squad for marketing",
            "complete fintech architecture with knowledge base",
        ]:
            profile, graph, framework = _full_pipeline(request)
            results = self.router.route(profile, graph, framework)
            for r in results:
                assert len(r.techniques_used) > 0, f"No techniques for: {request}"
                assert len(r.techniques_used) <= 4, f"Over-composed for: {request}"

    def test_multiagent_has_handoff_schema(self):
        profile, graph, framework = _full_pipeline("multi-agent squad orchestrator")
        graph.overall_tier = Tier.MULTI_AGENT
        results = self.router.route(profile, graph, framework)
        orchestrator = [r for r in results if r.metadata.get("agent_role") == "orchestrator"]
        assert len(orchestrator) == 1
        assert "handoff" in orchestrator[0].content.lower()

    def test_context_architect_has_compression(self):
        profile, graph, framework = _full_pipeline("full architecture system")
        graph.overall_tier = Tier.FULL_ARCHITECTURE
        results = self.router.route(profile, graph, framework)
        assert "compression" in results[0].content.lower()
