from backend.services.llm.interpreter import GoalInterpreter


def test_goal_interpreter_pdf_goal():
    interpreter = GoalInterpreter(provider=None)
    # Pattern 1 (create folder) matches first for this goal
    output = interpreter.interpret("Create a folder called AION_Demo in Downloads")
    actions = [t.action for t in output.tasks]
    assert "create_folder" in actions
    assert "verify" in actions
    
    # Pattern 2 (PDF workflow) requires specific PDF keywords
    output2 = interpreter.interpret("Download PDFs and organize into folders")
    actions2 = [t.action for t in output2.tasks]
    # Should trigger pattern 2 or default pattern
    assert len(actions2) > 0
