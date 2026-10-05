from backend.agents.browser_agent import BrowserAgent


def test_browser_agent_has_search_method():
    agent = BrowserAgent()
    assert hasattr(agent, "search_web")
