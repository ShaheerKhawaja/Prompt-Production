"""Main pipeline orchestrator for Prompt Production.

Wires the 5-phase flow: UNDERSTAND -> DESIGN EVALS -> GENERATE -> TEST -> DELIVER.
Phase 1 MVP: Agents 1 -> 2 -> 3 -> 6 -> 9 (Niche -> Decompose -> Eval -> Generate -> StructuralEval).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from prompt_production.agents.eval_architect import EvalArchitectAgent
from prompt_production.agents.niche_analyzer import NicheAnalyzerAgent
from prompt_production.agents.structural_eval import StructuralEvalAgent
from prompt_production.agents.task_decomposer import TaskDecomposerAgent
from prompt_production.types import (
    EvalFramework,
    GeneratedPrompt,
    NicheProfile,
    StructuralScore,
    TaskGraph,
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result from running the pipeline."""

    niche_profile: NicheProfile
    task_graph: TaskGraph
    eval_framework: EvalFramework
    generated_prompt: GeneratedPrompt
    structural_score: StructuralScore
    passed_gate: bool


class Pipeline:
    """Main pipeline orchestrator.

    Phase 1 MVP flow:
    1. Niche Analyzer (Agent 1) -> NicheProfile
    2. Task Decomposer (Agent 2) -> TaskGraph
    3. Assessment Architect (Agent 3) -> EvalFramework
    4. Generate prompt (stub for Agent 6) -> GeneratedPrompt
    5. Structural Assessment (Agent 9) -> StructuralScore
    """

    def __init__(self) -> None:
        self.niche_analyzer = NicheAnalyzerAgent()
        self.task_decomposer = TaskDecomposerAgent()
        self.eval_architect = EvalArchitectAgent()
        self.structural_eval = StructuralEvalAgent()

    def run(self, user_request: str) -> PipelineResult:
        """Execute the full pipeline for a user request."""
        logger.info("Pipeline started: %s", user_request[:80])

        # Phase 1: UNDERSTAND
        logger.info("Phase 1: Niche Analysis")
        niche_profile = self.niche_analyzer.analyze_request(user_request)
        logger.info("  Domain: %s | Tier: %s | Approach: %s",
                     niche_profile.domain, niche_profile.tier_hint.name, niche_profile.approach.value)

        logger.info("Phase 1: Task Decomposition")
        task_graph = self.task_decomposer.decompose(niche_profile, user_request)
        logger.info("  Subtasks: %d | Tier: %s | Order: %s",
                     len(task_graph.subtasks), task_graph.overall_tier.name, task_graph.execution_order)

        # Phase 2: DESIGN EVALS FIRST (TDD)
        logger.info("Phase 2: Assessment Framework Design (TDD)")
        eval_framework = self.eval_architect.design_framework(niche_profile, task_graph)
        logger.info("  Tests: %d (golden) + %d (adversarial) + %d (edge)",
                     len(eval_framework.test_cases) - eval_framework.adversarial_count - eval_framework.edge_case_count,
                     eval_framework.adversarial_count, eval_framework.edge_case_count)

        # Phase 3: GENERATE (stub for Phase 1 — Agent 6 will replace this)
        logger.info("Phase 3: Prompt Generation")
        generated_prompt = self._generate_stub(niche_profile, task_graph, eval_framework)
        logger.info("  Tokens: %d | Model: %s", generated_prompt.token_count, generated_prompt.model_target)

        # Phase 4: TEST (structural only in Phase 1)
        logger.info("Phase 4: Structural Assessment")
        structural_score = self.structural_eval.evaluate(generated_prompt)
        logger.info("  Score: %.1f/10 | Anti-patterns: %d | Issues: %d",
                     structural_score.score, len(structural_score.antipatterns_found), len(structural_score.issues))

        passed = structural_score.score >= 8.0

        logger.info("Pipeline %s (score: %.1f)", "PASSED" if passed else "FAILED", structural_score.score)

        return PipelineResult(
            niche_profile=niche_profile,
            task_graph=task_graph,
            eval_framework=eval_framework,
            generated_prompt=generated_prompt,
            structural_score=structural_score,
            passed_gate=passed,
        )

    def _generate_stub(
        self,
        profile: NicheProfile,
        graph: TaskGraph,
        framework: EvalFramework,
    ) -> GeneratedPrompt:
        """Stub prompt generator for Phase 1 MVP.

        Generates a basic but structurally clean prompt.
        Agent 6 (Complex Engineer) will replace this.
        """
        model = profile.model_recommendation
        domain = profile.domain
        constraints = profile.constraints
        antipatterns = profile.domain_antipatterns

        # Build XML-structured prompt for Claude, markdown for GPT
        if "claude" in model.lower():
            content = self._build_xml_prompt(domain, constraints, antipatterns, graph)
        else:
            content = self._build_markdown_prompt(domain, constraints, antipatterns, graph)

        techniques = []
        for subtask in graph.subtasks:
            techniques.extend(subtask.technique_candidates[:2])
        techniques = list(dict.fromkeys(techniques))[:4]  # Dedupe, cap at 4

        return GeneratedPrompt(
            content=content,
            tier=graph.overall_tier,
            model_target=model,
            token_count=len(content.split()),
            techniques_used=techniques,
            version="1.0.0",
        )

    def _build_xml_prompt(
        self, domain: str, constraints: list[str], antipatterns: list[str], graph: TaskGraph
    ) -> str:
        parts = [f"<role>You handle {domain.replace('/', ' ')} tasks.</role>"]
        parts.append("<process>")
        for i, subtask in enumerate(graph.subtasks, 1):
            parts.append(f"  {i}. {subtask.description}")
        parts.append("</process>")

        if constraints:
            parts.append("<constraints>")
            for c in constraints:
                parts.append(f"  - {c.replace('_', ' ').title()}")
            parts.append("</constraints>")

        if antipatterns:
            parts.append("<avoid>")
            for ap in antipatterns:
                parts.append(f"  - {ap.replace('_', ' ')}")
            parts.append("</avoid>")

        return "\n".join(parts)

    def _build_markdown_prompt(
        self, domain: str, constraints: list[str], antipatterns: list[str], graph: TaskGraph
    ) -> str:
        parts = [f"# Role\nYou handle {domain.replace('/', ' ')} tasks.\n"]
        parts.append("## Process")
        for i, subtask in enumerate(graph.subtasks, 1):
            parts.append(f"{i}. {subtask.description}")

        if constraints:
            parts.append("\n## Constraints")
            for c in constraints:
                parts.append(f"- {c.replace('_', ' ').title()}")

        if antipatterns:
            parts.append("\n## Avoid")
            for ap in antipatterns:
                parts.append(f"- {ap.replace('_', ' ')}")

        return "\n".join(parts)
