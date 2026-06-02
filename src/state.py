"""State schema for LangGraph."""

from typing import NotRequired, TypedDict


class CouncilState(TypedDict, total=False):
    """State for the Council AI multi-agent system."""

    messages: list[str]
    agent_outputs: dict[str, str]
    consensus: str
    consensus_confidence: float
    debate_rounds: int
    current_agent: str
    turn_count: int
    prompt: str
    max_turns: int