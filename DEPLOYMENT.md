# Deployment Guide

## Streamlit Cloud

1. Push this repository to GitHub.
2. Create a new app in Streamlit Cloud.
3. Connect the GitHub repository.
4. Set the main file path to `ui/app.py`.
5. Add these secrets in Streamlit Cloud:
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`
6. Deploy the app.

## Environment Variables

Required:
- `GROQ_API_KEY`: Groq API key for the debate agents.
- `TAVILY_API_KEY`: Tavily API key for live fact-checking in the Skeptic agent.

Optional:
- `STREAMLIT_WATCHER_TYPE=poll`: helps avoid some Windows watcher issues during local development.

## Local Deployment Check

```bash
pip install -r requirements.txt
streamlit run ui/app.py
```

Or use the CLI entry point after installation:

```bash
council-ai serve
```

## Common Issues

### Missing API keys
If the app shows API key errors, confirm both `GROQ_API_KEY` and `TAVILY_API_KEY` are set in Streamlit Cloud or your local shell.

### Favicon not loading
Ensure `assets/favicon.svg` exists and that both `.streamlit/config.toml` and `ui/app.py` point to it.

### Streamlit fails on Windows shutdown
`ui/app.py` already sets `STREAMLIT_WATCHER_TYPE=poll` to reduce watcher-related shutdown crashes.

### Dependency mismatch
If deployment fails after a dependency update, reinstall with a clean environment and confirm `requirements.txt` matches `pyproject.toml`.
