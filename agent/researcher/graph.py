from langgraph.graph import StateGraph, END
from agent.state import ResearcherState
from agent.researcher.nodes.prepare import prepare_node
from agent.researcher.nodes.search_all import search_all_node
from agent.researcher.nodes.format_research import format_research_node


def create_researcher_graph():
    """Simple 3-node researcher graph"""

    workflow = StateGraph(ResearcherState)

    # Add our 3 nodes
    workflow.add_node("prepare", prepare_node)
    workflow.add_node("search_all", search_all_node)
    workflow.add_node("format_research", format_research_node)

    # Simple linear flow
    workflow.set_entry_point("prepare")
    workflow.add_edge("prepare", "search_all")
    workflow.add_edge("search_all", "format_research")
    workflow.add_edge("format_research", END)

    return workflow.compile()
