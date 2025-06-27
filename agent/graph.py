from langgraph.graph import StateGraph, END
from IPython.display import Image, display

from agent.state import GraphState
from agent.workflow_router.graph import (
    route_master_router,
)
from agent.prepare_chapter.graph import create_prepare_chapter_graph
from agent.researcher.graph import create_researcher_graph
from agent.writer.graph import create_writer_graph
from agent.reviewer.graph import create_reviewer_graph
from agent.save_chapter.graph import create_save_chapter_graph
from agent.final_assembler.graph import create_final_assembler_graph


def create_document_generation_graph():
    """Create the main document generation graph by composing subgraphs"""

    # Create main workflow
    workflow = StateGraph(GraphState)

    # Add nodes (each node is a compiled subgraph)
    workflow.add_node("workflow_router", lambda state: state)  # Simple router node
    workflow.add_node("prepare_next_chapter", create_prepare_chapter_graph())
    workflow.add_node("researcher", create_researcher_graph())
    workflow.add_node("writer", create_writer_graph())
    workflow.add_node("reviewer", create_reviewer_graph())
    workflow.add_node("save_chapter", create_save_chapter_graph())
    workflow.add_node("final_assembler", create_final_assembler_graph())

    # Set entry point
    workflow.set_entry_point("workflow_router")

    # Add edges and conditional edges
    workflow.add_conditional_edges(
        "workflow_router",
        route_master_router,
        {"continue_loop": "prepare_next_chapter", "finish_process": "final_assembler"},
    )

    workflow.add_edge("prepare_next_chapter", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "reviewer")

    # Conditional edge after review
    def route_after_review_main(state: GraphState) -> str:
        chapter_id = state["current_chapter_id"]
        current_work = state["chapter_works"][chapter_id]

        if current_work["review_decision"] == "accept":
            return "proceed"
        else:
            return "rewrite"

    workflow.add_conditional_edges(
        "reviewer",
        route_after_review_main,
        {"proceed": "save_chapter", "rewrite": "researcher"},
    )

    workflow.add_edge("save_chapter", "workflow_router")
    workflow.add_edge("final_assembler", END)

    return workflow.compile()


def visualize_graph(app):
    """Visualize the compiled graph"""
    print("🎨 Visualizing graph...")
    display(Image(app.get_graph().draw_mermaid_png()))
