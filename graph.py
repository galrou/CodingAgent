from langgraph.graph import StateGraph, START, END
from models import AgentState
from agent import Agent

def create_app(api_key: str):
    # Initialize our OOP Agent
    agent = Agent(model_name="llama-3.3-70b-versatile", api_key=api_key)

    workflow = StateGraph(AgentState)

    # 1. Add All Nodes
    workflow.add_node("coder", agent.code_editor)
    workflow.add_node("test_writer", agent.test_writer)
    workflow.add_node("executor", agent.executor)
    workflow.add_node("documenter", agent.documenter)
    workflow.add_node("saver", agent.file_saver)

    # 2. Define the Linear Flow
    workflow.add_edge(START, "coder")
    workflow.add_edge("coder", "test_writer")
    workflow.add_edge("test_writer", "executor")

    # 3. Define Logic for Redoing vs. Finishing
    def decide_to_end(state: AgentState):
        if state["is_fixed"]:
            return "document"
        return "retry"

    # Route based on the REAL terminal output from the executor
    workflow.add_conditional_edges(
        "executor",
        decide_to_end,
        {
            "document": "documenter",
            "retry": "coder"
        }
    )

    # 4. Final Cleanup Steps
    workflow.add_edge("documenter", "saver")
    workflow.add_edge("saver", END)

    return workflow.compile()