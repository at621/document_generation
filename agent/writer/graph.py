from langgraph.graph import StateGraph, END
from agent.state import WriterState
from agent.writer.tools import write_chapter
from utils.llm_config import get_llm


def create_writer_graph():
    """Create the writer subgraph"""
    workflow = StateGraph(WriterState)

    llm = get_llm()

    def writer_node(state: WriterState) -> dict:
        return write_chapter(state, llm)

    workflow.add_node("write", writer_node)

    workflow.set_entry_point("write")
    workflow.add_edge("write", END)

    return workflow.compile()
