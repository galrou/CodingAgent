from langgraph.graph import StateGraph, START, END
from roles import Engineer,QA
from models import AgentState


def create_app(llm):
    # Initialize Roles
    engineer = Engineer(llm)
    qa = QA(llm)

    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("coder", engineer.code_editor)
    workflow.add_node("test_writer", qa.write_tests)
    workflow.add_node("executor", qa.run_tests)

    # Wiring
    workflow.add_edge(START, "coder")
    workflow.add_edge("coder", "test_writer")
    workflow.add_edge("test_writer", "executor")

    # The Decision Logic
    def route_after_test(state):
        if state["is_fixed"]:
            return "end"
        if state.get("retry_count", 0) >= 3:  # ADD THIS - stop after 3 retries
            return "end"
        return "retry"

    workflow.add_conditional_edges(
        "executor",
        route_after_test,
        {"end": END, "retry": "coder"}
    )

    return workflow.compile()