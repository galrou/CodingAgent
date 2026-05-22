from typing import Dict, Any, Generator
from langgraph.graph import StateGraph, START, END
from roles.engineer import Engineer  # Adjust imports based on your file structure
from roles.qa import QA
from models import AgentState
from workspace_sandbox import WorkspaceSandbox


class AgentPipeline:
    def __init__(self, llm, sandbox_branch: str = "agent-palindrome-run"):
        # 1. Initialize the sandbox infrastructure layer
        self.sandbox = WorkspaceSandbox(branch_name=sandbox_branch)

        # 2. Inject dependencies into specialized roles correctly
        self.engineer = Engineer(llm, sandbox=self.sandbox)
        self.qa = QA(sandbox=self.sandbox)  # FIX: Passed sandbox instance here instead of llm!

        # 3. Compile the internal state graph
        self.app = self._compile_workflow()

    def _router(self, state: AgentState) -> str:
        """Determines whether to retry or finish based on validation metrics."""
        if state.get("is_fixed", False):
            return "end"
        if state.get("retry_count", 0) >= 3:
            print("[Pipeline] Max retries reached. Exiting graph.")
            return "end"
        return "retry"

    def _compile_workflow(self) -> StateGraph:
        """Assembles the modular nodes into a stateful execution loop."""
        workflow = StateGraph(AgentState)

        # Register execution steps mapping to our class methods
        workflow.add_node("coder", self.engineer.write_code)
        workflow.add_node("test_writer", self.qa.write_tests)

        # Set entry point
        workflow.add_edge(START, "coder")
        workflow.add_edge("coder", "test_writer")

        # Set up self-correction conditional feedback loop
        workflow.add_conditional_edges(
            "test_writer",
            self._router,
            {
                "end": END,
                "retry": "coder"
            }
        )

        return workflow.compile()

    def run(self, initial_input: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Deploys an isolated workspace environment, streams graph execution events,
        and guarantees cleanup operations upon termination.
        """
        try:
            # 1. Spin up the git worktree before processing nodes
            self.sandbox.create()

            # 2. Stream execution steps directly to your main program runner
            for event in self.app.stream(initial_input):
                yield event

        finally:
            # 3. CRITICAL: Guarantee workspace teardown even if compilation or execution crashes
            self.sandbox.cleanup()