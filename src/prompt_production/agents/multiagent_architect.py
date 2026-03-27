"""Agent 7: Multi-Agent Systems Architect (Tier 4).

Designs squad architectures with orchestrator + specialist prompts + handoff schemas.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import EvalFramework, GeneratedPrompt, NicheProfile, TaskGraph, Tier

AGENT_CONFIG = AgentConfig(
    name="multiagent_architect",
    agent_number=7,
    description="Designs multi-agent squad architectures (Tier 4)",
    phase="generate",
    tier_scope=4,
    model="claude-opus-4.6",
    stakes="high",
)


class MultiAgentArchitectAgent(BaseAgent):
    """Agent 7: Multi-Agent Systems Architect."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def generate(self, profile: NicheProfile, graph: TaskGraph, framework: EvalFramework) -> list[GeneratedPrompt]:
        """Generate multiple prompts for a multi-agent system."""
        domain = profile.domain.replace("/", " ")
        model = profile.model_recommendation
        prompts: list[GeneratedPrompt] = []

        # Orchestrator prompt
        orchestrator = self._build_orchestrator(domain, profile, graph, model)
        prompts.append(orchestrator)

        # Specialist prompts from subtasks
        for st in graph.subtasks:
            if "orchestrator" not in st.description.lower():
                specialist = self._build_specialist(st.description, st.id, profile, model)
                prompts.append(specialist)

        return prompts

    def _build_orchestrator(self, domain: str, profile: NicheProfile, graph: TaskGraph, model: str) -> GeneratedPrompt:
        lines = [f"<role>You orchestrate the {domain} agent squad.</role>"]

        lines.append("<delegation>")
        for st in graph.subtasks:
            if "orchestrator" not in st.description.lower():
                lines.append(f"  - Agent {st.id}: {st.description}")
        lines.append("</delegation>")

        lines.append("<routing>")
        lines.append("  For each user request:")
        lines.append("  1. Classify the request type")
        lines.append("  2. Route to the appropriate specialist agent")
        lines.append("  3. Monitor the specialist's response")
        lines.append("  4. Synthesize results if multiple agents involved")
        lines.append("  5. Deliver the final response to the user")
        lines.append("</routing>")

        lines.append("<handoff_schema>")
        lines.append('  {"from": "orchestrator", "to": "agent_id",')
        lines.append('   "context": "user request summary",')
        lines.append('   "instructions": "specific task for specialist",')
        lines.append('   "return_format": "expected response structure"}')
        lines.append("</handoff_schema>")

        lines.append("<rules>")
        lines.append("  NEVER: Attempt to handle specialist tasks directly.")
        lines.append("  ALWAYS: Pass full context when delegating.")
        lines.append("  ALWAYS: Verify specialist response before delivering to user.")
        lines.append("</rules>")

        content = "\n".join(lines)
        return GeneratedPrompt(
            content=content,
            tier=Tier.MULTI_AGENT,
            model_target=model,
            token_count=len(content.split()),
            techniques_used=["peer", "graph_of_thoughts", "handoff_schemas"],
            version="1.0.0",
            metadata={"agent_role": "orchestrator"},
        )

    def _build_specialist(self, description: str, agent_id: str, profile: NicheProfile, model: str) -> GeneratedPrompt:
        lines = [
            f"<role>You are specialist agent {agent_id}: {description}.</role>",
            "<scope>",
            f"  You ONLY handle: {description}",
            "  For anything outside your scope, return to the orchestrator.",
            "</scope>",
            "<process>",
            "  1. Receive task from orchestrator with context",
            f"  2. Execute: {description}",
            "  3. Return structured result to orchestrator",
            "</process>",
        ]

        if profile.constraints:
            lines.append("<constraints>")
            for c in profile.constraints:
                lines.append(f"  - {c.replace('_', ' ').title()}")
            lines.append("</constraints>")

        content = "\n".join(lines)
        return GeneratedPrompt(
            content=content,
            tier=Tier.COMPLEX,
            model_target=model,
            token_count=len(content.split()),
            techniques_used=["react", "constitutional_ai"],
            version="1.0.0",
            metadata={"agent_role": "specialist", "agent_id": agent_id},
        )

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        profile = NicheProfile(**input_data["niche_profile"])
        graph = TaskGraph(**input_data["task_graph"])
        framework = EvalFramework(**input_data["eval_framework"])
        results = self.generate(profile, graph, framework)
        return {"prompts": [r.model_dump() for r in results]}
