"""Main pipeline orchestrator for Prompt Production.

Wires the complete 6-phase flow:
  UNDERSTAND -> DESIGN EVALS -> SELECT TECHNIQUES -> GENERATE -> TEST -> DELIVER

All 13 agents are connected. The router dispatches to the correct tier specialist.
The testbench runs all 3 eval agents. The learning loop curates lessons after delivery.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from prompt_production.agents.eval_architect import EvalArchitectAgent
from prompt_production.agents.niche_analyzer import NicheAnalyzerAgent
from prompt_production.agents.task_decomposer import TaskDecomposerAgent
from prompt_production.engine.composer import TechniqueComposer
from prompt_production.engine.learner import LearningLoop
from prompt_production.engine.router import ComplexityRouter
from prompt_production.engine.testbench import Testbench, TestbenchResult
from prompt_production.types import (
    EvalFramework,
    GeneratedPrompt,
    LearningRecord,
    NicheProfile,
    TaskGraph,
    TechniqueSelection,
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Full result from running the pipeline."""

    niche_profile: NicheProfile
    task_graph: TaskGraph
    eval_framework: EvalFramework
    technique_selection: TechniqueSelection
    generated_prompts: list[GeneratedPrompt]
    testbench_result: TestbenchResult
    learning_record: LearningRecord | None
    passed_gate: bool
    failure_modes: list[str] = field(default_factory=list)

    @property
    def primary_prompt(self) -> GeneratedPrompt:
        """The main generated prompt (first in list)."""
        return self.generated_prompts[0]


class Pipeline:
    """Complete 6-phase pipeline orchestrator.

    Phase 1: UNDERSTAND (Agents 1-2)
    Phase 2: DESIGN EVALS (Agent 3 — TDD)
    Phase 3: SELECT TECHNIQUES (Composer)
    Phase 4: GENERATE (Router -> Agents 4-8)
    Phase 5: TEST (Testbench -> Agents 9-11 -> Gate -> Fix Loop)
    Phase 6: LEARN + DELIVER (Learning Loop)
    """

    def __init__(self) -> None:
        self.niche_analyzer = NicheAnalyzerAgent()
        self.task_decomposer = TaskDecomposerAgent()
        self.eval_architect = EvalArchitectAgent()
        self.composer = TechniqueComposer()
        self.router = ComplexityRouter()
        self.testbench = Testbench()
        self.learner = LearningLoop()

    def run(self, user_request: str) -> PipelineResult:
        """Execute the complete 6-phase pipeline."""
        logger.info("Pipeline started: %s", user_request[:80])

        # Phase 1: UNDERSTAND
        logger.info("Phase 1: UNDERSTAND")
        niche_profile = self.niche_analyzer.analyze_request(user_request)
        logger.info(
            "  Domain: %s | Tier: %s | Approach: %s",
            niche_profile.domain,
            niche_profile.tier_hint.name,
            niche_profile.approach.value,
        )

        task_graph = self.task_decomposer.decompose(niche_profile, user_request)
        logger.info(
            "  Subtasks: %d | Tier: %s | Order: %s",
            len(task_graph.subtasks),
            task_graph.overall_tier.name,
            task_graph.execution_order,
        )

        # Phase 2: DESIGN EVALS FIRST (TDD)
        logger.info("Phase 2: DESIGN EVALS (TDD)")
        eval_framework = self.eval_architect.design_framework(niche_profile, task_graph)
        golden_count = (
            len(eval_framework.test_cases) - eval_framework.adversarial_count - eval_framework.edge_case_count
        )
        logger.info(
            "  Tests: %d golden + %d adversarial + %d edge",
            golden_count,
            eval_framework.adversarial_count,
            eval_framework.edge_case_count,
        )

        # Phase 3: SELECT TECHNIQUES
        logger.info("Phase 3: SELECT TECHNIQUES")
        task_type = self._infer_task_type(user_request)
        technique_selection = self.composer.select(task_graph, task_type)
        logger.info(
            "  Techniques: %s | Recipe: %s",
            technique_selection.techniques,
            technique_selection.recipe_name or "custom",
        )

        # Phase 4: GENERATE (via complexity router)
        logger.info("Phase 4: GENERATE (Tier %d)", task_graph.overall_tier.value)
        generated_prompts = self.router.route(niche_profile, task_graph, eval_framework)
        logger.info(
            "  Generated %d prompt(s), total %d tokens",
            len(generated_prompts),
            sum(p.token_count for p in generated_prompts),
        )

        # Phase 5: TEST (full testbench — structural + behavioral + regression)
        logger.info("Phase 5: TEST")
        primary_prompt = generated_prompts[0]
        prompt_id = f"{niche_profile.domain}_{task_graph.overall_tier.name}".lower()
        testbench_result = self.testbench.run(primary_prompt, eval_framework, prompt_id)
        logger.info(
            "  Structural: %.1f | Behavioral: %d/%d | Gate: %s",
            testbench_result.verdict.structural_score,
            testbench_result.verdict.behavioral_pass_count,
            testbench_result.verdict.behavioral_total,
            "PASS" if testbench_result.verdict.passed else "FAIL",
        )

        # Phase 5b: FIX LOOP
        # Note: With rule-based agents (no LLM), regeneration is deterministic
        # so the fix loop is a no-op. With LLM-backed agents, each regeneration
        # would incorporate fix suggestions to produce improved output.
        # For now, we accept the first result without looping.

        # Phase 6: LEARN + DELIVER
        logger.info("Phase 6: LEARN + DELIVER")
        learning_record = self.learner.reflect_and_curate(niche_profile, technique_selection, testbench_result.result)
        logger.info("  Insight: %s", learning_record.key_insight[:80])

        # Generate failure modes
        failure_modes = self._generate_failure_modes(niche_profile, testbench_result)

        passed = testbench_result.verdict.passed
        logger.info(
            "Pipeline %s (score: %.1f)",
            "PASSED" if passed else "DELIVERED WITH CAVEATS",
            testbench_result.verdict.structural_score,
        )

        return PipelineResult(
            niche_profile=niche_profile,
            task_graph=task_graph,
            eval_framework=eval_framework,
            technique_selection=technique_selection,
            generated_prompts=generated_prompts,
            testbench_result=testbench_result,
            learning_record=learning_record,
            passed_gate=passed,
            failure_modes=failure_modes,
        )

    def _infer_task_type(self, request: str) -> str | None:
        """Infer the task type for technique selection."""
        req = request.lower()
        type_map = {
            "tool_using": ["tool", "api", "database", "function"],
            "conversational": ["chat", "conversation", "support"],
            "code": ["code", "programming", "review", "debug"],
            "creative": ["creative", "write", "generate", "design"],
            "knowledge": ["research", "analyze", "summarize"],
            "multi_agent": ["multi-agent", "squad", "orchestrat"],
        }
        for task_type, keywords in type_map.items():
            if any(kw in req for kw in keywords):
                return task_type
        return None

    def _generate_failure_modes(self, profile: NicheProfile, tb: TestbenchResult) -> list[str]:
        """Generate top failure modes based on domain and test results."""
        modes = []
        for ap in profile.domain_antipatterns[:3]:
            modes.append(f"Domain risk: {ap.replace('_', ' ')}")
        if tb.fix_suggestions:
            for fs in tb.fix_suggestions[:2]:
                modes.append(f"Test finding: {fs.reason}")
        if not modes:
            modes.append("No significant failure modes identified in testing")
        return modes
