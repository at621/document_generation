from typing import Dict
from agent.state import ResearcherState


def prepare_node(state: ResearcherState) -> Dict:
    """Extract chapter info and prepare for searching"""

    print("\n--- 📋 PREPARE NODE ---")

    # Get current chapter
    chapter_id = state["current_chapter_id"]
    chapter_works = state["chapter_works"]
    current_work = chapter_works[chapter_id]
    current_chapter = current_work["chapter_details"]

    print(f"  - Preparing research for: {current_chapter['heading_label']}")
    print(f"  - Target word count: {current_chapter.get('target_word_count', 500)}")

    # Just pass along the chapter info - keep it simple
    return {"current_chapter": current_chapter, "current_work": current_work}
