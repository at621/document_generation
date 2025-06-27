from langgraph.graph import StateGraph, END
from agent.state import GraphState
from agent.final_assembler.tools import assemble_final_document


def create_final_assembler_graph():
    """Create the final assembler subgraph"""
    workflow = StateGraph(GraphState)

    workflow.add_node("assemble", assemble_final_document)

    workflow.set_entry_point("assemble")
    workflow.add_edge("assemble", END)

    return workflow.compile()
