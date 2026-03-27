"""Tests for the Technique Composition Engine."""

from prompt_production.engine.composer import TechniqueComposer
from prompt_production.types import Subtask, TaskGraph, Tier


def _graph(tier: Tier, techniques: list[str]) -> TaskGraph:
    return TaskGraph(
        subtasks=[Subtask(id="A", description="test", tier=tier, dependencies=[], technique_candidates=techniques)],
        overall_tier=tier,
        execution_order=["A"],
    )


class TestTechniqueComposer:
    def setup_method(self):
        self.composer = TechniqueComposer()

    def test_max_four_techniques(self):
        graph = _graph(Tier.COMPLEX, ["a", "b", "c", "d", "e", "f"])
        result = self.composer.select(graph)
        assert len(result.techniques) <= 4

    def test_recipe_match_for_multi_agent(self):
        graph = _graph(Tier.MULTI_AGENT, ["peer", "graph_of_thoughts"])
        result = self.composer.select(graph)
        assert result.recipe_name == "multi_agent_orchestration"

    def test_recipe_match_for_context_architecture(self):
        graph = _graph(Tier.FULL_ARCHITECTURE, ["step_back", "token_budget"])
        result = self.composer.select(graph)
        assert result.recipe_name == "context_architecture"

    def test_task_type_recipe_match(self):
        graph = _graph(Tier.COMPLEX, ["self_debugging"])
        result = self.composer.select(graph, task_type="code")
        assert result.recipe_name == "code_generation"

    def test_creative_recipe(self):
        graph = _graph(Tier.COMPLEX, ["tree_of_thoughts"])
        result = self.composer.select(graph, task_type="creative")
        assert result.recipe_name == "creative_exploration"
        assert "tree_of_thoughts" in result.techniques

    def test_bad_combo_filtered(self):
        # chain_of_thought + tree_of_thoughts = BAD
        graph = _graph(Tier.COMPLEX, ["chain_of_thought", "tree_of_thoughts", "react"])
        result = self.composer.select(graph)
        # Should not have both
        has_cot = "chain_of_thought" in result.techniques
        has_tot = "tree_of_thoughts" in result.techniques
        assert not (has_cot and has_tot), "Bad combo chain_of_thought + tree_of_thoughts not filtered"

    def test_deduplicates_techniques(self):
        st_a = Subtask(
            id="A", description="t1", tier=Tier.COMPLEX,
            dependencies=[], technique_candidates=["react", "constitutional_ai"],
        )
        st_b = Subtask(
            id="B", description="t2", tier=Tier.MODERATE,
            dependencies=[], technique_candidates=["react", "phase_flow"],
        )
        graph = TaskGraph(subtasks=[st_a, st_b], overall_tier=Tier.COMPLEX, execution_order=["A", "B"])
        result = self.composer.select(graph)
        assert len(result.techniques) == len(set(result.techniques))  # No duplicates

    def test_reasoning_included(self):
        graph = _graph(Tier.SIMPLE, ["direct_instruction"])
        result = self.composer.select(graph)
        assert result.reasoning != ""

    def test_list_recipes(self):
        recipes = self.composer.list_recipes()
        assert len(recipes) >= 8
        assert "deep_reasoning" in recipes
        assert "bulletproof_agent" in recipes

    def test_get_technique_info(self):
        info = self.composer.get_technique_info("chain_of_thought")
        assert info is not None
        assert info["category"] == "thought_generation"

    def test_unknown_technique_returns_none(self):
        info = self.composer.get_technique_info("nonexistent_technique")
        assert info is None

    def test_tool_using_gets_bulletproof(self):
        graph = _graph(Tier.COMPLEX, ["react"])
        result = self.composer.select(graph, task_type="tool_using")
        assert result.recipe_name == "bulletproof_agent"
        assert "react" in result.techniques
        assert "constitutional_ai" in result.techniques
