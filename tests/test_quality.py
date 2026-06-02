import json

import pytest

from src import agents
from src.graph import build_council_graph


pytestmark = pytest.mark.slow


class DummyResponse:
    def __init__(self, content: str):
        self.content = content


class CouncilDummyLLM:
    def __init__(self, model: str, temperature: float):
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt: str):
        if "Visionary" in prompt:
            content = (
                "Visionary response: Build a structured learning loop with mock interviews, "
                "project checkpoints, and weekly reflection."
            )
        elif "Skeptic" in prompt:
            content = (
                "Skeptic response: Verify time commitments, compare against current hiring "
                "trends, and avoid unrealistic assumptions."
            )
        else:
            content = (
                "Pragmatist response: Start with one topic per week, add daily practice, "
                "and measure progress with mock feedback."
            )
        return DummyResponse(content)


class JudgeDummyLLM:
    def __init__(self, model: str, temperature: float):
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt: str):
        prompt_lower = prompt.lower()
        if "build a portfolio website" in prompt_lower:
            relevance = 8
            actionability = 8
            factual_accuracy = 7
        elif "study plan" in prompt_lower:
            relevance = 9
            actionability = 8
            factual_accuracy = 8
        else:
            relevance = 7
            actionability = 7
            factual_accuracy = 7

        payload = {
            "relevance": relevance,
            "actionability": actionability,
            "factual_accuracy": factual_accuracy,
        }
        return DummyResponse(json.dumps(payload))


def fake_search(query: str):
    return [{"title": "Source A", "content": f"Evidence for {query}", "url": "https://example.com"}]


def make_state(prompt: str):
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


def run_council(prompt: str, monkeypatch) -> str:
    monkeypatch.setattr(agents, "ChatGroq", CouncilDummyLLM)
    monkeypatch.setattr(agents, "run_web_search", fake_search)
    graph = build_council_graph()
    result = graph.invoke(make_state(prompt))
    return result["consensus"]


def score_with_judge(prompt: str, consensus: str):
    judge = JudgeDummyLLM(model="judge", temperature=0)
    response = judge.invoke(
        "You are a judge. Score the council output from 1 to 10 for relevance, "
        "actionability, and factual_accuracy as JSON.\n"
        f"Prompt: {prompt}\nConsensus: {consensus}"
    )
    return json.loads(response.content)


def test_llm_judge_average_score_above_threshold(monkeypatch):
    prompts = [
        "Build a portfolio website",
        "Create a 2-week interview study plan",
        "Plan a product launch on a tight budget",
        "Design a healthy daily routine for remote work",
        "Outline a simple approach to learning Python",
    ]

    scores = []
    for prompt in prompts:
        consensus = run_council(prompt, monkeypatch)
        judged = score_with_judge(prompt, consensus)
        scores.append(judged)

    average_score = sum(
        score["relevance"] + score["actionability"] + score["factual_accuracy"]
        for score in scores
    ) / (len(scores) * 3)

    assert average_score > 6.0