from typing import Dict, List
from pathlib import Path
import anthropic
from agent.state import ResearcherState
from agent.researcher.knowledge_base import KnowledgeBaseQuerier
from agent.researcher.md_processor import MarkdownProcessor
import ast


# Initialize Anthropic client
client = anthropic.Anthropic()


def search_all_node(state: ResearcherState) -> Dict:
    """Single node that does ALL searching"""

    print("\n--- 🔍 SEARCH ALL NODE ---")

    chapter = state["current_chapter"]
    chapter_id = state["current_chapter"]["id"]

    # TODO: review chapter structure, overlapping info

    # Create a simple search query from purpose and key topics
    purpose_text = " ".join(chapter.get("purpose", []))
    key_topics_text = " ".join(chapter.get("key_topics", []))

    search_query = f"Purpose: {purpose_text}\n\nKey topics: {key_topics_text}"

    # Check if we already have web search results for this chapter
    cached_web_results = state.get("cached_web_results", {})

    # 1. Web Search (with caching)
    if chapter_id in cached_web_results:
        print("  - Using cached web search results")
        web_results = cached_web_results[chapter_id]
    else:
        print("  - Performing web search...")
        web_results = perform_web_search(search_query)
        # Cache the results
        cached_web_results[chapter_id] = web_results

    # Initialize results container
    all_results = {"web": "", "kb_primary": "", "kb_ifrs": "", "documents": ""}

    # 1. Web Search
    print("  - Performing web search...")
    all_results["web"] = format_web_results(web_results)

    # 2. Primary KB Search
    print("  - Searching primary knowledge base...")
    primary_kb_path = state.get(
        "knowledge_base_path", "data/knowledge_base/df_with_embeddings_large.parquet"
    )
    embedding_model = state.get("embedding_model", "text-embedding-3-large")

    primary_querier = KnowledgeBaseQuerier(primary_kb_path, embedding_model)
    primary_results = primary_querier.search(search_query)

    if primary_results:
        print(f"    • Found {len(primary_results)} entries")
        # ADD: Display similarity scores
        print("    • Similarity scores:")
        for i, result in enumerate(primary_results[:10]):  # Show top 10
            print(
                f"      {i+1}. Score: {result['score']:.4f} - {result.get('Title_Heading', result.get('combined_text', '')[:50])}"
            )
        all_results["kb_primary"] = primary_querier.format_results(primary_results)

    # 3. IFRS KB Search
    print("  - Searching IFRS knowledge base...")
    ifrs_kb_path = state.get(
        "knowledge_base_additional_path",
        "data/knowledge_base/ifrs_knowledge_base_with_embeddings.parquet",
    )

    ifrs_querier = KnowledgeBaseQuerier(ifrs_kb_path, embedding_model)
    ifrs_results = ifrs_querier.search(search_query)

    if ifrs_results:
        print(f"    • Found {len(ifrs_results)} entries")
        # Display similarity scores
        print("    • Similarity scores:")
        for i, result in enumerate(ifrs_results[:10]):  # Show top 10
            print(
                f"      {i+1}. Score: {result['score']:.4f} - {result.get('combined_text', '')[:50]}"
            )
        all_results["kb_ifrs"] = ifrs_querier.format_results(ifrs_results)

    # 4. Research Documents
    print("  - Loading research documents...")
    research_files = chapter.get("research_files", [])

    if research_files:
        md_processor = MarkdownProcessor()
        doc_contents = []

        for md_file in research_files:
            print(f"    • Processing: {md_file}")
            content = md_processor.process_research_file(md_file, chapter)
            if content:
                formatted = md_processor.format_content(content, Path(md_file).name)
                doc_contents.append(formatted)

        all_results["documents"] = "\n\n".join(doc_contents)

    # Store all results in state
    return {
        "raw_search_results": all_results,
        "cached_web_results": cached_web_results,  # Preserve cache in state
    }


def perform_web_search(search_query: str) -> List[Dict]:
    """Execute web searches for the query"""

    search_queries = generate_search_queries(search_query)
    search_results = []

    for idx, query in enumerate(search_queries, 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please search for information about: {query}\n\nFocus on finding recent developments, best practices, and authoritative sources.",
                    }
                ],
                tools=[
                    {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}
                ],
            )

            result_text = ""
            for content_block in response.content:
                if hasattr(content_block, "type") and content_block.type == "text":
                    result_text += content_block.text

            search_results.append({"query": query, "response": result_text})

        except Exception as e:
            search_results.append({"query": query, "response": f"Error: {str(e)}"})

    return search_results


def generate_search_queries(search_query: str, num_queries: int = 3) -> List[str]:
    """Generate search queries using LLM based on the search query string"""

    prompt = f"""Based on the following information, generate {num_queries} diverse and specific web search queries that would help gather comprehensive information on this topic.

Information:
{search_query}

Return ONLY a Python list of {num_queries} search query strings, no explanation needed.
Example format: ["query 1", "query 2", "query 3"]"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        # Extract the list from response
        response_text = response.content[0].text.strip()
        print(f"    • LLM response: {response_text}")  # DEBUG

        queries = ast.literal_eval(response_text)
        print(f"    • Parsed queries: {queries}, type: {type(queries)}")  # DEBUG

        if isinstance(queries, list) and len(queries) > 0:
            return queries[:num_queries]
        else:
            print(
                f"    • Failed condition: is list? {isinstance(queries, list)}, has items? {len(queries) if isinstance(queries, list) else 'N/A'}"
            )

    except Exception as e:
        print(f"    • Error generating queries with LLM: {e}")

    # Should never reach here
    raise Exception("Failed to generate valid search queries")


def format_web_results(search_results: List[Dict]) -> str:
    """Format web search results for inclusion in research"""

    if not search_results:
        return "No web search results available."

    formatted_parts = []

    for idx, result in enumerate(search_results, 1):
        formatted_parts.append(f"--- Web Search {idx}: {result['query']} ---")
        formatted_parts.append(result["response"])
        formatted_parts.append("")  # Empty line between results

    return "\n".join(formatted_parts)
