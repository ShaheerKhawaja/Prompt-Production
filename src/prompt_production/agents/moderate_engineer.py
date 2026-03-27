"""Agent 5: Moderate Workflow Engineer (Tier 2).

Generates phase-based conversation prompts ~1,500 tokens.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import EvalFramework, GeneratedPrompt, NicheProfile, TaskGraph, Tier

AGENT_CONFIG = AgentConfig(
    name="moderate_engineer",
    agent_number=5,
    description="Generates Tier 2 workflow prompts (~1500 tokens)",
    phase="generate",
    tier_scope=2,
    model="claude-sonnet-4.6",
    stakes="medium",
)


class ModerateEngineerAgent(BaseAgent):
    """Agent 5: Moderate Workflow Engineer."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def generate(self, profile: NicheProfile, graph: TaskGraph, framework: EvalFramework) -> GeneratedPrompt:
        domain = profile.domain.replace("/", " ")
        model = profile.model_recommendation

        if "claude" in model.lower():
            content = self._build_xml(domain, profile, graph)
        else:
            content = self._build_markdown(domain, profile, graph)

        techniques = graph.subtasks[0].technique_candidates[:3] if graph.subtasks else ["phase_flow"]

        return GeneratedPrompt(
            content=content,
            tier=Tier.MODERATE,
            model_target=model,
            token_count=len(content.split()),
            techniques_used=techniques,
            version="1.0.0",
        )

    def _build_xml(self, domain: str, profile: NicheProfile, graph: TaskGraph) -> str:
        lines = [f"<role>You handle {domain} conversations through a structured process.</role>"]

        lines.append("<process>")
        lines.append("  Phase 1: GREET")
        lines.append("    Introduce yourself. Identify the user's need in 1-2 questions.")
        lines.append("  Phase 2: GATHER")
        lines.append("    Collect necessary information. Ask focused questions, one at a time.")
        lines.append("  Phase 3: RESOLVE")
        lines.append("    Address the user's need based on gathered information.")
        lines.append("    If you cannot resolve, explain why and offer alternatives.")
        lines.append("  Phase 4: CONFIRM")
        lines.append("    Verify the user is satisfied. Ask if there is anything else.")
        lines.append("  Phase 5: CLOSE")
        lines.append("    Summarize what was done. End professionally.")
        lines.append("</process>")

        lines.append("<rules>")
        lines.append("  ALWAYS: Ask one question at a time.")
        lines.append("  ALWAYS: Confirm understanding before acting.")
        lines.append("  NEVER: Make assumptions about the user's intent.")
        lines.append("  NEVER: Skip the confirmation phase.")
        if profile.constraints:
            for c in profile.constraints:
                lines.append(f"  - {c.replace('_', ' ').title()}")
        lines.append("</rules>")

        if profile.domain_antipatterns:
            lines.append("<avoid>")
            for ap in profile.domain_antipatterns[:3]:
                lines.append(f"  - {ap.replace('_', ' ')}")
            lines.append("</avoid>")

        return "\n".join(lines)

    def _build_markdown(self, domain: str, profile: NicheProfile, graph: TaskGraph) -> str:
        lines = [f"# Role\nYou handle {domain} conversations through a structured process.\n"]

        lines.append("## Process")
        lines.append("1. **GREET**: Introduce yourself. Identify the user's need.")
        lines.append("2. **GATHER**: Collect information. One question at a time.")
        lines.append("3. **RESOLVE**: Address the need. If unable, explain why.")
        lines.append("4. **CONFIRM**: Verify satisfaction. Ask if anything else needed.")
        lines.append("5. **CLOSE**: Summarize and end professionally.")

        lines.append("\n## Rules")
        lines.append("- ALWAYS: Ask one question at a time.")
        lines.append("- ALWAYS: Confirm understanding before acting.")
        lines.append("- NEVER: Make assumptions about intent.")
        lines.append("- NEVER: Skip confirmation.")

        if profile.domain_antipatterns:
            lines.append("\n## Avoid")
            for ap in profile.domain_antipatterns[:3]:
                lines.append(f"- {ap.replace('_', ' ')}")

        return "\n".join(lines)

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        profile = NicheProfile(**input_data["niche_profile"])
        graph = TaskGraph(**input_data["task_graph"])
        framework = EvalFramework(**input_data["eval_framework"])
        result = self.generate(profile, graph, framework)
        return result.model_dump()
