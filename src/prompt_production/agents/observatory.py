"""Agent 13: Observatory.

Production monitoring specialist. Generates monitoring specs, alerting rules,
and runbooks for deployed prompts.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from prompt_production.agents.base import AgentConfig, BaseAgent
from prompt_production.types import GeneratedPrompt, NicheProfile

AGENT_CONFIG = AgentConfig(
    name="observatory",
    agent_number=13,
    description="Generates monitoring specs, alerts, and runbooks for deployed prompts",
    phase="cross_cutting",
    tier_scope=None,
    model="claude-sonnet-4.6",
    stakes="medium",
)


class MonitoringSpec(BaseModel):
    metrics: list[dict[str, str]]  # [{name, description, threshold}]
    alerts: list[dict[str, str]]  # [{condition, severity, action}]
    runbook_steps: list[str]
    regression_schedule: str
    drift_signals: list[str]


class ObservatoryAgent(BaseAgent):
    """Agent 13: Observatory."""

    def __init__(self) -> None:
        super().__init__(config=AGENT_CONFIG)

    def generate_monitoring(self, prompt: GeneratedPrompt, profile: NicheProfile) -> MonitoringSpec:
        """Generate a monitoring specification for a deployed prompt."""
        domain = profile.domain.split("/")[0]

        metrics = self._design_metrics(domain, prompt)
        alerts = self._design_alerts(domain, profile)
        runbook = self._design_runbook(domain)
        drift_signals = self._identify_drift_signals(profile)

        return MonitoringSpec(
            metrics=metrics,
            alerts=alerts,
            runbook_steps=runbook,
            regression_schedule="Weekly: re-run golden test suite against current model version",
            drift_signals=drift_signals,
        )

    def _design_metrics(self, domain: str, prompt: GeneratedPrompt) -> list[dict[str, str]]:
        base_metrics = [
            {
                "name": "resolution_rate",
                "description": "Percentage of conversations resolved without escalation",
                "threshold": ">70%",
            },
            {"name": "avg_turns", "description": "Average conversation turns to resolution", "threshold": "<8"},
            {"name": "user_satisfaction_proxy", "description": "Last-message sentiment score", "threshold": ">0.6"},
            {
                "name": "token_usage_per_turn",
                "description": "Average tokens consumed per turn",
                "threshold": f"<{prompt.token_count * 3}",
            },
        ]

        domain_metrics = {
            "fintech": [
                {
                    "name": "compliance_adherence",
                    "description": "Percentage of interactions following PCI protocol",
                    "threshold": ">99%",
                }
            ],
            "healthcare": [
                {
                    "name": "escalation_appropriateness",
                    "description": "Correct escalation decisions for emergency symptoms",
                    "threshold": "100%",
                }
            ],
            "support": [
                {
                    "name": "first_contact_resolution",
                    "description": "Resolved on first contact without follow-up",
                    "threshold": ">60%",
                }
            ],
        }

        return base_metrics + domain_metrics.get(domain, [])

    def _design_alerts(self, domain: str, profile: NicheProfile) -> list[dict[str, str]]:
        alerts = [
            {
                "condition": "resolution_rate < 50%",
                "severity": "critical",
                "action": "Page oncall. Check for model regression or prompt corruption.",
            },
            {
                "condition": "avg_turns > 15",
                "severity": "warning",
                "action": "Review conversation logs. Prompt may be looping.",
            },
            {
                "condition": "golden_test_failure",
                "severity": "critical",
                "action": "Block new deployments. Run full regression suite.",
            },
        ]

        if profile.compliance_requirements:
            alerts.append(
                {
                    "condition": "compliance_adherence < 99%",
                    "severity": "critical",
                    "action": "Immediate review. Compliance failure is a regulatory risk.",
                }
            )

        return alerts

    def _design_runbook(self, domain: str) -> list[str]:
        return [
            "1. Check: Is the model version the same as when the prompt was tested?",
            "2. Check: Has the prompt been modified since last test pass?",
            "3. Run: Full golden test suite against current deployment",
            "4. Compare: Current scores vs baseline (from regression eval)",
            "5. If regression detected: Roll back to last known-good prompt version",
            "6. If model changed: Re-run technique composition (model may need different approach)",
            "7. If new failure pattern: Add to adversarial test suite and regenerate prompt",
            "8. Document: Update the prompt changelog with findings",
        ]

    def _identify_drift_signals(self, profile: NicheProfile) -> list[str]:
        signals = [
            "Model version change (provider update)",
            "Golden test pass rate drops below 80%",
            "User satisfaction proxy drops > 20% from baseline",
            "New conversation patterns not seen in test suite",
        ]

        if profile.compliance_requirements:
            signals.append("Any compliance-related test failure (zero tolerance)")

        return signals

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        prompt = GeneratedPrompt(**input_data["prompt"])
        profile = NicheProfile(**input_data["niche_profile"])
        result = self.generate_monitoring(prompt, profile)
        return result.model_dump()
