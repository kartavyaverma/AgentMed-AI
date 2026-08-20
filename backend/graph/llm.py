from functools import lru_cache

from langchain_groq import ChatGroq

from backend.config import get_settings

settings = get_settings()

AGENT_MODEL_TIER: dict[str, str] = {
    "router": "small",
    "intake": "small",
    "research": "large",
    "clinical_reasoning": "large",
    "safety": "small",
    "composer": "large",
}

@lru_cache
def _model_for_tier(tier: str, temperature: float) -> ChatGroq:
    model_name = (
        settings.groq_model_large if tier == "large" else settings.groq_model_small
    )
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=model_name,
        temperature=temperature,
        streaming=True,
    )

def get_llm(agent_name: str, temperature: float = 0.2) -> ChatGroq:
    tier = AGENT_MODEL_TIER.get(agent_name, "small")
    return _model_for_tier(tier, temperature)
