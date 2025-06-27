WRITER_PROMPT_TEMPLATE = """

**DOCUMENT CONTEXT:**
You are writing a chapter for an official technical standards document. This document
details the complete methodology for developing a macroeconomic add-on for the
bank's Probability of Default (PD) models. The primary goal is to ensure
compliance with IFRS 9 reporting standards by creating a robust and auditable
framework for this PD add-on. Your audience includes risk modelers, validators,
auditors, and regulators.

**YOUR TASK:**
Write the body content for the chapter titled '{chapter_title}'.

IMPORTANT INSTRUCTIONS:
- Write ONLY the chapter content - do not add any headings or titles
- The heading '{chapter_title}' will be added automatically by the system
- Focus on creating comprehensive, well-structured prose content
- Target word count: {target_word_count} words
- Writing style: {tone_and_style}
- You are free to add your own insights if you are really sure that they are correct

Key topics to cover:
{key_topics}

Research material:
{research}

{feedback}

Remember: Write only the body content. Do not include the chapter title or any markdown headings.
"""
