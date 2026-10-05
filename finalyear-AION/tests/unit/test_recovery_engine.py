from backend.recovery.recovery_engine import RecoveryEngine


def test_recovery_for_missing_destination():
    engine = RecoveryEngine()
    result = engine.recover("move_file", {"destination": "tmp/a/b/file.txt"}, "missing dir")
    assert result["status"] in {"RECOVERED", "FAILED"}
