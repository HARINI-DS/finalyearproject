from backend.agents.application_agent import ApplicationAgent


def test_application_not_found():
    agent = ApplicationAgent()
    try:
        agent.open_application("definitely-not-installed-app")
    except FileNotFoundError:
        assert True
    else:
        assert False
