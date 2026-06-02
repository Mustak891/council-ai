"""LangGraph state machine for Council AI."""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, StateGraph

from src.agents import pragmatist, skeptic, visionary
from src.state import CouncilState


def _initial_state(state: CouncilState) -> CouncilState:
    """Normalize the incoming state before the debate begins."""
    normalized_state: CouncilState = {
        **state,
        "messages": list(state.get("messages", [])),
        "agent_outputs": dict(state.get("agent_outputs", {})),
        "debate_rounds": state.get("debate_rounds", 0),
        "turn_count": state.get("turn_count", 0),
        "max_turns": state.get("max_turns", 3),
    }
    print(f"[graph] Initial state normalized: round={normalized_state['debate_rounds']}, turns={normalized_state['turn_count']}")
    return normalized_state


def visionary_node(state: CouncilState) -> CouncilState:
    print("[graph] Entering visionary node")
    return visionary(state)


def skeptic_node(state: CouncilState) -> CouncilState:
    print("[graph] Entering skeptic node")
    return skeptic(state)


def pragmatist_node(state: CouncilState) -> CouncilState:
    print("[graph] Entering pragmatist node")
    updated_state = pragmatist(state)
    updated_state["debate_rounds"] = updated_state.get("debate_rounds", 0) + 1
    updated_state["turn_count"] = updated_state.get("turn_count", 0) + 1
    print(f"[graph] Debate round advanced to {updated_state['debate_rounds']}")
    return updated_state


def finalize_node(state: CouncilState) -> CouncilState:
    print("[graph] Finalizing debate output")
    messages = state.get("messages", [])
    agent_outputs = state.get("agent_outputs", {})
    consensus = agent_outputs.get("pragmatist") or (messages[-1] if messages else "No consensus available.")
    confidence = 0.45 + min(state.get("debate_rounds", 0), 3) * 0.15
    finalized_state: CouncilState = {
        **state,
        "consensus": consensus,
        "consensus_confidence": min(confidence, 0.9),
    }
    print(f"[graph] Consensus confidence set to {finalized_state['consensus_confidence']}")
    return finalized_state


def route_after_pragmatist(state: CouncilState) -> Literal["continue", "finalize"]:
    """Route to the next round or end the debate."""
    debate_rounds = state.get("debate_rounds", 0)
    turn_count = state.get("turn_count", 0)
    max_turns = state.get("max_turns", 3)
    print(f"[graph] Routing after pragmatist: rounds={debate_rounds}, turns={turn_count}, max_turns={max_turns}")
    if debate_rounds < 2 and turn_count < max_turns:
        return "continue"
    return "finalize"


def build_council_graph():
    """Build and return the compiled LangGraph workflow."""
    graph = StateGraph(CouncilState)
    graph.add_node("initialize", _initial_state)
    graph.add_node("visionary_node", visionary_node)
    graph.add_node("skeptic_node", skeptic_node)
    graph.add_node("pragmatist_node", pragmatist_node)
    graph.add_node("finalize_node", finalize_node)

    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "visionary_node")
    graph.add_edge("visionary_node", "skeptic_node")
    graph.add_edge("skeptic_node", "pragmatist_node")
    graph.add_conditional_edges(
        "pragmatist_node",
        route_after_pragmatist,
        {
            "continue": "visionary_node",
            "finalize": "finalize_node",
        },
    )
    graph.add_edge("finalize_node", END)
    return graph.compile()