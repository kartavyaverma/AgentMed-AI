from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.llm import get_llm
from backend.graph.state import MedicalChatState

REASONING_SYSTEM_PROMPT = """You are a clinical information assistant, NOT a \
diagnosing physician. Given symptoms and research notes, list 2-4 POSSIBLE, \
general, non-exhaustive explanations for informational purposes only.

Rules you must follow:
- Never state a definitive diagnosis.
- Always use hedging language: "could be associated with", "one possibility is".
- Do not recommend specific prescription treatments or dosages.
- If symptoms are vague or evidence is thin, say more information/a doctor \
visit is needed rather than guessing.

Respond as a short plain-text list."""

async def clinical_reasoning_node(state: MedicalChatState) -> dict:
    if state.get("is_emergency"):
        return {"possible_explanations": []}

    if state.get("intent") not in ("symptom_check",):
                                                                         
                                                                            
                                                                     
        return {"possible_explanations": []}

    symptoms = state.get("extracted_symptoms", [])
    duration = state.get("symptom_duration")
    research_notes = state.get("research_notes", "")

    llm = get_llm("clinical_reasoning", temperature=0.3)
    context = (
        f"Symptoms: {', '.join(symptoms) if symptoms else 'not clearly specified'}\n"
        f"Duration: {duration or 'not specified'}\n"
        f"Research notes:\n{research_notes}"
    )
    response = await llm.ainvoke(
        [SystemMessage(content=REASONING_SYSTEM_PROMPT), HumanMessage(content=context)]
    )

    explanations = [line.strip("-• ").strip() for line in response.content.split("\n") if line.strip()]
    return {"possible_explanations": explanations}
