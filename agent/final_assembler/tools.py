from datetime import datetime
from pathlib import Path
import pypandoc
from agent.state import GraphState
from utils.token_tracker import create_token_usage


def assemble_final_document(state: GraphState) -> dict:
    """Assemble the final document from all completed chapters"""
    print("\n--- 📚 ASSEMBLING FINAL DOCUMENT ---")

    # Configuration
    WORD_TEMPLATE_PATH = "data/input/20250525_word_template.docx"  # Modify this to your specific template file

    completed_chapters = state["completed_chapters"]

    # Create the final document following the exact outline structure
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_usage = state.get("total_token_usage", create_token_usage(0, 0))

    # Build the markdown document following the exact outline structure
    markdown_lines = []

    # Sort chapters by their ID to maintain the outline order
    sorted_chapter_ids = sorted(
        completed_chapters.keys(), key=lambda x: [int(i) for i in x.split(".")]
    )

    # Add each chapter with proper heading levels from the outline
    for chapter_id in sorted_chapter_ids:
        chapter_data = completed_chapters[chapter_id]
        chapter_details = chapter_data["details"]

        # Determine heading level based on the chapter level in the outline
        level = chapter_details.get("level", 1)
        heading_prefix = "#" * level

        # Add the chapter with proper heading level
        markdown_lines.extend(
            [
                f"{heading_prefix} {chapter_details['heading_label']}",
                "",
                chapter_data["text"],
                "",
            ]
        )

    final_document = "\n".join(markdown_lines)

    # Save to file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Create filename with timestamp
    filename_base = f"generated_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    markdown_filename = f"{filename_base}.md"
    markdown_filepath = output_dir / markdown_filename

    # Write the markdown file
    with open(markdown_filepath, "w", encoding="utf-8") as f:
        f.write(final_document)

    print(f"\n💾 Markdown document saved to: {markdown_filepath}")
    print(f"   File size: {markdown_filepath.stat().st_size:,} bytes")

    # Convert to Word format using pypandoc with template
    word_filename = f"{filename_base}.docx"
    word_filepath = output_dir / word_filename

    # Use the configured template path
    template_path = Path(WORD_TEMPLATE_PATH)

    if template_path.exists():
        print(f"\n📄 Using Word template: {template_path}")

        try:
            # Convert markdown to Word with template
            pypandoc.convert_file(
                str(markdown_filepath),
                "docx",
                outputfile=str(word_filepath),
                extra_args=[f"--reference-doc={str(template_path)}"],
            )

            print(f"✅ Word document saved to: {word_filepath}")
            print(f"   File size: {word_filepath.stat().st_size:,} bytes")

        except Exception as e:
            print(f"❌ Error converting to Word format: {e}")
            print("   Markdown file is still available.")
    else:
        print(f"\n⚠️  Word template not found at: {template_path}")
        print("   Please ensure your template file exists at this location.")
        print("   Attempting to create Word document without template...")

        # Create Word without template as fallback
        try:
            pypandoc.convert_file(
                str(markdown_filepath), "docx", outputfile=str(word_filepath)
            )
            print(f"✅ Word document saved to: {word_filepath} (no template applied)")
        except Exception as e:
            print(f"❌ Error converting to Word format: {e}")

    # Also save a detailed report and metadata
    save_token_report(state, output_dir)
    save_metadata_report(state, output_dir, total_usage, completed_chapters, timestamp)

    # Print comprehensive token summary
    print_final_summary(state, total_usage, completed_chapters)

    return {"final_document": final_document}


