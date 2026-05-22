from typing import Dict, Any, List
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # Core Task Info
    task_description: str
    current_file_path: str

    # Execution Tracking
    code_history: List[str]
    terminal_output: str
    error_summary: str

    # Control Flow State
    retry_count: int
    is_fixed: bool