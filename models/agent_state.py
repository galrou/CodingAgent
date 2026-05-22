from typing import TypedDict


class AgentState(TypedDict):
    task: str
    code: str
    tests: str
    terminal_output: str
    test_results: str
    is_fixed: bool
    retry_count: int
    sandbox_path: str