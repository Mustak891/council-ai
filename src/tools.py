"""External tool helpers for Council AI."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Force load .env from project root BEFORE any tool initialization
load_dotenv(Path(__file__).parent.parent / ".env")

# Now import other modules
try:
    from langchain_community.tools import TavilySearchResults
    from langchain_core.tools import BaseTool
    
    # Initialize Tavily if API key is available
    if os.getenv("TAVILY_API_KEY"):
        web_search_tool: BaseTool = TavilySearchResults(max_results=3)
        print("[tools] ✅ Tavily web search enabled")
    else:
        web_search_tool = None
        print("[tools] ️ Tavily disabled (no API key)")
except ImportError:
    web_search_tool = None
    print("[tools] ⚠️ Tavily not available (langchain-community not installed)")


def run_web_search(query: str) -> str | None:
    """Run web search for fact-checking.
    
    Args:
        query: Search query string
        
    Returns:
        Search results as string, or None if tool unavailable
    """
    if web_search_tool is None:
        return None
    
    try:
        results = web_search_tool.invoke(query)
        return str(results)
    except Exception as e:
        print(f"[tools] Search error: {e}")
        return None