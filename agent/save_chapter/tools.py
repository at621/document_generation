from agent.state import GraphState
from utils.token_tracker import create_token_usage, print_token_usage


def save_accepted_chapter(state: GraphState) -> dict:
    """Save an accepted chapter"""
    print("\n--- ✅ SAVING ACCEPTED CHAPTER ---")
    chapter_id = state["current_chapter_id"]
    chapter_works = state["chapter_works"]
    current_work = chapter_works[chapter_id]

    # Calculate total tokens for this chapter
    chapter_total_usage = create_token_usage(0, 0)
    for operation, usage in current_work["token_usage"].items():
        chapter_total_usage["prompt_tokens"] += usage["prompt_tokens"]
        chapter_total_usage["completion_tokens"] += usage["completion_tokens"]
        chapter_total_usage["total_tokens"] += usage["total_tokens"]
        chapter_total_usage["input_cost"] += usage["input_cost"]
        chapter_total_usage["output_cost"] += usage["output_cost"]
        chapter_total_usage["total_cost"] += usage["total_cost"]

    print_token_usage(chapter_total_usage, f"Chapter {chapter_id} Total Token Usage")

    # Save the complete ChapterWork to completed_chapters
    saved_chapter_data = {
        "details": current_work["chapter_details"],
        "text": current_work["generated_text"],
        "full_work": current_work,
        "chapter_token_summary": chapter_total_usage,
    }

    updated_completed = {
        **state.get("completed_chapters", {}),
        chapter_id: saved_chapter_data,
    }

    return {"completed_chapters": updated_completed}
