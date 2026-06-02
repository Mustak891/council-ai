import pytest


@pytest.fixture(autouse=True)
def set_dummy_api_keys(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")