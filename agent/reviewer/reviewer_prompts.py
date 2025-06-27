REVIEWER_PROMPT_TEMPLATE = """
You are a meticulous editor. Review the following text.
Text: "{text}"

If the text is well-written, comprehensive, and at least a few paragraphs long, respond with only the word 'accept'.
If it fails, start your response with 'reject:' followed by a concise, one-sentence explanation of what is missing or wrong.
"""
