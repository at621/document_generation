from langgraph.graph import StateGraph, END
from agent.state import ReviewerState
from agent.reviewer.tools import review_chapter
from utils.llm_config import get_llm


def route_after_review(state: ReviewerState) -> str:
    """Route based on review decision"""
    print("\n--- 🗺️ ROUTING: After Review ---")
    chapter_id = state["current_chapter_id"]
    current_work = state["chapter_works"][chapter_id]

    if current_work["review_decision"] == "accept":
        print("  - Decision: Chapter accepted.")
        return "accept"
    else:
        print("  - Decision: Chapter rejected.")
        return "reject"


def create_reviewer_graph():
    """Create the reviewer subgraph"""
    workflow = StateGraph(ReviewerState)

    llm = get_llm()

    def reviewer_node(state: ReviewerState) -> dict:
        return review_chapter(state, llm)

    workflow.add_node("review", reviewer_node)

    workflow.set_entry_point("review")
    workflow.add_conditional_edges(
        "review", route_after_review, {"accept": END, "reject": END}
    )

    return workflow.compile()
