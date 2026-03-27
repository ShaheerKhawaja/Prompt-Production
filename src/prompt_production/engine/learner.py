"""Self-Learning Loop — ACE-inspired Generate/Reflect/Curate cycle.

After every generation+test cycle, reflects on what worked, curates
lessons into an evolving playbook, and applies on future requests.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from prompt_production.types import (
    EvalResult,
    LearningRecord,
    NicheProfile,
    TechniqueSelection,
)

logger = logging.getLogger(__name__)

_PLAYBOOK_DIR = Path(__file__).parent.parent.parent.parent / "playbook" / "domains"


class LearningLoop:
    """ACE-inspired self-learning: Generate -> Reflect -> Curate."""

    def __init__(self, playbook_dir: Path | None = None) -> None:
        self._dir = playbook_dir or _PLAYBOOK_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    def reflect_and_curate(
        self,
        profile: NicheProfile,
        technique_selection: TechniqueSelection,
        results: EvalResult,
    ) -> LearningRecord:
        """Reflect on a generation cycle and store a lesson."""
        domain = profile.domain
        model = profile.model_recommendation

        # Reflect: what worked?
        structural_score = results.structural.score
        behavioral_total = results.behavioral.tests_total
        behavioral_passed = results.behavioral.tests_passed
        pass_summary = f"{behavioral_passed}/{behavioral_total}"

        # Determine best/avoid techniques
        techniques_used = technique_selection.techniques
        best_techniques = list(techniques_used) if structural_score >= 8.0 else []
        avoid_techniques: list[dict[str, str]] = []

        if structural_score < 7.0:
            for t in techniques_used:
                avoid_techniques.append(
                    {"technique": t, "reason": f"Low structural score ({structural_score}) with this technique"}
                )

        # Generate key insight
        insight = self._generate_insight(profile, results, technique_selection)

        record = LearningRecord(
            domain=domain,
            model=model,
            best_techniques=best_techniques,
            avoid_techniques=avoid_techniques,
            structural_score=structural_score,
            behavioral_pass_summary=pass_summary,
            key_insight=insight,
            timestamp=datetime.now(tz=UTC).isoformat(),
        )

        # Curate: store in playbook
        self._store(record)

        return record

    def consult(self, domain: str, model: str) -> list[LearningRecord]:
        """Consult the playbook for a domain+model combination."""
        records: list[LearningRecord] = []
        domain_key = domain.replace("/", "_")

        filepath = self._dir / f"{domain_key}.jsonl"
        if not filepath.exists():
            return records

        for line in filepath.read_text().splitlines():
            if line.strip():
                data = json.loads(line)
                if data.get("model") == model or not model:
                    records.append(LearningRecord(**data))

        return records

    def _generate_insight(
        self,
        profile: NicheProfile,
        results: EvalResult,
        selection: TechniqueSelection,
    ) -> str:
        """Generate a key insight from the results."""
        parts: list[str] = []

        if results.structural.antipatterns_found:
            parts.append(f"Anti-patterns found: {', '.join(results.structural.antipatterns_found)}")

        if results.behavioral.failures:
            fail_types = [f.get("severity", "unknown") for f in results.behavioral.failures]
            if "critical" in fail_types:
                parts.append("Critical behavioral failures detected")

        if results.structural.score >= 9.0:
            parts.append(f"Excellent structural quality with {', '.join(selection.techniques)}")

        if profile.compliance_requirements:
            parts.append(f"Compliance requirements: {', '.join(profile.compliance_requirements)}")

        return "; ".join(parts) if parts else "Standard generation, no notable insights"

    def _store(self, record: LearningRecord) -> None:
        """Append a learning record to the domain's playbook file."""
        domain_key = record.domain.replace("/", "_")
        filepath = self._dir / f"{domain_key}.jsonl"

        with open(filepath, "a") as f:
            f.write(record.model_dump_json() + "\n")

        logger.info("Learning record stored: %s (%s)", record.domain, record.key_insight[:60])
