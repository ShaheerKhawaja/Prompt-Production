"""Agent 8: Context Architecture Designer (Tier 5).

Designs complete context architectures: token budgets, KB structures,
compression strategies, monitoring plans.
"""

from __future__ import annotations

from typing import Any

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import EvalFramework, GeneratedPrompt, NicheProfile, TaskGraph, Tier

AGENT_CONFIG = AgentConfig(
    name="context_architect",
    agent_number=8,
    description="Designs full context architectures with token budgets (Tier 5)",
    phase="generate",
    tier_scope=5,
    model="claude-opus-4.6",
    stakes="high",
)

_DEFAULT_CONTEXT_WINDOW = 128_000


class ContextArchitectAgent(BaseAgent):
    """Agent 8: Context Architecture Designer."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def generate(self, profile: NicheProfile, graph: TaskGraph, framework: EvalFramework) -> GeneratedPrompt:
        domain = profile.domain.replace("/", " ")
        model = profile.model_recommendation
        budget = self._design_token_budget(profile)

        lines = [f"<role>You handle {domain} with full context architecture.</role>"]

        # Token budget visualization
        lines.append("<token_budget>")
        for section, alloc in budget.items():
            bar = "#" * int(alloc["percent"] / 2)
            lines.append(f"  {section:20s} {alloc['percent']:5.1f}% ({alloc['tokens']:,} tokens) {bar}")
        lines.append("</token_budget>")

        # Process from subtasks
        lines.append("<process>")
        for i, st in enumerate(graph.subtasks, 1):
            lines.append(f"  {i}. {st.description}")
        lines.append("</process>")

        # KB architecture
        lines.append("<knowledge_base>")
        lines.append("  Structure:")
        lines.append("    policies/     - Domain policies, compliance docs")
        lines.append("    faqs/         - Frequently asked questions by category")
        lines.append("    reference/    - Product/service reference material")
        lines.append("  Retrieval: Semantic search, inject top 3 relevant chunks per query.")
        lines.append("  Freshness: Re-index weekly. Flag stale docs > 30 days.")
        lines.append("</knowledge_base>")

        # Compression strategy
        lines.append("<compression>")
        lines.append("  When context exceeds 80% of budget:")
        lines.append("  1. Summarize conversation history (keep last 5 turns verbatim)")
        lines.append("  2. Compress KB results to key facts only")
        lines.append("  3. NEVER compress system prompt or constraints")
        lines.append("</compression>")

        # Constraints
        lines.append("<constraints>")
        for c in profile.constraints:
            lines.append(f"  - {c.replace('_', ' ').title()}")
        if profile.compliance_requirements:
            for cr in profile.compliance_requirements:
                lines.append(f"  - Comply with {cr}")
        lines.append("  NEVER: Exceed token budget for any section.")
        lines.append("  NEVER: Compress safety-critical constraints.")
        lines.append("</constraints>")

        # Monitoring
        lines.append("<monitoring>")
        lines.append("  Track: resolution rate, avg turns, escalation rate, token usage per turn")
        lines.append("  Alert on: >30% escalation rate, >10 avg turns, token budget >90%")
        lines.append("  Regression: Re-run golden tests weekly. Any failure triggers review.")
        lines.append("</monitoring>")

        # Anti-patterns
        if profile.domain_antipatterns:
            lines.append("<avoid>")
            for ap in profile.domain_antipatterns:
                lines.append(f"  - {ap.replace('_', ' ')}")
            lines.append("</avoid>")

        content = "\n".join(lines)

        techniques = ["step_back", "recursive_summarization", "token_budget"]
        for st in graph.subtasks:
            techniques.extend(st.technique_candidates[:1])
        techniques = list(dict.fromkeys(techniques))[:4]

        return GeneratedPrompt(
            content=content,
            tier=Tier.FULL_ARCHITECTURE,
            model_target=model,
            token_count=len(content.split()),
            techniques_used=techniques,
            version="1.0.0",
            metadata={"context_window": _DEFAULT_CONTEXT_WINDOW, "token_budget": budget},
        )

    def _design_token_budget(self, profile: NicheProfile) -> dict[str, dict[str, Any]]:
        """Design token allocation based on the profile."""
        window = _DEFAULT_CONTEXT_WINDOW

        # Default allocation
        allocations = {
            "system_prompt": {"percent": 2.0, "tokens": 0},
            "knowledge_base": {"percent": 10.0, "tokens": 0},
            "conversation": {"percent": 60.0, "tokens": 0},
            "tool_results": {"percent": 15.0, "tokens": 0},
            "reserved": {"percent": 13.0, "tokens": 0},
        }

        # Adjust for domain
        if any(kw in profile.domain for kw in ["fintech", "healthcare", "legal"]):
            allocations["knowledge_base"]["percent"] = 15.0
            allocations["conversation"]["percent"] = 50.0
            allocations["reserved"]["percent"] = 18.0

        # Calculate token counts
        for section in allocations.values():
            section["tokens"] = int(window * section["percent"] / 100)

        return allocations

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        profile = NicheProfile(**input_data["niche_profile"])
        graph = TaskGraph(**input_data["task_graph"])
        framework = EvalFramework(**input_data["eval_framework"])
        result = self.generate(profile, graph, framework)
        return result.model_dump()
