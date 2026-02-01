from langchain_openai import ChatOpenAI
from app.config import settings

def make_llm():
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
