RESEARCH_PROMPT_TEMPLATE = """
You are conducting research for a business document with the following style guide:
- Tone and Style: {tone_and_style}

Research Task for Chapter: '{chapter_title}'

Chapter Purpose:
{purpose}

Key Topics to Research (provide comprehensive information on each):
{topics}

Keywords to incorporate in your research: {keywords}

{source_guidance}

IMPORTANT - Topics to AVOID in your research:
{topics_to_avoid}

Please provide detailed research summaries that will help write a {target_word_count}-word chapter.
Your research should be thorough enough to support all the stated purposes and cover all key topics comprehensively.
"""

RESEARCH_PROMPT_TEMPLATE_NO_SOURCES = """
You are conducting research for a business document with the following style guide:
- Tone and Style: {tone_and_style}

Research Task for Chapter: '{chapter_title}'

Chapter Purpose:
{purpose}

Key Topics to Research (provide comprehensive information on each):
{topics}

Keywords to incorporate in your research: {keywords}

IMPORTANT - Topics to AVOID in your research:
{topics_to_avoid}

Please provide detailed research summaries that will help write a {target_word_count}-word chapter.
Your research should be thorough enough to support all the stated purposes and cover all key topics comprehensively.
"""
