"""Core data types for Prompt Production.

Every agent reads and writes these types. They form the contract
between the 13 agents in the pipeline.
"""

from __future__ import annotations

from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Tier(int, Enum):
    """Complexity tier for prompt generation routing."""

    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    MULTI_AGENT = 4
    FULL_ARCHITECTURE = 5


class Approach(StrEnum):
    """Whether to prompt engineer, context engineer, or both."""

    PROMPT_ENGINEER = "prompt_engineer"
    HYBRID = "hybrid"
    CONTEXT_ENGINEER = "context_engineer"


class NicheProfile(BaseModel):
    """Output of Agent 1: Niche Analyzer."""

    domain: str
    model_recommendation: str
    tier_hint: Tier
    approach: Approach
    constraints: list[str]
    domain_antipatterns: list[str]
    compliance_requirements: list[str]
    deployment_target: str
    confidence: float = Field(ge=0.0, le=1.0)


class Subtask(BaseModel):
    """A single atomic subtask in the task graph."""

    id: str
    description: str
    tier: Tier
    dependencies: list[str]
    technique_candidates: list[str]


class TaskGraph(BaseModel):
    """Output of Agent 2: Task Decomposer."""

    subtasks: list[Subtask]
    overall_tier: Tier
    execution_order: list[str]

    @field_validator("subtasks")
    @classmethod
    def max_five_subtasks(cls, v: list[Subtask]) -> list[Subtask]:
        if len(v) > 5:
            msg = f"max 5 subtasks allowed, got {len(v)}"
            raise ValueError(msg)
        return v


class EvalTestCase(BaseModel):
    """A single test case in the eval framework."""

    id: str
    category: str
    input_text: str
    expected_behavior: str
    pass_criteria: str


class ScoringRubric(BaseModel):
    """Multi-dimensional scoring rubric."""

    dimensions: dict[str, int]
    weights: dict[str, float]
    pass_threshold: float


class EvalFramework(BaseModel):
    """Output of Agent 3: Eval Architect."""

    test_cases: list[EvalTestCase]
    rubric: ScoringRubric
    adversarial_count: int
    edge_case_count: int


class TechniqueSelection(BaseModel):
    """Which techniques were selected and why."""

    techniques: list[str]
    recipe_name: str | None = None
    reasoning: str


class GeneratedPrompt(BaseModel):
    """Output of Agents 4-8: the generated prompt."""

    content: str
    tier: Tier
    model_target: str
    token_count: int
    techniques_used: list[str]
    version: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class StructuralScore(BaseModel):
    """Output of Agent 9: Structural Eval."""

    score: float = Field(ge=0.0, le=10.0)
    antipatterns_found: list[str]
    token_efficiency: float
    model_compatibility: float = Field(ge=0.0, le=10.0)
    technique_validation: bool
    issues: list[str]


class BehavioralScore(BaseModel):
    """Output of Agent 10: Behavioral Eval."""

    tests_passed: int
    tests_total: int
    failures: list[dict[str, str]]
    adversarial_passed: int
    adversarial_total: int
    edge_case_passed: int
    edge_case_total: int


class Recommendation(StrEnum):
    """Regression eval recommendation."""

    BASELINE_ESTABLISHED = "baseline_established"
    KEEP = "keep"
    REVIEW = "review"
    REVERT = "revert"


class RegressionScore(BaseModel):
    """Output of Agent 11: Regression Eval."""

    is_baseline: bool
    score_delta: float
    regressions: list[str]
    improvements: list[str]
    recommendation: Recommendation


class EvalResult(BaseModel):
    """Combined eval results from all 3 eval agents."""

    structural: StructuralScore
    behavioral: BehavioralScore
    regression: RegressionScore


class GateVerdict(BaseModel):
    """Decision from the test gate."""

    passed: bool
    structural_score: float
    behavioral_pass_count: int
    behavioral_total: int
    regression_delta: float
    iteration: int
    max_iterations: int = 3

    @property
    def can_retry(self) -> bool:
        return not self.passed and self.iteration < self.max_iterations


class LearningRecord(BaseModel):
    """Output of self-learning loop — stored in playbook."""

    domain: str
    model: str
    best_techniques: list[str]
    avoid_techniques: list[dict[str, str]]
    structural_score: float
    behavioral_pass_summary: str  # "11/11" format
    key_insight: str
    timestamp: str


class DeliveryPackage(BaseModel):
    """The final output delivered to the user."""

    prompts: list[GeneratedPrompt]
    eval_framework: EvalFramework
    eval_results: EvalResult
    niche_profile: NicheProfile
    task_graph: TaskGraph
    technique_selection: TechniqueSelection
    test_gate_verdict: GateVerdict
    failure_modes: list[str]
    version_info: str
    upgrade_path: str | None = None
    learning_record: LearningRecord | None = None
