from langgraph.graph import StateGraph, END
from agent.state import GraphState


def prepare_next_chapter(state: GraphState) -> dict:
    """Prepare the next chapter for processing"""
    print("\n--- 📋 PREPARING NEXT CHAPTER ---")
    chapters_to_process = state["chapters_to_process"]

    if chapters_to_process:
        next_chapter = chapters_to_process[0]
        chapter_id = next_chapter["id"]

        # Initialize ChapterWork for this chapter if it doesn't exist
        chapter_works = state.get("chapter_works", {})
        if chapter_id not in chapter_works:
            chapter_works[chapter_id] = {
                "chapter_details": next_chapter,
                "research_results": None,
                "generated_text": None,
                "review_feedback": None,
                "review_decision": None,
                "token_usage": {},
            }

        print(
            f"  - Processing Chapter ID: {chapter_id} - {next_chapter['heading_label']}"
        )

        return {
            "chapters_to_process": chapters_to_process[1:],
            "current_chapter_id": chapter_id,
            "chapter_works": chapter_works,
        }
    return {}


def create_prepare_chapter_graph():
    """Create the prepare chapter subgraph"""
    workflow = StateGraph(GraphState)

    workflow.add_node("prepare", prepare_next_chapter)

    workflow.set_entry_point("prepare")
    workflow.add_edge("prepare", END)

    return workflow.compile()