def save_token_report(state: GraphState, output_dir: Path):
    """Save a detailed token usage report"""
    report_filename = f"token_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_filepath = output_dir / report_filename

    with open(report_filepath, "w", encoding="utf-8") as f:
        f.write("COMPREHENSIVE TOKEN USAGE REPORT\n")
        f.write("=" * 80 + "\n\n")

        for chapter_id, work in state["chapter_works"].items():
            chapter_details = work["chapter_details"]
            f.write(f"Chapter {chapter_id}: {chapter_details['heading_label']}\n")
            f.write("-" * 60 + "\n")

            for operation, usage in work["token_usage"].items():
                f.write(f"\n{operation}:\n")
                f.write(
                    f"  - Tokens: {usage['total_tokens']:,} (prompt: {usage['prompt_tokens']:,}, completion: {usage['completion_tokens']:,})\n"
                )
                f.write(
                    f"  - Cost: ${usage['total_cost']:.6f} (input: ${usage['input_cost']:.6f}, output: ${usage['output_cost']:.6f})\n"
                )

            if chapter_id in state["completed_chapters"]:
                chapter_total = state["completed_chapters"][chapter_id][
                    "chapter_token_summary"
                ]
                f.write(f"\nCHAPTER TOTAL:\n")
                f.write(f"  - Total tokens: {chapter_total['total_tokens']:,}\n")
                f.write(f"  - Total cost: ${chapter_total['total_cost']:.6f}\n")

            f.write("\n" + "=" * 80 + "\n\n")

        total_usage = state.get("total_token_usage", create_token_usage(0, 0))
        f.write("OVERALL SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total prompt tokens: {total_usage['prompt_tokens']:,}\n")
        f.write(f"Total completion tokens: {total_usage['completion_tokens']:,}\n")
        f.write(f"Total tokens used: {total_usage['total_tokens']:,}\n")
        f.write(f"Total input cost: ${total_usage['input_cost']:.6f}\n")
        f.write(f"Total output cost: ${total_usage['output_cost']:.6f}\n")
        f.write(f"TOTAL COST: ${total_usage['total_cost']:.6f}\n")

    print(f"📊 Token report saved to: {report_filepath}")


def save_metadata_report(
    state: GraphState, output_dir: Path, total_usage, completed_chapters, timestamp
):
    """Save a metadata report with document generation statistics"""
    metadata_filename = (
        f"document_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    metadata_filepath = output_dir / metadata_filename

    with open(metadata_filepath, "w", encoding="utf-8") as f:
        f.write("# Document Generation Metadata\n\n")
        f.write(f"*Generated on: {timestamp}*\n\n")
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total Chapters**: {len(completed_chapters)}\n")
        f.write(f"- **Total Tokens Used**: {total_usage['total_tokens']:,}\n")
        f.write(f"- **Total Cost**: ${total_usage['total_cost']:.6f}\n")
        if completed_chapters:
            f.write(
                f"- **Average Cost per Chapter**: ${total_usage['total_cost'] / len(completed_chapters):.6f}\n"
            )
        else:
            f.write("- **Average Cost per Chapter**: N/A\n")
        f.write(f"- **Generated on**: {timestamp}\n\n")

        f.write("## Token Usage Breakdown\n\n")
        f.write(f"- **Prompt Tokens**: {total_usage['prompt_tokens']:,}\n")
        f.write(f"- **Completion Tokens**: {total_usage['completion_tokens']:,}\n")
        f.write(f"- **Input Cost**: ${total_usage['input_cost']:.6f}\n")
        f.write(f"- **Output Cost**: ${total_usage['output_cost']:.6f}\n\n")

        f.write("## Chapter Details\n\n")
        for chapter_id, chapter_data in completed_chapters.items():
            chapter_details = chapter_data["details"]
            f.write(f"### {chapter_details['heading_label']}\n")
            f.write(
                f"- Chapter tokens: {chapter_data['chapter_token_summary']['total_tokens']:,}\n"
            )
            f.write(
                f"- Cost: ${chapter_data['chapter_token_summary']['total_cost']:.6f}\n\n"
            )

    print(f"📋 Metadata report saved to: {metadata_filepath}")


def print_final_summary(state: GraphState, total_usage, completed_chapters):
    """Print comprehensive token usage summary"""
    print("\n" + "=" * 80)
    print("                    💰 COMPREHENSIVE TOKEN USAGE REPORT 💰")
    print("=" * 80)

    # Per-chapter breakdown
    print("\n📊 PER-CHAPTER TOKEN USAGE:")
    print("-" * 80)

    for chapter_id, work in state["chapter_works"].items():
        chapter_details = work["chapter_details"]
        print(f"\n🔸 Chapter {chapter_id}: {chapter_details['heading_label']}")

        # Show each operation's token usage
        for operation, usage in work["token_usage"].items():
            print(f"\n   {operation}:")
            print(
                f"     - Tokens: {usage['total_tokens']:,} (prompt: {usage['prompt_tokens']:,}, completion: {usage['completion_tokens']:,})"
            )
            print(
                f"     - Cost: ${usage['total_cost']:.6f} (input: ${usage['input_cost']:.6f}, output: ${usage['output_cost']:.6f})"
            )

        # Chapter total
        if chapter_id in completed_chapters:
            chapter_total = completed_chapters[chapter_id]["chapter_token_summary"]
            print(f"\n   CHAPTER TOTAL:")
            print(f"     - Total tokens: {chapter_total['total_tokens']:,}")
            print(f"     - Total cost: ${chapter_total['total_cost']:.6f}")

