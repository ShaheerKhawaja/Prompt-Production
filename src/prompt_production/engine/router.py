"""Complexity Router — dispatches to the correct tier specialist agent.

Routes TaskGraph.overall_tier to Agents 4-8:
  Tier 1 -> Agent 4 (Simple Engineer)
  Tier 2 -> Agent 5 (Moderate Engineer)
  Tier 3 -> Agent 6 (Complex Engineer)
  Tier 4 -> Agent 7 (Multi-Agent Architect)
  Tier 5 -> Agent 8 (Context Architect)
"""

from __future__ import annotations

import logging

from prompt_production.agents.complex_engineer import ComplexEngineerAgent
from prompt_production.agents.context_architect import ContextArchitectAgent
from prompt_production.agents.moderate_engineer import ModerateEngineerAgent
from prompt_production.agents.multiagent_architect import MultiAgentArchitectAgent
from prompt_production.agents.simple_engineer import SimpleEngineerAgent
from prompt_production.types import EvalFramework, GeneratedPrompt, NicheProfile, TaskGraph, Tier

logger = logging.getLogger(__name__)


class ComplexityRouter:
    """Routes requests to the correct tier specialist."""

    def __init__(self) -> None:
        self._agents = {
            Tier.SIMPLE: SimpleEngineerAgent(),
            Tier.MODERATE: ModerateEngineerAgent(),
            Tier.COMPLEX: ComplexEngineerAgent(),
            Tier.MULTI_AGENT: MultiAgentArchitectAgent(),
            Tier.FULL_ARCHITECTURE: ContextArchitectAgent(),
        }

    def route(
        self,
        profile: NicheProfile,
        graph: TaskGraph,
        framework: EvalFramework,
    ) -> list[GeneratedPrompt]:
        """Route to the appropriate agent and return generated prompts."""
        tier = graph.overall_tier
        agent = self._agents.get(tier)

        if agent is None:
            msg = f"No agent registered for tier {tier}"
            raise ValueError(msg)

        logger.info("Routing to %s (Tier %d)", agent.config.name, tier.value)

        if tier == Tier.MULTI_AGENT and isinstance(agent, MultiAgentArchitectAgent):
            return agent.generate(profile, graph, framework)

        # All other agents return a single prompt
        result = agent.generate(profile, graph, framework)  # type: ignore[union-attr]
        return [result]
