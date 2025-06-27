import json
from datetime import datetime
from agent import create_document_generation_graph, GraphState
from utils.token_tracker import create_token_usage


def load_outline(filepath: str = "data/input/outline.json") -> dict:
    """Load document outline from JSON file"""
    with open(filepath, "r") as f:
        return json.load(f)


def main():
    """Main execution function"""
    # Create the graph
    app = create_document_generation_graph()

    # Load outline
    document_outline = load_outline()

    # Extract styleguide and metadata
    styleguide = document_outline.get(
        "styleguide", {"overall_tone_and_style": "Professional"}
    )

    metadata = document_outline.get(
        "metadata",
        {
            "version": "1.0",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "author": "Document Generation System",
        },
    )

    # Initialize state
    initial_state = {
        "outline": document_outline,
        "styleguide": styleguide,
        "metadata": metadata,
        "chapters_to_process": document_outline["table_of_contents"].copy(),
        "chapter_works": {},
        "current_chapter_id": None,
        "completed_chapters": {},
        "total_token_usage": create_token_usage(0, 0),
        "token_log": [],
        "knowledge_base_path": "data/knowledge_base/df_with_embeddings_large.parquet",
        "knowledge_base_additional_path": 'data/knowledge_base/ifrs_knowledge_base_with_embeddings.parquet',
        "embedding_model": "text-embedding-3-large",
    }

    print("\n🚀 Starting Document Generation Process...")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(
        f"📝 Document style: {styleguide.get('overall_tone_and_style', 'Not specified')}"
    )
    print(f"📚 Total chapters to process: {len(document_outline['table_of_contents'])}")

    # Execute the graph
    final_state = app.invoke(initial_state, {"recursion_limit": 1000})

    print(f"\n⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Print final summary
    print_final_summary(final_state)


def print_final_summary(final_state: GraphState):
    """Print a summary of the final state"""
    print("\n\n" + "=" * 80)
    print("                    ✅ DOCUMENT GENERATION COMPLETE ✅")
    print("=" * 80 + "\n")

    # Display summary statistics
    outline = final_state.get("outline", {})
    toc = outline.get("table_of_contents", [])
    completed_chapters = final_state.get("completed_chapters", {})

    # FIX: Calculate total from chapters instead of using total_token_usage
    total_tokens = 0
    total_cost = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0

    # Sum up all token usage from chapter_works
    for chapter_work in final_state["chapter_works"].values():
        for operation_usage in chapter_work["token_usage"].values():
            total_tokens += operation_usage.get("total_tokens", 0)
            total_cost += operation_usage.get("total_cost", 0)
            total_prompt_tokens += operation_usage.get("prompt_tokens", 0)
            total_completion_tokens += operation_usage.get("completion_tokens", 0)

    print("📊 SUMMARY:")
    print(f"  - Total chapters in outline: {len(toc)}")
    print(f"  - Chapters completed: {len(completed_chapters)}")
    print(f"  - Total tokens used: {total_tokens:,}")
    print(f"  - Prompt tokens: {total_prompt_tokens:,}")
    print(f"  - Completion tokens: {total_completion_tokens:,}")
    print(f"  - Total cost: ${total_cost:.6f}")

    # Calculate average per chapter with proper error handling
    if len(completed_chapters) > 0:
        avg_cost = total_cost / len(completed_chapters)
        avg_tokens = total_tokens / len(completed_chapters)
        print(f"  - Average cost per chapter: ${avg_cost:.6f}")
        print(f"  - Average tokens per chapter: {avg_tokens:,.0f}")
    else:
        print("  - No chapters completed")

    print("\n💾 Output files have been saved to the 'output' directory.")


if __name__ == "__main__":
    main()
