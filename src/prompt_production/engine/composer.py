"""Technique Composition Engine.

Selects 2-4 techniques from the registry based on task type,
validates against composition rules, returns a TechniqueSelection.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from prompt_production.types import TaskGraph, TechniqueSelection, Tier

logger = logging.getLogger(__name__)

_TECHNIQUES_DIR = Path(__file__).parent.parent.parent.parent / "techniques"


def _load_yaml(filename: str) -> dict:
    path = _TECHNIQUES_DIR / filename
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


class TechniqueComposer:
    """Selects and validates technique compositions."""

    def __init__(self) -> None:
        self._registry = _load_yaml("registry.yaml").get("techniques", {})
        self._recipes = _load_yaml("recipes.yaml").get("recipes", {})
        rules = _load_yaml("composition_rules.yaml")
        self._bad_combos: list[list[str]] = rules.get("compatibility", {}).get("bad", [])
        self._good_combos: list[list[str]] = rules.get("compatibility", {}).get("good", [])
        self._max = rules.get("max_composition", 4)
        self._priority = rules.get("priority_order", [])

    def select(self, task_graph: TaskGraph, task_type: str | None = None) -> TechniqueSelection:
        """Select techniques for a task graph."""
        # Try recipe match first
        recipe = self._match_recipe(task_graph, task_type)
        if recipe:
            return recipe

        # Collect candidates from subtasks
        candidates: list[str] = []
        for st in task_graph.subtasks:
            candidates.extend(st.technique_candidates)
        candidates = list(dict.fromkeys(candidates))  # dedupe

        # Validate and cap
        selected = self._validate_and_cap(candidates)

        reasoning = f"Selected {len(selected)} techniques from {len(candidates)} candidates. "
        reasoning += f"Tier: {task_graph.overall_tier.name}."

        return TechniqueSelection(
            techniques=selected,
            recipe_name=None,
            reasoning=reasoning,
        )

    def _match_recipe(self, graph: TaskGraph, task_type: str | None) -> TechniqueSelection | None:
        """Try to match a pre-built recipe."""
        tier = graph.overall_tier

        # Tier-based recipe matching
        recipe_map = {
            "tool_using": "bulletproof_agent",
            "conversational": "deep_reasoning" if tier.value >= Tier.COMPLEX.value else None,
            "creative": "creative_exploration",
            "code": "code_generation",
            "multi_agent": "multi_agent_orchestration",
            "context_arch": "context_architecture",
            "knowledge": "knowledge_synthesis",
        }

        recipe_name = recipe_map.get(task_type or "") if task_type else None

        # Tier-based fallback
        if not recipe_name:
            if tier == Tier.MULTI_AGENT:
                recipe_name = "multi_agent_orchestration"
            elif tier == Tier.FULL_ARCHITECTURE:
                recipe_name = "context_architecture"

        if recipe_name and recipe_name in self._recipes:
            recipe = self._recipes[recipe_name]
            techniques = recipe.get("techniques", [])
            return TechniqueSelection(
                techniques=techniques[:self._max],
                recipe_name=recipe_name,
                reasoning=f"Matched recipe '{recipe_name}': {recipe.get('description', '')}",
            )

        return None

    def _validate_and_cap(self, candidates: list[str]) -> list[str]:
        """Validate compositions and cap at max."""
        # Remove bad combinations
        filtered = list(candidates)
        for bad in self._bad_combos:
            if len(bad) == 2 and bad[0] in filtered and bad[1] in filtered:
                # Keep the one that appears first in priority, drop the other
                keep = bad[0] if bad[0] in self._priority else bad[1]
                drop = bad[1] if keep == bad[0] else bad[0]
                if drop in filtered:
                    filtered.remove(drop)
                    logger.info("Dropped %s (conflicts with %s)", drop, keep)

        # Cap at max, keeping priority items
        if len(filtered) > self._max:
            priority_items = [t for t in self._priority if t in filtered]
            non_priority = [t for t in filtered if t not in priority_items]
            remaining_slots = self._max - len(priority_items)
            filtered = priority_items + non_priority[:max(0, remaining_slots)]

        return filtered[:self._max]

    def get_technique_info(self, name: str) -> dict | None:
        """Get info about a specific technique."""
        return self._registry.get(name)

    def list_recipes(self) -> dict:
        """List all available recipes."""
        return dict(self._recipes)
