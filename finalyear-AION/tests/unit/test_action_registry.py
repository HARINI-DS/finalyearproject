from backend.security.action_registry import AllowedActionRegistry


def test_action_registry_contains_expected_actions():
    registry = AllowedActionRegistry()
    assert registry.is_allowed("create_folder")
    assert registry.is_allowed("move_files")
    assert not registry.is_allowed("run_powershell")
