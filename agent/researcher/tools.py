from pathlib import Path
from typing import Dict
from agent.state import ResearcherState
from utils.token_tracker import (
    create_token_usage,
    update_total_tokens,
    print_token_usage,
)
from agent.researcher.knowledge_base import KnowledgeBaseQuerier
from agent.researcher.md_processor import MarkdownProcessor
from agent.researcher.prompt_builder import ResearchPromptBuilder


def research_chapter(state: ResearcherState, llm) -> dict:
    """Main research function that orchestrates all research activities"""
    print("\n--- 🧑‍🔬 EXECUTING RESEARCHER NODE ---")

    # Extract basic info
    chapter_id = state["current_chapter_id"]
    chapter_works = state["chapter_works"]
    current_work = chapter_works[chapter_id]
    current_chapter = current_work["chapter_details"]

    print(f"  - Researching for chapter: {current_chapter['heading_label']}")

    # Step 1: Query Knowledge Base (Semantic Search with OpenAI embeddings)
    kb_results = query_knowledge_base_semantic(current_chapter, state)

    # Step 2: Load research markdown files specified for this chapter
    md_content = load_research_markdown(current_chapter, state)

    # Step 3: Build Research Prompt
    prompt_builder = ResearchPromptBuilder(state, current_chapter, current_work)
    research_prompt = prompt_builder.build_prompt(kb_results, md_content)

    # Step 4: Call LLM
    llm_response = call_llm_for_research(llm, research_prompt, current_chapter)

    # Step 5: Update State
    return update_research_state(state, chapter_id, chapter_works, llm_response)


def query_knowledge_base_semantic(chapter: Dict, state: ResearcherState) -> str:
    """Query the embeddings-based knowledge bases using semantic search"""
    # Primary knowledge base
    kb_path = state.get(
        "knowledge_base_path", "data/knowledge_base/df_with_embeddings_large.parquet"
    )
    # IFRS knowledge base
    ifrs_kb_path = state.get(
        "knowledge_base_additional_path",
        "data/knowledge_base/ifrs_knowledge_base_with_embeddings.parquet",
    )
    embedding_model = state.get("embedding_model", "text-embedding-3-large")

    print("  - Querying knowledge bases:")
    print(f"    • Primary: {kb_path}")
    print(f"    • IFRS: {ifrs_kb_path}")
    print(f"  - Using embedding model: {embedding_model}")

    print(f"  - The input to search: {chapter}")

    # Query primary knowledge base
    kb_querier = KnowledgeBaseQuerier(kb_path, embedding_model)
    primary_results = kb_querier.search(chapter)

    if primary_results:
        print(f"    • Found {len(primary_results)} entries")
        print("    • Similarity scores:")
        for i, result in enumerate(primary_results):
            print(f"      {i+1}. Score: {result['score']:.4f}")

    # Query IFRS knowledge base
    ifrs_kb_querier = KnowledgeBaseQuerier(ifrs_kb_path, embedding_model)
    ifrs_results = ifrs_kb_querier.search(chapter)

    if ifrs_results:
        print(f"    • Found {len(ifrs_results)} entries")
        print("    • Similarity scores:")
        for i, result in enumerate(ifrs_results):
            print(f"      {i+1}. Score: {result['score']:.4f}")

    # Combine results
    all_results = []

    if primary_results:
        print(f"  - Found {len(primary_results)} relevant entries in primary KB")
        # Show top 3 scores from primary
        for i, result in enumerate(primary_results[:5]):
            print(
                f"    • Entry {result['id']}: similarity = {result['score']:.3f} ({result['category_1']})"
            )
        all_results.extend(primary_results)
    else:
        print("  - No relevant entries found in primary knowledge base")

    if ifrs_results:
        print(f"  - Found {len(ifrs_results)} relevant entries in IFRS KB")
        # Show top 3 scores from IFRS
        for i, result in enumerate(ifrs_results[:5]):
            print(
                f"    • IFRS Entry {result['id']}: similarity = {result['score']:.3f} ({result.get('category_1', 'IFRS')})"
            )
        all_results.extend(ifrs_results)
    else:
        print("  - No relevant entries found in IFRS knowledge base")

    # Sort combined results by similarity score (descending)
    if all_results:
        all_results.sort(key=lambda x: x["score"], reverse=True)
        print(f"  - Total combined entries: {len(all_results)}")

        # Format results with source indication
        formatted_primary = kb_querier.format_results(
            [r for r in all_results if r in primary_results]
        )
        formatted_ifrs = ifrs_kb_querier.format_results(
            [r for r in all_results if r in ifrs_results]
        )

        # Combine formatted results with clear separation
        combined_output = ""
        if formatted_primary:
            combined_output += "=== PRIMARY KNOWLEDGE BASE RESULTS ===\n"
            combined_output += formatted_primary + "\n"

        if formatted_ifrs:
            if combined_output:
                combined_output += "\n"
            combined_output += "=== IFRS KNOWLEDGE BASE RESULTS ===\n"
            combined_output += formatted_ifrs

        return combined_output
    else:
        print("  - No relevant entries found in any knowledge base")
        return ""


def load_research_markdown(chapter: Dict, state: ResearcherState) -> str:
    """Load research markdown files specified for this chapter"""
    # Get research files from chapter details
    research_files = chapter.get("research_files", [])

    print(f"  - Loading {len(research_files)} research file(s)")

    md_processor = MarkdownProcessor()
    all_content = []

    # Load each specified markdown file
    for md_file in research_files:
        print(f"  - Processing: {md_file}")

        # Load the file
        content = md_processor.process_research_file(md_file, chapter)

        if content:
            # Format for inclusion in prompt
            formatted_content = md_processor.format_content(content, Path(md_file).name)
            all_content.append(formatted_content)
        else:
            print(f"    • Warning: No content loaded from {md_file}")

    # Combine all content with separators
    if all_content:
        combined_content = "\n\n=== RESEARCH DOCUMENTS ===\n"
        combined_content += "\n".join(all_content)
        combined_content += "\n\n=== END OF RESEARCH DOCUMENTS ===\n"

        total_size = len(combined_content)
        print(f"  - Total research content size: {total_size:,} characters")

        return combined_content
    else:
        print("  - No research content loaded from any file")
        return ""


def call_llm_for_research(llm, research_prompt: str, chapter: Dict) -> Dict:
    """Call the LLM with the research prompt"""
    print("  - Calling LLM for research generation...")
    print(f"  - Target word count: {chapter.get('target_word_count', 500)}")
    print(f"  - Research prompt length: {len(research_prompt):,} characters")

    response = llm.invoke(research_prompt)

    # Extract token usage
    usage_metadata = response.response_metadata.get("token_usage", {})

    return {
        "content": response.content,
        "prompt_tokens": usage_metadata.get("prompt_tokens", 0),
        "completion_tokens": usage_metadata.get("completion_tokens", 0),
    }


def update_research_state(
    state: ResearcherState, chapter_id: str, chapter_works: Dict, llm_response: Dict
) -> Dict:
    """Update the state with research results and token usage"""
    # Create token usage record
    token_usage = create_token_usage(
        llm_response["prompt_tokens"], llm_response["completion_tokens"]
    )
    print_token_usage(token_usage, "Researcher Token Usage")

    # Update chapter work
    chapter_works[chapter_id]["research_results"] = llm_response["content"]
    chapter_works[chapter_id]["token_usage"]["researcher"] = token_usage

    # Update total tokens
    token_updates = update_total_tokens(state, token_usage, "researcher", chapter_id)

    return {"chapter_works": chapter_works, **token_updates}
