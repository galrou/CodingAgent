from typing import Dict, Any
from models import AgentState
from workspace_sandbox import WorkspaceSandbox


class QA:
    def __init__(self, sandbox: WorkspaceSandbox):
        self.sandbox = sandbox

    def write_tests(self, state: AgentState) -> Dict[str, Any]:
        print(f"[QA] Running validation suite on {state['current_file_path']}...")

        # Execute tests via our isolated sandbox environment layer
        run_results = self.sandbox.run_tests(test_target=state['current_file_path'])

        # ---------- FIXED HERE ----------
        # Changed from "terminal_output" to "output"
        terminal_log = run_results.get("output", "")
        # Changed from "is_fixed" to "success"
        is_successful = run_results.get("success", False)
        # --------------------------------

        # Extract a clean snippet of the error traceback if it exists
        error_lines = []

        # If execution wasn't successful, log what went wrong
        if not is_successful:
            if terminal_log:
                error_lines = terminal_log.splitlines()[-15:]
            else:
                error_lines = ["Execution finished with an error, but terminal output was completely empty."]

        # Return the exact state fields your langgraph workflow state expects
        return {
            "terminal_output": terminal_log,
            "error_summary": "\n".join(error_lines),
            "is_fixed": is_successful,
            "retry_count": state.get("retry_count", 0) + (0 if is_successful else 1)
        }