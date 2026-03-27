"""Agent 2: Task Decomposer.

Breaks complex prompt requests into atomic subtasks with dependency graphs.
Assigns tier to each subtask and selects technique candidates.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import NicheProfile, Subtask, TaskGraph, Tier

AGENT_CONFIG = AgentConfig(
    name="task_decomposer",
    agent_number=2,
    description="Breaks requests into atomic subtasks with dependency graphs",
    phase="understand",
    tier_scope=None,
    model="claude-sonnet-4.6",
    stakes="medium",
)

_TECHNIQUE_MAP: dict[str, list[str]] = {
    "conversational": ["phase_flow", "emotion_prompt", "never_always_rules"],
    "tool_using": ["react", "constitutional_ai", "structured_output"],
    "knowledge": ["step_back", "cumulative_reasoning", "chain_of_density"],
    "creative": ["tree_of_thoughts", "self_refine", "emotion_prompt"],
    "multi_agent": ["peer", "graph_of_thoughts", "handoff_schemas"],
    "context_arch": ["step_back", "recursive_summarization", "token_budget"],
    "code": ["self_debugging", "contrastive_cot", "react"],
    "analysis": ["chain_of_thought", "self_consistency", "step_back"],
}


class TaskDecomposerAgent(BaseAgent):
    """Agent 2: Task Decomposer."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def decompose(self, niche_profile: NicheProfile, user_request: str) -> TaskGraph:
        """Decompose a request into a task graph based on the niche profile."""
        tier = niche_profile.tier_hint
        domain_primary = niche_profile.domain.split("/")[0]

        if tier.value <= Tier.MODERATE.value:
            return self._atomic_task(niche_profile, user_request)

        if tier == Tier.COMPLEX:
            return self._complex_decomposition(niche_profile, user_request, domain_primary)

        if tier == Tier.MULTI_AGENT:
            return self._multi_agent_decomposition(niche_profile, user_request, domain_primary)

        return self._full_architecture_decomposition(niche_profile, user_request, domain_primary)

    def _atomic_task(self, profile: NicheProfile, request: str) -> TaskGraph:
        """Tier 1-2: single subtask, no decomposition needed."""
        task_type = self._infer_task_type(request)
        subtask = Subtask(
            id="A",
            description=request,
            tier=profile.tier_hint,
            dependencies=[],
            technique_candidates=self._select_techniques(task_type),
        )
        return TaskGraph(subtasks=[subtask], overall_tier=profile.tier_hint, execution_order=["A"])

    def _complex_decomposition(self, profile: NicheProfile, request: str, domain: str) -> TaskGraph:
        """Tier 3: typically 2-3 subtasks."""
        subtasks = [
            Subtask(
                id="A",
                description=f"Core {domain} conversation handler",
                tier=Tier.COMPLEX,
                dependencies=[],
                technique_candidates=self._select_techniques("tool_using"),
            ),
            Subtask(
                id="B",
                description="Constraint and compliance rules",
                tier=Tier.MODERATE,
                dependencies=[],
                technique_candidates=self._select_techniques("analysis"),
            ),
        ]

        if profile.compliance_requirements:
            subtasks.append(
                Subtask(
                    id="C",
                    description="Compliance verification protocol",
                    tier=Tier.MODERATE,
                    dependencies=["A"],
                    technique_candidates=["constitutional_ai", "never_always_rules"],
                )
            )

        execution_order = self._resolve_order(subtasks)
        return TaskGraph(subtasks=subtasks, overall_tier=Tier.COMPLEX, execution_order=execution_order)

    def _multi_agent_decomposition(self, profile: NicheProfile, request: str, domain: str) -> TaskGraph:
        """Tier 4: orchestrator + specialists."""
        subtasks = [
            Subtask(
                id="A",
                description=f"Orchestrator prompt for {domain} squad",
                tier=Tier.MULTI_AGENT,
                dependencies=["B", "C"],
                technique_candidates=self._select_techniques("multi_agent"),
            ),
            Subtask(
                id="B",
                description=f"Specialist agent 1: primary {domain} handler",
                tier=Tier.COMPLEX,
                dependencies=[],
                technique_candidates=self._select_techniques("tool_using"),
            ),
            Subtask(
                id="C",
                description="Specialist agent 2: escalation/handoff handler",
                tier=Tier.MODERATE,
                dependencies=[],
                technique_candidates=self._select_techniques("conversational"),
            ),
        ]
        execution_order = self._resolve_order(subtasks)
        return TaskGraph(subtasks=subtasks, overall_tier=Tier.MULTI_AGENT, execution_order=execution_order)

    def _full_architecture_decomposition(self, profile: NicheProfile, request: str, domain: str) -> TaskGraph:
        """Tier 5: full context architecture."""
        subtasks = [
            Subtask(
                id="A",
                description="Knowledge base architecture design",
                tier=Tier.FULL_ARCHITECTURE,
                dependencies=[],
                technique_candidates=self._select_techniques("context_arch"),
            ),
            Subtask(
                id="B",
                description=f"Core {domain} system prompt",
                tier=Tier.COMPLEX,
                dependencies=["A"],
                technique_candidates=self._select_techniques("tool_using"),
            ),
            Subtask(
                id="C",
                description="Token budget and context allocation plan",
                tier=Tier.FULL_ARCHITECTURE,
                dependencies=["A", "B"],
                technique_candidates=["token_budget", "recursive_summarization"],
            ),
            Subtask(
                id="D",
                description="Monitoring and alerting specification",
                tier=Tier.MODERATE,
                dependencies=["B"],
                technique_candidates=["step_back", "analysis"],
            ),
        ]
        execution_order = self._resolve_order(subtasks)
        return TaskGraph(subtasks=subtasks, overall_tier=Tier.FULL_ARCHITECTURE, execution_order=execution_order)

    def _infer_task_type(self, request: str) -> str:
        req = request.lower()
        type_keywords = {
            "tool_using": ["tool", "api", "database", "function", "search"],
            "conversational": ["chat", "conversation", "support", "assist"],
            "code": ["code", "programming", "review", "debug"],
            "creative": ["creative", "write", "generate", "design"],
            "knowledge": ["research", "analyze", "summarize", "extract"],
            "multi_agent": ["multi-agent", "squad", "orchestrat", "team"],
        }
        for task_type, keywords in type_keywords.items():
            if any(kw in req for kw in keywords):
                return task_type
        return "conversational"

    def _select_techniques(self, task_type: str) -> list[str]:
        return _TECHNIQUE_MAP.get(task_type, ["chain_of_thought", "self_consistency"])

    def _resolve_order(self, subtasks: list[Subtask]) -> list[str]:
        """Topological sort of subtasks by dependencies."""
        resolved: list[str] = []
        remaining = {s.id: s for s in subtasks}

        while remaining:
            ready = [sid for sid, s in remaining.items() if all(d in resolved for d in s.dependencies)]
            if not ready:
                ready = list(remaining.keys())[:1]
            for sid in sorted(ready):
                resolved.append(sid)
                del remaining[sid]

        return resolved

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        profile = NicheProfile(**input_data["niche_profile"])
        user_request = input_data.get("user_request", "")
        graph = self.decompose(profile, user_request)
        return graph.model_dump()
