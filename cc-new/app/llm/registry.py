#app.llm.registry.py
from app.llm.anthropic import AnthropicProvider
from app.llm.openai import OpenAIProvider
from app.llm.bedrock import BedrockProvider


def resolve_llm(name: str):
    if name == "anthropic":
        return AnthropicProvider()
    if name == "openai":
        return OpenAIProvider()
    if name == "bedrock":
        return BedrockProvider()
    raise ValueError(f"Unsupported LLM provider: {name}")
