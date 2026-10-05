"""Test interpreter pattern matching directly"""
from backend.services.llm.interpreter import GoalInterpreter
from pathlib import Path

interpreter = GoalInterpreter()

# Test delete goal
goal = "Delete the DeleteMe_Test folder in Downloads"
print(f"Goal: {goal}")

try:
    result = interpreter.interpret(goal)
    print(f"Interpretation: {result}")
    print(f"Tasks: {len(result.tasks)}")
    for task in result.tasks:
        print(f"  - {task.action}: {task.parameters}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
