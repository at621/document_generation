from langgraph.graph import StateGraph, END
from agent.state import GraphState
from agent.save_chapter.tools import save_accepted_chapter


def create_save_chapter_graph():
    """Create the save chapter subgraph"""
    workflow = StateGraph(GraphState)

    workflow.add_node("save", save_accepted_chapter)

    workflow.set_entry_point("save")
    workflow.add_edge("save", END)

    return workflow.compile()
