from typing import Tuple, Dict
from datetime import datetime
from agent.state import TokenUsage

# Token pricing for different models (in USD per 1K tokens)
PRICING = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "gpt-4.1-mini": {"input": 0.003, "output": 0.015},
    "o3": {"input": 0.003, "output": 0.015},
    "claude-sonnet-4-20250514": {  # Claude Sonnet 4
        "input": 0.003,  # $0.15 per 1M tokens
        "output": 0.015,  # $0.60 per 1M tokens
    },
}

# Default model for backward compatibility
DEFAULT_MODEL = "gpt-4.1-mini"


def calculate_cost(
    prompt_tokens: int, completion_tokens: int, model: str = DEFAULT_MODEL
) -> Tuple[float, float, float]:
    """Calculate the cost based on token usage for a specific model"""
    if model not in PRICING:
        print(f"Warning: Unknown model '{model}', using default pricing")
        model = DEFAULT_MODEL

    input_cost = (prompt_tokens / 1000) * PRICING[model]["input"]
    output_cost = (completion_tokens / 1000) * PRICING[model]["output"]
    total_cost = input_cost + output_cost
    return input_cost, output_cost, total_cost


def create_token_usage(
    prompt_tokens: int, completion_tokens: int, model: str = DEFAULT_MODEL
) -> TokenUsage:
    """Create a TokenUsage dictionary with model-specific pricing"""
    input_cost, output_cost, total_cost = calculate_cost(
        prompt_tokens, completion_tokens, model
    )
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "model": model,  # Track which model was used
    }


def merge_token_usage(usage1: TokenUsage, usage2: TokenUsage) -> TokenUsage:
    """Merge two token usage dictionaries"""
    return {
        "prompt_tokens": usage1.get("prompt_tokens", 0)
        + usage2.get("prompt_tokens", 0),
        "completion_tokens": usage1.get("completion_tokens", 0)
        + usage2.get("completion_tokens", 0),
        "total_tokens": usage1.get("total_tokens", 0) + usage2.get("total_tokens", 0),
        "input_cost": usage1.get("input_cost", 0) + usage2.get("input_cost", 0),
        "output_cost": usage1.get("output_cost", 0) + usage2.get("output_cost", 0),
        "total_cost": usage1.get("total_cost", 0) + usage2.get("total_cost", 0),
    }


def update_total_tokens(
    state: Dict, new_usage: TokenUsage, operation: str, chapter_id: str
) -> Dict:
    """Update the total token usage in state"""
    # Initialize if not exists
    if "total_token_usage" not in state:
        state["total_token_usage"] = create_token_usage(0, 0)

    total_usage = state["total_token_usage"]

    # Update totals
    total_usage["prompt_tokens"] += new_usage.get("prompt_tokens", 0)
    total_usage["completion_tokens"] += new_usage.get("completion_tokens", 0)
    total_usage["total_tokens"] += new_usage.get("total_tokens", 0)
    total_usage["input_cost"] += new_usage.get("input_cost", 0)
    total_usage["output_cost"] += new_usage.get("output_cost", 0)
    total_usage["total_cost"] += new_usage.get("total_cost", 0)

    # Add to token log
    token_log = state.get("token_log", [])
    token_log.append(
        {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "chapter_id": chapter_id,
            "usage": new_usage.copy(),
            "cumulative_total": total_usage.copy(),  # Track running total
        }
    )

    return {"total_token_usage": total_usage, "token_log": token_log}


def print_token_usage(usage: TokenUsage, label: str = "Token Usage"):
    """Pretty print token usage"""
    print(f"\n💰 {label}:")
    print(f"  - Prompt tokens: {usage.get('prompt_tokens', 0):,}")
    print(f"  - Completion tokens: {usage.get('completion_tokens', 0):,}")
    print(f"  - Total tokens: {usage.get('total_tokens', 0):,}")
    print(f"  - Input cost: ${usage.get('input_cost', 0):.6f}")
    print(f"  - Output cost: ${usage.get('output_cost', 0):.6f}")
    print(f"  - Total cost: ${usage.get('total_cost', 0):.6f}")
    if "model" in usage:
        print(f"  - Model: {usage['model']}")


def generate_token_report(state: Dict) -> str:
    """Generate a comprehensive token usage report"""
    report = []
    report.append("=" * 80)
    report.append("                    💰 COMPREHENSIVE TOKEN USAGE REPORT 💰")
    report.append("=" * 80)

    # Get chapter works for detailed breakdown
    chapter_works = state.get("chapter_works", {})

    if chapter_works:
        report.append("\n📊 PER-CHAPTER TOKEN USAGE:")
        report.append("-" * 80)

        grand_total = create_token_usage(0, 0)

        for chapter_id, work in chapter_works.items():
            chapter_details = work.get("chapter_details", {})
            chapter_title = chapter_details.get(
                "heading_label", f"Chapter {chapter_id}"
            )

            report.append(f"\n🔸 Chapter {chapter_id}: {chapter_title}")

            token_usage = work.get("token_usage", {})
            chapter_total = create_token_usage(0, 0)

            # Process each operation
            for operation in ["researcher", "writer", "reviewer"]:
                if operation in token_usage:
                    usage = token_usage[operation]
                    report.append(f"\n   {operation}:")
                    report.append(
                        f"     - Tokens: {usage.get('total_tokens', 0):,} "
                        f"(prompt: {usage.get('prompt_tokens', 0):,}, "
                        f"completion: {usage.get('completion_tokens', 0):,})"
                    )
                    report.append(
                        f"     - Cost: ${usage.get('total_cost', 0):.6f} "
                        f"(input: ${usage.get('input_cost', 0):.6f}, "
                        f"output: ${usage.get('output_cost', 0):.6f})"
                    )

                    # Add to chapter total
                    chapter_total = merge_token_usage(chapter_total, usage)

            # Show chapter total
            report.append("\n   CHAPTER TOTAL:")
            report.append(f"     - Total tokens: {chapter_total['total_tokens']:,}")
            report.append(f"     - Total cost: ${chapter_total['total_cost']:.6f}")

            # Add to grand total
            grand_total = merge_token_usage(grand_total, chapter_total)

    return "\n".join(report)


def debug_token_tracking(state: Dict):
    """Debug function to trace token tracking issues"""
    print("\n🔍 TOKEN TRACKING DEBUG:")
    print("-" * 50)

    # Show token log
    token_log = state.get("token_log", [])
    print(f"Token log entries: {len(token_log)}")

    for i, entry in enumerate(token_log[-5:]):  # Show last 5 entries
        print(f"\nEntry {i+1}:")
        print(f"  Operation: {entry['operation']}")
        print(f"  Chapter: {entry['chapter_id']}")
        print(f"  Tokens: {entry['usage'].get('total_tokens', 0):,}")
        print(f"  Cost: ${entry['usage'].get('total_cost', 0):.6f}")
        if "cumulative_total" in entry:
            print(
                f"  Cumulative cost: ${entry['cumulative_total'].get('total_cost', 0):.6f}"
            )

    # Show final total
    total_usage = state.get("total_token_usage", {})
    print(f"\nFinal total tokens: {total_usage.get('total_tokens', 0):,}")
    print(f"Final total cost: ${total_usage.get('total_cost', 0):.6f}")
