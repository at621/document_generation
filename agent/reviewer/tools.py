from agent.state import ReviewerState
from utils.token_tracker import (
    create_token_usage,
    print_token_usage,
)
from agent.reviewer.reviewer_prompts import REVIEWER_PROMPT_TEMPLATE


def review_chapter(state: ReviewerState, llm) -> dict:
    """Review a generated chapter"""
    print("\n--- 🧐 EXECUTING REVIEWER NODE ---")
    chapter_id = state["current_chapter_id"]
    chapter_works = state["chapter_works"]
    current_work = chapter_works[chapter_id]
    current_chapter = current_work["chapter_details"]
    generated_text = current_work["generated_text"]

    # Get style guide
    styleguide = state.get("styleguide", {})
    tone_and_style = styleguide.get("overall_tone_and_style", "Professional")

    # Calculate word count
    actual_word_count = len(generated_text.split())
    target_word_count = current_chapter.get("target_word_count", 500)

    # Show the text the reviewer is actually seeing
    print("  - Reviewer is analyzing the full text.")
    print(f"  - Word count: {actual_word_count} (target: {target_word_count})")

    # Simple review prompt
    prompt = f"""
    You are a meticulous editor reviewing text that should be in a {tone_and_style} tone.

    Review the following text for chapter '{current_chapter['heading_label']}':
    Text: "{generated_text}"

    If the text is well-written, comprehensive, appropriate in tone, respond with only the word 'accept'.

    If it fails, start your response with 'reject:' followed by a concise explanation of what is missing or wrong.
    """

    # Call LLM and track tokens
    response = llm.invoke(prompt)
    review_response = response.content.strip()

    # Extract token usage
    usage_metadata = response.response_metadata.get("token_usage", {})
    prompt_tokens = usage_metadata.get("prompt_tokens", 0)
    completion_tokens = usage_metadata.get("completion_tokens", 0)

    # Create token usage record
    token_usage = create_token_usage(prompt_tokens, completion_tokens)
    print_token_usage(token_usage, "Reviewer Token Usage")

    if review_response.lower() == "accept":
        decision = "accept"
        feedback = "Chapter accepted."
    else:
        decision = "reject"
        feedback = review_response.replace("reject:", "").strip()

    print(f"  - Review Decision: {decision.upper()}")
    if decision == "reject":
        print(f"  - Feedback Provided: {feedback}")

    # Update chapter work
    chapter_works[chapter_id]["review_feedback"] = feedback
    chapter_works[chapter_id]["review_decision"] = decision

    # Track review iterations
    review_count = sum(
        1 for key in chapter_works[chapter_id]["token_usage"] if "reviewer" in key
    )
    operation_name = f"reviewer_{review_count + 1}" if review_count > 0 else "reviewer"
    chapter_works[chapter_id]["token_usage"][operation_name] = token_usage

    return {"chapter_works": chapter_works}
