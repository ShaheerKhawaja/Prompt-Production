"""Base agent protocol for all 13 agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str
    agent_number: int
    description: str
    phase: str
    tier_scope: int | None  # None = all tiers
    model: str
    stakes: str  # "low", "medium", "high"


class BaseAgent:
    """Base class for all 13 agents in the framework."""

    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    @property
    def prompt_path(self) -> str:
        filename = f"agent_{self.config.agent_number:02d}_{self.config.name}.md"
        return str(self.PROMPTS_DIR / filename)

    def load_prompt(self) -> str:
        path = Path(self.prompt_path)
        if not path.exists():
            msg = f"Prompt file not found: {path}"
            raise FileNotFoundError(msg)
        return path.read_text()

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent. Subclasses override this."""
        raise NotImplementedError
