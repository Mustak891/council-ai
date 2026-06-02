# Council AI - Multi-Agent Debate System

## 🎯 Project Goal
Build a multi-agent AI system where specialized agents debate and collaborate to solve problems, demonstrating advanced AI orchestration skills for job hunting in 2026.

## 🏗️ Architecture Overview
- **3 Specialized Agents**: Visionary, Skeptic, Pragmatist
- **Orchestration**: LangGraph for state management
- **Tools**: Web search for fact-checking
- **UI**: Streamlit for real-time visualization
- **Evals**: Quality measurement pipeline

## 📋 Implementation Phases

### Phase 1: Core Setup (Day 1)
- [ ] Initialize Python environment
- [ ] Install dependencies: langgraph, langchain, streamlit, tavily
- [ ] Create basic LangGraph state schema
- [ ] Set up agent prompts

### Phase 2: Agent Development (Day 2)
- [ ] Build Visionary agent (creative brainstorming)
- [ ] Build Skeptic agent (critical analysis + web search tool)
- [ ] Build Pragmatist agent (actionable planning)
- [ ] Implement agent communication flow

### Phase 3: UI & Testing (Day 3)
- [ ] Create Streamlit interface
- [ ] Add real-time agent conversation display
- [ ] Implement consensus output
- [ ] Test with 5 different scenarios

### Phase 4: Polish & Deploy (Day 4)
- [ ] Add evaluation metrics
- [ ] Create README with demo GIF
- [ ] Deploy to Streamlit Cloud
- [ ] Record demo video

## 📁 File Structure

council-ai/
├── PLAN.md
├── README.md
├── requirements.txt
├── src/
│ ├── init.py
│ ├── agents.py
│ ├── graph.py
│ ├── tools.py
│ └── state.py
├── ui/
│ └── app.py
└── tests/
└── test_agents.py


## 🛠️ Tech Stack
- **Python 3.10+**
- **LangGraph** - Agent orchestration
- **LangChain** - LLM integration
- **Streamlit** - Frontend
- **Tavily API** - Web search tool
- **OpenAI/Claude API** - LLM backend

## 🎬 Copilot Instructions
When building, always:
1. Create modular, testable code
2. Add type hints and docstrings
3. Log agent decisions for debugging
4. Handle errors gracefully
5. Keep functions single-responsibility

## 📊 Success Metrics
- Agents complete debate in <30 seconds
- Final output is actionable and specific
- System handles 10+ conversation turns
- Zero infinite loops

