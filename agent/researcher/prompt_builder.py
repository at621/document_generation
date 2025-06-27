from typing import Dict, List, Optional
from agent.researcher.researcher_prompts import (
    RESEARCH_PROMPT_TEMPLATE,
    RESEARCH_PROMPT_TEMPLATE_NO_SOURCES,
)


class ResearchPromptBuilder:
    """Build research prompts with all available information"""

    def __init__(self, state: Dict, chapter: Dict, current_work: Dict):
        self.state = state
        self.chapter = chapter
        self.current_work = current_work
        self.styleguide = state.get("styleguide", {})

    def build_prompt(self, combined_sources: Optional[str] = None) -> str:
        """Build the complete research prompt

        Args:
            combined_sources: All research sources already formatted and combined
        """

        # Get basic info
        tone_and_style = self.styleguide.get("overall_tone_and_style", "Professional")

        # Handle feedback if rewriting
        topics = self._get_topics_with_feedback()

        # Format components
        purpose = self._format_purpose()
        topics_to_avoid = self._format_topics_to_avoid()
        keywords_str = self._format_keywords()

        # Check if we have sources
        has_sources = bool(combined_sources and combined_sources.strip())

        # Choose template based on whether we have sources
        if has_sources:
            template = RESEARCH_PROMPT_TEMPLATE
            source_guidance = self._format_source_guidance() + "\n\n" + combined_sources
        else:
            template = RESEARCH_PROMPT_TEMPLATE_NO_SOURCES
            source_guidance = ""

        # Build prompt
        prompt_params = {
            "tone_and_style": tone_and_style,
            "chapter_title": self.chapter["heading_label"],
            "purpose": purpose,
            "topics": "\n".join([f"- {topic}" for topic in topics]),
            "keywords": keywords_str,
            "topics_to_avoid": topics_to_avoid,
            "target_word_count": self.chapter.get("target_word_count", 500),
        }

        # Add source_guidance only if using the template that expects it
        if has_sources:
            prompt_params["source_guidance"] = source_guidance

        return template.format(**prompt_params)

    def _get_topics_with_feedback(self) -> List[str]:
        """Get topics, including feedback if this is a rewrite"""
        feedback = self.current_work.get("review_feedback")

        if feedback and self.current_work.get("review_decision") == "reject":
            print(f"  - Incorporating review feedback into research: {feedback}")
            return self.chapter.get("key_topics", []) + [
                f"Additional research to address: {feedback}"
            ]

        return self.chapter.get("key_topics", [])

    def _format_purpose(self) -> str:
        """Format chapter purpose"""
        purpose_list = self.chapter.get("purpose", [])
        if purpose_list:
            return "\n".join([f"- {p}" for p in purpose_list])
        return "- Provide comprehensive information about the topic"

    def _format_topics_to_avoid(self) -> str:
        """Format topics to avoid"""
        topics_to_avoid_list = self.chapter.get("topics_to_avoid", [])
        if topics_to_avoid_list:
            return "\n".join([f"- {t}" for t in topics_to_avoid_list])
        return "- No specific topics to avoid"

    def _format_source_guidance(self) -> str:
        """Format source hints if available"""
        source_hints = self.chapter.get("source_hints")
        if not source_hints:
            return ""

        internal_files = source_hints.get("internal_files", [])
        public_refs = source_hints.get("public_references", [])
        priority = source_hints.get("priority", "general")

        guidance = f"\nSource Guidance (Priority: {priority}):"
        if internal_files:
            guidance += (
                f"\n- Internal documents to reference: {', '.join(internal_files)}"
            )
        if public_refs:
            guidance += f"\n- Public sources to consult: {', '.join(public_refs)}"

        return guidance

    def _format_keywords(self) -> str:
        """Format keywords"""
        keywords = self.chapter.get("keywords", [])
        return ", ".join(keywords) if keywords else "No specific keywords"
