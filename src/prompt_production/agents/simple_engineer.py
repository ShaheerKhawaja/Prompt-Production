"""Agent 4: Simple Prompt Engineer (Tier 1).

Generates focused ~500 token prompts: role + rules + output format.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import EvalFramework, GeneratedPrompt, NicheProfile, TaskGraph, Tier

AGENT_CONFIG = AgentConfig(
    name="simple_engineer",
    agent_number=4,
    description="Generates simple Tier 1 prompts (~500 tokens)",
    phase="generate",
    tier_scope=1,
    model="claude-sonnet-4.6",
    stakes="low",
)


class SimpleEngineerAgent(BaseAgent):
    """Agent 4: Simple Prompt Engineer."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def generate(self, profile: NicheProfile, graph: TaskGraph, framework: EvalFramework) -> GeneratedPrompt:
        domain = profile.domain.replace("/", " ")
        model = profile.model_recommendation

        if "claude" in model.lower():
            content = self._build_xml(domain, profile)
        else:
            content = self._build_markdown(domain, profile)

        return GeneratedPrompt(
            content=content,
            tier=Tier.SIMPLE,
            model_target=model,
            token_count=len(content.split()),
            techniques_used=["direct_instruction"],
            version="1.0.0",
        )

    def _build_xml(self, domain: str, profile: NicheProfile) -> str:
        lines = [
            f"<role>You {domain}. Respond accurately and concisely.</role>",
            "<rules>",
            "  1. Stay within your defined scope.",
            "  2. If uncertain, say so rather than guessing.",
            "  3. Keep responses focused and direct.",
        ]
        if profile.constraints:
            for c in profile.constraints:
                lines.append(f"  - {c.replace('_', ' ').title()}")
        lines.append("</rules>")
        lines.append("<output>Respond in plain text unless a specific format is requested.</output>")
        return "\n".join(lines)

    def _build_markdown(self, domain: str, profile: NicheProfile) -> str:
        lines = [
            f"# Role\nYou {domain}. Respond accurately and concisely.\n",
            "## Rules",
            "1. Stay within your defined scope.",
            "2. If uncertain, say so rather than guessing.",
            "3. Keep responses focused and direct.",
        ]
        if profile.constraints:
            for c in profile.constraints:
                lines.append(f"- {c.replace('_', ' ').title()}")
        lines.append("\n## Output\nRespond in plain text unless a specific format is requested.")
        return "\n".join(lines)

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        profile = NicheProfile(**input_data["niche_profile"])
        graph = TaskGraph(**input_data["task_graph"])
        framework = EvalFramework(**input_data["eval_framework"])
        result = self.generate(profile, graph, framework)
        return result.model_dump()
