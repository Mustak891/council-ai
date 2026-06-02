import time

from src import agents
from src.graph import build_council_graph


class DummyResponse:
    def __init__(self, content: str):
        self.content = content


class DummyLLM:
    def __init__(self, model: str, temperature: float):
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt: str):
        if "Visionary" in prompt:
            content = "Visionary response: " + "Bold idea. " * 10
        elif "Skeptic" in prompt:
            content = "Skeptic response: " + "Evidence suggests caution. " * 8
        else:
            content = "Pragmatist response: " + "Step 1. Step 2. Step 3. " * 8
        return DummyResponse(content)


def fake_search(query: str):
    return [{"title": "Source A", "content": f"Evidence for {query}", "url": "https://example.com"}]


def make_state(prompt: str = "Build a study plan"):
    return {
        "prompt": prompt,
        "messages": [f"User: {prompt}"],
        "agent_outputs": {},
        "debate_rounds": 0,
        "current_agent": "",
        "turn_count": 0,
        "max_turns": 3,
        "consensus": "",
        "consensus_confidence": 0.0,
    }


def test_agent_response_time_under_ten_seconds(monkeypatch):
    monkeypatch.setattr(agents, "ChatGroq", DummyLLM)
    monkeypatch.setattr(agents, "run_web_search", fake_search)

    state = make_state()
    start = time.perf_counter()
    visionary_state = agents.visionary(state)
    skeptic_state = agents.skeptic(visionary_state)
    pragmatist_state = agents.pragmatist(skeptic_state)
    elapsed = time.perf_counter() - start

    assert elapsed < 10
    assert pragmatist_state["messages"][-1].startswith("Pragmatist:")


def test_response_length_reasonable(monkeypatch):
    monkeypatch.setattr(agents, "ChatGroq", DummyLLM)
    monkeypatch.setattr(agents, "run_web_search", fake_search)

    state = make_state()
    visionary_state = agents.visionary(state)
    response_text = visionary_state["agent_outputs"]["visionary"]

    assert 50 <= len(response_text) <= 1000


def test_consensus_generation(monkeypatch):
    monkeypatch.setattr(agents, "ChatGroq", DummyLLM)
    monkeypatch.setattr(agents, "run_web_search", fake_search)

    graph = build_council_graph()
    result = graph.invoke(make_state())

    assert result["consensus"]


def test_confidence_score_in_range(monkeypatch):
    monkeypatch.setattr(agents, "ChatGroq", DummyLLM)
    monkeypatch.setattr(agents, "run_web_search", fake_search)

    graph = build_council_graph()
    result = graph.invoke(make_state())

    confidence = result["consensus_confidence"]
    assert 0.0 <= confidence <= 1.0
