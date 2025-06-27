from typing import Dict
from agent.state import ResearcherState
from agent.researcher.prompt_builder import ResearchPromptBuilder
from utils.llm_config import get_llm
from utils.token_tracker import (
    create_token_usage,
    update_total_tokens,
    print_token_usage,
)


def format_research_node(state: ResearcherState) -> Dict:
    """Format all search results and call LLM to generate research"""

    print("\n--- 📝 FORMAT RESEARCH NODE ---")

    chapter = state["current_chapter"]
    current_work = state["current_work"]
    raw_results = state["raw_search_results"]

    # Combine all search results into formatted sections
    research_content = []

    if raw_results["web"]:
        research_content.append("=== WEB SEARCH RESULTS ===")
        research_content.append(raw_results["web"])
        research_content.append("")

    if raw_results["kb_primary"]:
        research_content.append("=== PRIMARY KNOWLEDGE BASE ===")
        research_content.append(raw_results["kb_primary"])
        research_content.append("")

    if raw_results["kb_ifrs"]:
        research_content.append("=== IFRS KNOWLEDGE BASE ===")
        research_content.append(raw_results["kb_ifrs"])
        research_content.append("")

    if raw_results["documents"]:
        research_content.append("=== RESEARCH DOCUMENTS ===")
        research_content.append(raw_results["documents"])
        research_content.append("")

    combined_research = "\n".join(research_content)

    # Build prompt using existing prompt builder
    prompt_builder = ResearchPromptBuilder(state, chapter, current_work)
    research_prompt = prompt_builder.build_prompt(combined_research)

    print(f"  - Research content size: {len(combined_research):,} characters")
    print(f"  - Final prompt size: {len(research_prompt):,} characters")

    # Call LLM
    print("  - Calling LLM for research generation...")
    llm = get_llm()
    response = llm.invoke(research_prompt)

    # Extract token usage
    usage_metadata = response.response_metadata.get("token_usage", {})
    token_usage = create_token_usage(
        usage_metadata.get("prompt_tokens", 0),
        usage_metadata.get("completion_tokens", 0),
    )
    print_token_usage(token_usage, "Researcher Token Usage")

    # Update state
    chapter_id = state["current_chapter_id"]
    chapter_works = state["chapter_works"]

    chapter_works[chapter_id]["research_results"] = response.content
    chapter_works[chapter_id]["token_usage"]["researcher"] = token_usage

    # Update total tokens
    token_updates = update_total_tokens(state, token_usage, "researcher", chapter_id)

    return {
        "chapter_works": chapter_works,
        "research_results": response.content,
        **token_updates,
    }
