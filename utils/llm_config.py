from langchain_openai import ChatOpenAI


def get_llm():
    """Get configured LLM instance"""
    # return ChatOpenAI(model="gpt-4.1-mini", temperature=0.1)  # gpt-4.1-mini
    return ChatOpenAI(model="o3")
