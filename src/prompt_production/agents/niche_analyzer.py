"""Agent 1: Niche Analyzer.

Analyzes domain, constraints, model ecosystem, and deployment target.
Runs the Nuance Engine to determine tier and approach.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.engine.nuance import NuanceEngine, NuanceInput
from prompt_production.types import NicheProfile

AGENT_CONFIG = AgentConfig(
    name="niche_analyzer",
    agent_number=1,
    description="Analyzes domain, constraints, model ecosystem, deployment target",
    phase="understand",
    tier_scope=None,
    model="claude-sonnet-4.6",
    stakes="medium",
)

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "fintech": ["fintech", "banking", "payment", "financial", "finance"],
    "healthcare": ["health", "medical", "patient", "clinical", "hospital"],
    "ecommerce": ["ecommerce", "shop", "retail", "product", "store"],
    "saas": ["saas", "software", "platform", "dashboard", "app"],
    "support": ["support", "customer service", "help desk", "helpdesk"],
    "code": ["code", "programming", "developer", "engineering", "review"],
    "marketing": ["marketing", "seo", "content", "campaign", "ads"],
    "legal": ["legal", "law", "attorney", "compliance", "contract"],
    "education": ["education", "tutor", "learn", "teach", "course"],
}

_DOMAIN_ANTIPATTERNS: dict[str, list[str]] = {
    "fintech": ["policy_hallucination", "compliance_drift", "escalation_gaps", "balance_fabrication"],
    "healthcare": ["medical_advice_liability", "phi_exposure", "empathy_deficit", "diagnosis_hallucination"],
    "ecommerce": ["inventory_hallucination", "pricing_errors", "return_policy_drift"],
    "saas": ["feature_hallucination", "outdated_docs", "scope_creep"],
    "support": ["repetitive_responses", "premature_escalation", "context_loss", "tone_mismatch"],
    "code": ["hallucinated_apis", "untested_suggestions", "security_blind_spots", "deprecated_patterns"],
    "marketing": ["metric_fabrication", "strategy_hallucination", "brand_voice_drift"],
    "legal": ["legal_advice_liability", "jurisdiction_errors", "precedent_fabrication"],
    "education": ["incorrect_explanations", "difficulty_mismatch", "assumed_prerequisites"],
}

_COMPLIANCE_MAP: dict[str, list[str]] = {
    "PCI-DSS": ["pci", "payment card", "credit card", "fintech", "banking", "financial"],
    "HIPAA": ["hipaa", "phi", "protected health", "health", "medical", "patient"],
    "SOC2": ["soc2", "soc 2"],
    "GDPR": ["gdpr", "data protection", "eu", "european"],
}

_TOOL_INDICATORS = ["api", "database", "search", "lookup", "tool", "function", "webhook", "endpoint"]


class NicheAnalyzerAgent(BaseAgent):
    """Agent 1: Niche Analyzer."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)
        self.nuance_engine = NuanceEngine()

    def analyze_request(self, user_request: str) -> NicheProfile:
        """Analyze a user request and produce a NicheProfile."""
        req = user_request.lower()

        domain = self._classify_domain(req)
        constraints = self._discover_constraints(req)
        compliance = self._detect_compliance(req)
        deployment = self._detect_deployment(req)
        model_rec = self._recommend_model(req, deployment)
        nuance_input = self._build_nuance_input(req, compliance)
        nuance_result = self.nuance_engine.analyze(nuance_input)

        return NicheProfile(
            domain=domain,
            model_recommendation=model_rec,
            tier_hint=nuance_result.tier,
            approach=nuance_result.approach,
            constraints=constraints,
            domain_antipatterns=self._get_antipatterns(domain),
            compliance_requirements=compliance,
            deployment_target=deployment,
            confidence=0.8,
        )

    def _classify_domain(self, request: str) -> str:
        for domain, keywords in _DOMAIN_KEYWORDS.items():
            if any(kw in request for kw in keywords):
                subdomain = "general"
                for sub_kw in ["support", "onboarding", "intake", "review", "analysis", "generation"]:
                    if sub_kw in request:
                        subdomain = sub_kw
                        break
                return f"{domain}/{subdomain}"
        return "general/general"

    def _discover_constraints(self, request: str) -> list[str]:
        constraints: list[str] = []
        constraint_map = {
            "formal_tone": ["formal", "professional", "enterprise", "corporate"],
            "friendly_tone": ["friendly", "casual", "conversational", "warm"],
            "escalation_required": ["escalat", "transfer", "human", "handoff"],
            "voice_optimized": ["voice", "phone", "call", "speak"],
            "low_latency": ["fast", "real-time", "realtime", "instant"],
            "multilingual": ["multilingual", "language", "translate", "spanish", "french"],
        }
        for constraint, keywords in constraint_map.items():
            if any(kw in request for kw in keywords):
                constraints.append(constraint)
        return constraints

    def _detect_compliance(self, request: str) -> list[str]:
        found: set[str] = set()
        for standard, keywords in _COMPLIANCE_MAP.items():
            if any(kw in request for kw in keywords):
                found.add(standard)
        return sorted(found)

    def _detect_deployment(self, request: str) -> str:
        targets = {
            "vapi": ["vapi", "voice ai"],
            "claude_project": ["claude project"],
            "cassidy": ["cassidy"],
            "langgraph": ["langchain", "langgraph", "langsmith"],
            "chatgpt": ["chatgpt", "gpt project", "custom gpt"],
        }
        for target, keywords in targets.items():
            if any(kw in request for kw in keywords):
                return target
        return "api"

    def _recommend_model(self, request: str, deployment: str) -> str:
        if deployment == "vapi":
            return "claude-haiku-4.5"
        model_hints = {
            "claude-opus-4.6": ["opus", "highest quality", "best model"],
            "claude-sonnet-4.6": ["claude", "sonnet"],
            "gpt-5.4": ["gpt", "openai"],
            "gemini-3-pro": ["gemini", "google"],
        }
        for model, keywords in model_hints.items():
            if any(kw in request for kw in keywords):
                return model
        return "claude-sonnet-4.6"

    def _build_nuance_input(self, request: str, compliance: list[str]) -> NuanceInput:
        turns = "multi"
        if any(w in request for w in ["single", "one-shot", "summarize", "classify", "extract"]):
            turns = "single"
        if any(w in request for w in ["orchestrat", "coordinate", "manage agents", "squad"]):
            turns = "orchestrates"

        tools = sum(1 for w in _TOOL_INDICATORS if w in request)

        knowledge = "training_data"
        if any(w in request for w in ["knowledge base", "documentation", "faq", "docs"]):
            knowledge = "few_docs"
        if any(w in request for w in ["extensive", "large corpus", "100+", "thousands"]):
            knowledge = "extensive"

        multi_agent = any(w in request for w in ["multi-agent", "squad", "team of agents", "orchestrat"])

        return NuanceInput(
            turns=turns,
            tools=tools,
            compliance=bool(compliance),
            knowledge_depth=knowledge,
            multi_agent=multi_agent,
        )

    def _get_antipatterns(self, domain: str) -> list[str]:
        primary = domain.split("/")[0]
        return _DOMAIN_ANTIPATTERNS.get(primary, ["generic_hallucination", "context_loss", "scope_creep"])

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        user_request = input_data.get("user_request", "")
        profile = self.analyze_request(user_request)
        return profile.model_dump()
