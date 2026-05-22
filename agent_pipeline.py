import sys
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from roles import Engineer, QA
from models import AgentState
from workspace_sandbox import WorkspaceSandbox

class AgentPipeline:
    def __init__(self, llm, sandbox_branch: str = "agent-active-run"):
        self.sandbox = WorkspaceSandbox(branch_name=sandbox_branch)
        self.engineer = Engineer(llm)
        self.qa = QA(llm)
        self.app = self._compile_workflow()

    def _compile_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("init_env", self._init_env_node)
        workflow.add_node("coder", self.engineer.code_editor)
        workflow.add_node("test_writer", self.qa.write_tests)
        workflow.add_node("executor", self._execute_tests_node)  # <--- Handled by pipeline

        workflow.add_edge(START, "init_env")
        workflow.add_edge("init_env", "coder")
        workflow.add_edge("coder", "test_writer")
        workflow.add_edge("test_writer", "executor")

        workflow.add_conditional_edges(
            "executor",
            self._route_after_test,
            {"end": END, "retry": "coder"}
        )

        return workflow.compile()

    def _init_env_node(self, state: AgentState) -> AgentState:
        state["sandbox_path"] = self.sandbox.create()
        return state

    def _execute_tests_node(self, state: AgentState) -> AgentState:
        print("---QA: Executing Tests inside Sandbox---")
        execution = self.sandbox.run_tests(
            test_command=f'"{sys.executable}" -m pytest',
            timeout_seconds=15
        )

        return {
            "terminal_output": execution["output"],
            "is_fixed": execution["success"],
            "retry_count": state.get("retry_count", 0) + 1
        }

    def _route_after_test(self, state: AgentState) -> str:
        if state["is_fixed"]:
            print("[Pipeline] Tests Passed! Task completed successfully.")
            return "end"
        if state.get("retry_count", 0) >= 3:
            print("[Pipeline] Maximum retries reached. Exiting graph.")
            return "end"
        print(f"[Pipeline] Tests Failed. Incrementing retry loop count: {state.get('retry_count')}")
        return "retry"

    def run(self, initial_input: Dict[str, Any]):
        try:
            for event in self.app.stream(initial_input):
                yield event
        finally:
            self.sandbox.cleanup()