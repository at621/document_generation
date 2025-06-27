from langgraph.graph import StateGraph, END
from agent.state import GraphState


def route_master_router(state: GraphState) -> str:
    """Determine whether to continue processing chapters or finish"""
    print("\n--- 🗺️ ROUTING: Master Router ---")
    if state["chapters_to_process"]:
        print("  - Decision: Chapters remaining. Continue generation loop.")
        return "continue_loop"
    else:
        print("  - Decision: No chapters remaining. Proceed to final assembly.")
        return "finish_process"


def create_workflow_router_graph():
    """Create the workflow router subgraph"""
    workflow = StateGraph(GraphState)

    # Simple pass-through node
    workflow.add_node("route", lambda state: {})

    workflow.set_entry_point("route")
    workflow.add_conditional_edges(
        "route", route_master_router, {"continue_loop": END, "finish_process": END}
    )

    return workflow.compile()
