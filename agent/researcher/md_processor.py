from pathlib import Path
from typing import Dict


class MarkdownProcessor:
    """Process markdown files - include entire content without chunking"""

    def __init__(self):
        pass

    def process_research_file(self, md_file: str, chapter_info: Dict) -> str:
        """Read and return the entire markdown file content"""
        file_path = Path(md_file)

        if not file_path.exists():
            print(f"  - Warning: Markdown file not found: {md_file}")
            return ""

        print(f"  - Loading research file: {file_path.name}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_size = len(content)
            print(f"    • File size: {file_size:,} characters")

            # Return the entire content
            return content

        except Exception as e:
            print(f"  - Error reading markdown file: {e}")
            return ""

    def format_content(self, content: str, filename: str) -> str:
        """Format the markdown content for inclusion in research prompt"""
        if not content:
            return ""

        formatted = f"\n\n### Research Document: {filename}\n"
        formatted += "*Full document content included below:*\n\n"
        formatted += content
        formatted += "\n\n---End of Research Document---\n"

        return formatted
