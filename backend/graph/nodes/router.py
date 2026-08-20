import json

from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.llm import get_llm
from backend.graph.state import MedicalChatState
from backend.utils.safety_rules import detect_red_flags

ROUTER_SYSTEM_PROMPT = """You are a routing classifier for a medical information \
assistant. Classify the user's message into exactly one intent and one urgency \
level. Respond ONLY with JSON: {"intent": "...", "urgency_level": "..."}

intent options: casual, general_info, symptom_check, drug_question, emergency
urgency_level options: low, moderate, high, emergency

Use "casual" for non-medical queries (greetings, general chit-chat, off-topic questions, introduction of names, etc.).
Use "general_info", "symptom_check", "drug_question", or "emergency" for medical-related queries.

Err on the side of higher urgency when in doubt."""

async def router_node(state: MedicalChatState) -> dict:
    user_input = state["user_input"]

    red_flags = detect_red_flags(user_input)
    if red_flags:
        return {
            "intent": "emergency",
            "urgency_level": "emergency",
            "red_flags": red_flags,
            "is_emergency": True,
            "messages": [HumanMessage(content=user_input)],
        }

    llm = get_llm("router", temperature=0.0)
    response = await llm.ainvoke(
        [SystemMessage(content=ROUTER_SYSTEM_PROMPT), HumanMessage(content=user_input)]
    )

    try:
        parsed = json.loads(response.content)
        intent = parsed.get("intent", "general_info")
        urgency = parsed.get("urgency_level", "low")
    except (json.JSONDecodeError, AttributeError):
        intent, urgency = "general_info", "low"

    return {
        "intent": intent,
        "urgency_level": urgency,
        "red_flags": [],
        "is_emergency": False,
        "messages": [HumanMessage(content=user_input)],
    }
