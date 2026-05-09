from typing import TypedDict


class AgentState(TypedDict):
    task: str
    code: str
    tests: str          # New: The test code
    terminal_output: str # New: Real output from running the code
    test_results: str    # Pass/Fail
    is_fixed: bool