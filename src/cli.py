"""Command-line entry point for Council AI."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_streamlit() -> int:
    """Launch the Streamlit app."""
    project_root = Path(__file__).resolve().parent.parent
    app_path = project_root / "ui" / "app.py"
    command = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    return subprocess.call(command)


def run_evals() -> int:
    """Run the batch evaluation script."""
    project_root = Path(__file__).resolve().parent.parent
    eval_script = project_root / "evals" / "run_evals.py"
    command = [sys.executable, str(eval_script)]
    return subprocess.call(command)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Council AI command-line interface")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("serve", help="Run the Streamlit app")
    subparsers.add_parser("eval", help="Run the batch evaluation pipeline")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "serve":
        return run_streamlit()
    if args.command == "eval":
        return run_evals()

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())