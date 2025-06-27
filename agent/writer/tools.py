from agent.state import WriterState
from utils.token_tracker import (
    create_token_usage,
    print_token_usage,
)


def write_chapter(state: WriterState, llm) -> dict:
    """Write a chapter based on research"""
    print("\n--- ✍️ EXECUTING WRITER NODE ---")
    chapter_id = state["current_chapter_id"]
    chapter_works = state["chapter_works"]
    current_work = chapter_works[chapter_id]
    current_chapter = current_work["chapter_details"]
    research = current_work["research_results"]

    # Get style guide
    styleguide = state.get("styleguide", {})
    tone_and_style = styleguide.get("overall_tone_and_style", "Professional")

    feedback_prompt = ""
    if current_work.get("review_decision") == "reject":
        feedback_prompt = f"Please address the following feedback from the previous version: {current_work['review_feedback']}"

    # Format key topics as a bullet list
    key_topics = "\n".join(
        [f"- {topic}" for topic in current_chapter.get("key_topics", [])]
    )

    # Updated prompt that instructs the writer NOT to add headings
    prompt = f"""
Write the content for the chapter '{current_chapter['heading_label']}'.

IMPORTANT INSTRUCTIONS:
- Write ONLY the chapter content - do not add any headings, titles, or markdown headers
- The heading '{current_chapter['heading_label']}' will be added automatically by the system
- Focus on creating comprehensive, well-structured prose content
- Target word count: {current_chapter.get('target_word_count', 500)} words
- Writing style: {tone_and_style}

Key topics to cover:
{key_topics}

Purpose of this chapter:
{' '.join(current_chapter.get('purpose', []))}

Research material:
{research}

{feedback_prompt}

Remember: Write only the body content. Do not include the chapter title or any markdown headings (#, ##, ###, etc.).
Start directly with the chapter content.
"""

    # Call LLM and track tokens
    response = llm.invoke(prompt)
    generated_text = response.content

    # Clean up any headings that might have been added despite instructions
    # Remove lines that start with # (markdown headings)
    lines = generated_text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Skip lines that are markdown headings
        if not line.strip().startswith("#"):
            cleaned_lines.append(line)

    generated_text = "\n".join(cleaned_lines).strip()

    # Extract token usage
    usage_metadata = response.response_metadata.get("token_usage", {})
    prompt_tokens = usage_metadata.get("prompt_tokens", 0)
    completion_tokens = usage_metadata.get("completion_tokens", 0)

    # Create token usage record
    token_usage = create_token_usage(prompt_tokens, completion_tokens)
    print_token_usage(token_usage, "Writer Token Usage")

    # Print the cleaned text
    print("  - Writer Generated Text (Cleaned):")
    print(f'  """\n{generated_text}\n"""')

    # Update chapter work
    chapter_works[chapter_id]["generated_text"] = generated_text

    # Track if this is a rewrite
    operation_name = (
        "writer_rewrite"
        if "writer" in chapter_works[chapter_id]["token_usage"]
        else "writer"
    )
    chapter_works[chapter_id]["token_usage"][operation_name] = token_usage

    return {"chapter_works": chapter_works}
