"""Agent 6: Complex Agent Engineer (Tier 3).

Generates hybrid prompts for tool-using agents ~2,500 tokens.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import EvalFramework, GeneratedPrompt, NicheProfile, TaskGraph, Tier

AGENT_CONFIG = AgentConfig(
    name="complex_engineer",
    agent_number=6,
    description="Generates Tier 3 hybrid prompts for tool-using agents (~2500 tokens)",
    phase="generate",
    tier_scope=3,
    model="claude-sonnet-4.6",
    stakes="high",
)


class ComplexEngineerAgent(BaseAgent):
    """Agent 6: Complex Agent Engineer."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def generate(self, profile: NicheProfile, graph: TaskGraph, framework: EvalFramework) -> GeneratedPrompt:
        domain = profile.domain.replace("/", " ")
        model = profile.model_recommendation

        if "claude" in model.lower():
            content = self._build_xml(domain, profile, graph)
        else:
            content = self._build_markdown(domain, profile, graph)

        techniques = []
        for st in graph.subtasks:
            techniques.extend(st.technique_candidates[:2])
        techniques = list(dict.fromkeys(techniques))[:4]

        return GeneratedPrompt(
            content=content,
            tier=Tier.COMPLEX,
            model_target=model,
            token_count=len(content.split()),
            techniques_used=techniques or ["react", "constitutional_ai"],
            version="1.0.0",
        )

    def _build_xml(self, domain: str, profile: NicheProfile, graph: TaskGraph) -> str:
        lines = [f"<role>You handle {domain} requests using available tools.</role>"]

        # Process from subtasks
        lines.append("<process>")
        for i, st in enumerate(graph.subtasks, 1):
            lines.append(f"  {i}. {st.description}")
        lines.append("</process>")

        # Tool usage protocol
        lines.append("<tool_usage>")
        lines.append("  For each user request:")
        lines.append("  1. Determine if a tool call is needed")
        lines.append("  2. Call the appropriate tool with correct parameters")
        lines.append("  3. Interpret the tool response")
        lines.append("  4. Format the result for the user")
        lines.append("  If a tool call fails, inform the user and offer alternatives.")
        lines.append("</tool_usage>")

        # Constraints
        lines.append("<constraints>")
        for c in profile.constraints:
            lines.append(f"  - {c.replace('_', ' ').title()}")
        if profile.compliance_requirements:
            for cr in profile.compliance_requirements:
                lines.append(f"  - Comply with {cr}")
        lines.append("  NEVER: Fabricate data that should come from tools.")
        lines.append("  NEVER: Call tools without verifying required parameters.")
        lines.append("  ALWAYS: Confirm sensitive actions before executing.")
        lines.append("</constraints>")

        # Anti-patterns
        if profile.domain_antipatterns:
            lines.append("<avoid>")
            for ap in profile.domain_antipatterns:
                lines.append(f"  - {ap.replace('_', ' ')}")
            lines.append("</avoid>")

        return "\n".join(lines)

    def _build_markdown(self, domain: str, profile: NicheProfile, graph: TaskGraph) -> str:
        lines = [f"# Role\nYou handle {domain} requests using available tools.\n"]

        lines.append("## Process")
        for i, st in enumerate(graph.subtasks, 1):
            lines.append(f"{i}. {st.description}")

        lines.append("\n## Tool Usage")
        lines.append("1. Determine if a tool call is needed")
        lines.append("2. Call the appropriate tool with correct parameters")
        lines.append("3. Interpret the tool response")
        lines.append("4. Format the result for the user")
        lines.append("If a tool call fails, inform the user and offer alternatives.")

        lines.append("\n## Constraints")
        for c in profile.constraints:
            lines.append(f"- {c.replace('_', ' ').title()}")
        lines.append("- NEVER: Fabricate data that should come from tools.")
        lines.append("- ALWAYS: Confirm sensitive actions before executing.")

        if profile.domain_antipatterns:
            lines.append("\n## Avoid")
            for ap in profile.domain_antipatterns:
                lines.append(f"- {ap.replace('_', ' ')}")

        return "\n".join(lines)

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        profile = NicheProfile(**input_data["niche_profile"])
        graph = TaskGraph(**input_data["task_graph"])
        framework = EvalFramework(**input_data["eval_framework"])
        result = self.generate(profile, graph, framework)
        return result.model_dump()
