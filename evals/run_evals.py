"""Batch evaluation runner for Council AI."""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.graph import build_council_graph

load_dotenv()


PROMPTS = [
    "Build a portfolio website for a machine learning engineer.",
    "Create a 2-week study plan for a technical interview.",
    "Plan a product launch for a new productivity app on a small budget.",
    "Design a healthy daily routine for a remote worker.",
    "Outline a simple approach to learning Python from scratch.",
    "Recommend a content strategy for a solo founder.",
    "Propose a debugging workflow for a failing production service.",
    "Create a webinar promotion plan for a B2B startup.",
    "Draft a career transition plan from operations to data analysis.",
    "Suggest a 30-day plan to improve public speaking confidence.",
]


@dataclass
class EvaluationRow:
    prompt: str
    consensus: str
    relevance: float
    actionability: float
    factual_accuracy: float
    timestamp: str


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


def require_api_keys() -> None:
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your environment or .env file.")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY is not set. Add it to your environment or .env file.")


def judge_consensus(prompt: str, consensus: str) -> dict[str, float]:
    judge_llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)
    judge_prompt = (
        "You are an evaluation judge. Return only JSON with keys relevance, actionability, "
        "and factual_accuracy, each scored 1-10.\n"
        f"Prompt: {prompt}\n"
        f"Consensus: {consensus}\n"
        "JSON only."
    )
    response = judge_llm.invoke(judge_prompt)
    text = getattr(response, "content", str(response)).strip()
    if text.startswith("```"):
        text = text.strip("`")
    data = json.loads(text)
    return {
        "relevance": float(data["relevance"]),
        "actionability": float(data["actionability"]),
        "factual_accuracy": float(data["factual_accuracy"]),
    }


def run_batch(output_path: Path) -> list[EvaluationRow]:
    require_api_keys()
    graph = build_council_graph()
    rows: list[EvaluationRow] = []

    for prompt in PROMPTS:
        timestamp = datetime.utcnow().isoformat()
        result = graph.invoke(make_state(prompt))
        scores = judge_consensus(prompt, result.get("consensus", ""))
        rows.append(
            EvaluationRow(
                prompt=prompt,
                consensus=result.get("consensus", ""),
                relevance=scores["relevance"],
                actionability=scores["actionability"],
                factual_accuracy=scores["factual_accuracy"],
                timestamp=timestamp,
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["prompt", "consensus", "relevance", "actionability", "factual_accuracy", "timestamp"])
        for row in rows:
            writer.writerow([
                row.prompt,
                row.consensus,
                f"{row.relevance:.2f}",
                f"{row.actionability:.2f}",
                f"{row.factual_accuracy:.2f}",
                row.timestamp,
            ])

    return rows


def print_summary(rows: list[EvaluationRow]) -> None:
    relevance_scores = [row.relevance for row in rows]
    actionability_scores = [row.actionability for row in rows]
    factual_scores = [row.factual_accuracy for row in rows]

    print("Evaluation summary")
    print(f"  Prompts evaluated: {len(rows)}")
    print(f"  Average relevance: {mean(relevance_scores):.2f}")
    print(f"  Average actionability: {mean(actionability_scores):.2f}")
    print(f"  Average factual accuracy: {mean(factual_scores):.2f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Council AI batch evaluations.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional CSV output path. Defaults to evals/results/council_eval_<timestamp>.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output:
        output_path = Path(args.output)
    else:
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / "results" / f"council_eval_{stamp}.csv"

    rows = run_batch(output_path)
    print(f"Wrote evaluation CSV to {output_path}")
    print_summary(rows)


if __name__ == "__main__":
    main()