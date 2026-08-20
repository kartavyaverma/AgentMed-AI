import json

from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.llm import get_llm
from backend.graph.state import MedicalChatState

INTAKE_SYSTEM_PROMPT = """Extract structured medical intake data from the user's \
message. Respond ONLY with JSON:
{"extracted_symptoms": ["..."], "symptom_duration": "..." or null}

Only include symptoms explicitly mentioned or clearly implied. Do not infer \
symptoms that were not stated."""

async def intake_node(state: MedicalChatState) -> dict:
                                                                         
                                                                            
    if state.get("is_emergency"):
        return {"extracted_symptoms": [], "symptom_duration": None}

    llm = get_llm("intake", temperature=0.0)
    response = await llm.ainvoke(
        [
            SystemMessage(content=INTAKE_SYSTEM_PROMPT),
            HumanMessage(content=state["user_input"]),
        ]
    )

    try:
        parsed = json.loads(response.content)
    except (json.JSONDecodeError, AttributeError):
        parsed = {}

    return {
        "extracted_symptoms": parsed.get("extracted_symptoms", []),
        "symptom_duration": parsed.get("symptom_duration"),
    }
