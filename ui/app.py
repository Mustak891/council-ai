# Fix Windows threading crash on shutdown
import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "poll"
import sys
import time
from pathlib import Path

# Fix the import path - this tells Python where to find the src folder
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from src.graph import build_council_graph
from src.state import CouncilState

st.set_page_config(page_title="Council AI Demo", page_icon="assets/favicon.svg")
st.title("Council AI - Multi-Agent Debate Demo")

prompt = st.text_input(
    "Prompt",
    "How should I prepare for a technical interview?",
    placeholder="Enter your question or topic...",
    help="Please enter at least 5 characters",
)

prompt_length = len(prompt.strip()) if prompt else 0
st.caption(f"Character count: {prompt_length}")

if not prompt or not prompt.strip():
    st.error("⚠️ Please enter a valid prompt to debate")
    st.stop()

if prompt_length < 5:
    st.warning("⚠️ Please enter at least 5 characters for a meaningful debate")
    st.stop()

thinking_placeholder = st.empty()
progress_placeholder = st.empty()
output_placeholder = st.container()


def show_thinking_animation() -> None:
    """Render a small thinking animation while the agents run."""
    frames = ["Thinking.", "Thinking..", "Thinking..."]
    for frame in frames:
        thinking_placeholder.info(frame)
        time.sleep(0.2)


def render_progress(round_number: int, max_rounds: int) -> None:
    """Render the debate progress bar and current round label."""
    progress_value = round_number / max_rounds if max_rounds else 0
    progress_placeholder.progress(progress_value, text=f"Debate Progress: Round {round_number}/{max_rounds}")


if st.button("Run debate"):
    print("[ui] Run debate clicked")
    graph = build_council_graph()
    state: CouncilState = {
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

    with st.spinner("🤖 Council is debating..."):
        show_thinking_animation()

        latest_state = state
        for step_index, event in enumerate(graph.stream(state, stream_mode="values"), start=1):
            latest_state = event
            print(f"[ui] State transition {step_index}: round={latest_state.get('debate_rounds', 0)}, turns={latest_state.get('turn_count', 0)}")
            current_round = max(1, latest_state.get("debate_rounds", 0))
            render_progress(min(current_round, latest_state.get("max_turns", 3)), latest_state.get("max_turns", 3))

            messages = latest_state.get("messages", [])
            if messages:
                last_message = messages[-1]
                if last_message.startswith("Visionary:"):
                    st.info(last_message)
                elif last_message.startswith("Skeptic:"):
                    st.warning(last_message)
                elif last_message.startswith("Pragmatist:"):
                    st.success(last_message)

        with output_placeholder:
            st.subheader("Final Consensus")
            st.write(latest_state.get("consensus", "No consensus returned."))
            st.caption(
                f"Confidence score: {latest_state.get('consensus_confidence', 0.0):.2f}"
            )

    thinking_placeholder.empty()
    render_progress(latest_state.get("debate_rounds", 1), latest_state.get("max_turns", 3))
else:
    st.write("Enter a prompt and click 'Run debate' to see the agent debate.")