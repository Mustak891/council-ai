"""Agent prompt templates and Groq-backed agent functions."""

import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.state import CouncilState
from src.tools import run_web_search

load_dotenv()

VISIONARY_PROMPT = """You are the Visionary. Think big and creative. Ignore constraints."""

SKEPTIC_PROMPT = """You are the Skeptic. Analyze risks and feasibility. Be critical."""

PRAGMATIST_PROMPT = """You are the Pragmatist. Create actionable, step-by-step plans."""


def get_llm(temperature: float) -> ChatGroq:
    """Create a Groq chat model with a shared model choice."""
    print(f"[agents] Initializing ChatGroq with temperature={temperature}")
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=temperature)


def _run_agent(
    role_name: str,
    system_prompt: str,
    state: CouncilState,
    temperature: float,
) -> CouncilState:
    """Run a single agent and return the updated state."""
    try:
        print(f"[agents] Running {role_name} agent")
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your environment or a .env file."
            )
        llm = get_llm(temperature=temperature)
        messages = state.get("messages", [])
        print(f"[agents] {role_name} sees {len(messages)} prior messages")
        prompt_text = state.get("prompt", "")
        conversation = "\n".join(messages)
        llm_prompt = (
            f"{system_prompt}\n\n"
            f"Conversation so far:\n{conversation or 'No prior messages.'}\n\n"
            f"User prompt: {prompt_text}"
        )
        response = llm.invoke(llm_prompt)
        response_text = getattr(response, "content", str(response))
        print(f"[agents] {role_name} response received")
        updated_messages = list(messages)
        updated_messages.append(f"{role_name}: {response_text}")
        updated_outputs = dict(state.get("agent_outputs", {}))
        updated_outputs[role_name.lower()] = response_text
        return {
            **state,
            "messages": updated_messages,
            "agent_outputs": updated_outputs,
            "current_agent": role_name.lower(),
        }
    except Exception as exc:
        print(f"[agents] {role_name} agent error: {exc}")
        updated_messages = list(state.get("messages", []))
        error_message = f"{role_name} agent error: {exc}"
        updated_messages.append(error_message)
        updated_outputs = dict(state.get("agent_outputs", {}))
        updated_outputs[role_name.lower()] = error_message
        return {
            **state,
            "messages": updated_messages,
            "agent_outputs": updated_outputs,
            "current_agent": role_name.lower(),
        }


def visionary(state: CouncilState) -> CouncilState:
    """Visionary agent - returns creative ideas."""
    return _run_agent("Visionary", VISIONARY_PROMPT, state, temperature=0.8)


def skeptic(state: CouncilState) -> CouncilState:
    """Skeptic agent - analyzes risks and fact-checks Visionary claims."""
    try:
        print("[agents] Running Skeptic agent")
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your environment or a .env file."
            )

        llm = get_llm(temperature=0.3)
        messages = state.get("messages", [])
        visionary_message = next(
            (message for message in reversed(messages) if message.startswith("Visionary:")),
            messages[-1] if messages else "",
        )
        print(f"[agents] Skeptic reviewing Visionary message: {visionary_message[:200]}...")

        claims = _extract_claims(visionary_message)
        print(f"[agents] Skeptic extracted {len(claims)} claims")

        fact_checks = []
        for claim in claims:
            print(f"[agents] Skeptic searching claim: {claim[:80]}...")
            try:
                search_results = run_web_search(claim)
                fact_checks.append(_format_fact_check(claim, search_results))
            except Exception as exc:
                print(f"[agents] Skeptic search error: {exc}")
                fact_checks.append(f"Claim: {claim}\nSearch error: {exc}")

        conversation = "\n".join(messages)
        llm_prompt = (
            f"{SKEPTIC_PROMPT}\n\n"
            f"Visionary message:\n{visionary_message or 'No Visionary message available.'}\n\n"
            f"Claims to fact-check:\n" + "\n".join(f"- {claim}" for claim in claims) +
            f"\n\nSearch evidence:\n" + "\n\n".join(fact_checks) +
            f"\n\nConversation so far:\n{conversation or 'No prior messages.'}\n\n"
            "Write a skeptical critique that explicitly references the search evidence."
        )

        response = llm.invoke(llm_prompt)
        response_text = getattr(response, "content", str(response))
        print("[agents] Skeptic response received")

        updated_messages = list(messages)
        updated_messages.append(f"Skeptic: {response_text}")
        updated_outputs = dict(state.get("agent_outputs", {}))
        updated_outputs["skeptic"] = response_text
        return {
            **state,
            "messages": updated_messages,
            "agent_outputs": updated_outputs,
            "current_agent": "skeptic",
        }
    except Exception as exc:
        print(f"[agents] Skeptic agent error: {exc}")
        updated_messages = list(state.get("messages", []))
        error_message = f"Skeptic agent error: {exc}"
        updated_messages.append(error_message)
        updated_outputs = dict(state.get("agent_outputs", {}))
        updated_outputs["skeptic"] = error_message
        return {
            **state,
            "messages": updated_messages,
            "agent_outputs": updated_outputs,
            "current_agent": "skeptic",
        }


def pragmatist(state: CouncilState) -> CouncilState:
    """Pragmatist agent - creates an action plan."""
    return _run_agent("Pragmatist", PRAGMATIST_PROMPT, state, temperature=0.5)


def _extract_claims(visionary_message: str) -> list[str]:
    """Extract candidate claims from the Visionary's message."""
    if not visionary_message:
        return ["No Visionary claims were provided."]

    if ":" in visionary_message:
        _, content = visionary_message.split(":", 1)
    else:
        content = visionary_message

    lines = [line.strip("-• \t") for line in content.splitlines() if line.strip()]
    claims: list[str] = []
    for line in lines:
        parts = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", line) if segment.strip()]
        claims.extend(parts or [line])

    cleaned_claims = [claim for claim in claims if len(claim) > 10]
    return cleaned_claims[:3] or [content.strip()]


def _format_fact_check(claim: str, search_results: str | None) -> str:
    """Format Tavily results into a readable fact-check summary.
    
    Args:
        claim: The claim being fact-checked
        search_results: String output from run_web_search() or None
        
    Returns:
        Formatted fact-check text
    """
    lines = [f"Claim: {claim}"]

    if search_results is None:
        lines.append("No search results found.")
        return "\n".join(lines)

    if isinstance(search_results, str):
        # Tavily returns a string representation of results
        # Try to extract meaningful content
        if search_results.strip():
            # Clean up the string - remove extra brackets/quotes
            cleaned = search_results.strip("[]'\"")
            lines.append(f"Search results: {cleaned[:500]}")
        else:
            lines.append("No relevant search results found.")
            
    return "\n".join(lines)