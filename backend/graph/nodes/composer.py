from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from backend.graph.llm import get_llm
from backend.graph.state import MedicalChatState
from backend.utils.safety_rules import EMERGENCY_RESPONSE_TEMPLATE, STANDARD_DISCLAIMER

COMPOSER_SYSTEM_PROMPT = """You are a warm, clear medical information assistant \
writing the final response to a user. Combine the research notes, possible \
explanations, and any drug interaction warnings into a single well-organized \
plain-language answer.

Rules:
- Never state a definitive diagnosis.
- If drug interaction warnings are present, feature them prominently near the top.
- Keep it concise: short paragraphs or bullet points, not a wall of text.
- End with a brief note on when to see a doctor in person.
- Do NOT include a disclaimer yourself -- one is appended automatically."""

async def composer_node(state: MedicalChatState) -> dict:
    if state.get("is_emergency"):
        flags = ", ".join(state.get("red_flags", [])) or "the symptoms described"
        answer = EMERGENCY_RESPONSE_TEMPLATE.format(flags=flags)
        return {
            "final_answer": answer,
            "disclaimer": STANDARD_DISCLAIMER,
            "messages": [AIMessage(content=answer)],
        }

    context_parts = []

    if state.get("research_notes"):
        context_parts.append(f"Research notes:\n{state['research_notes']}")
    if state.get("possible_explanations"):
        context_parts.append(
            "Possible explanations (non-diagnostic):\n"
            + "\n".join(f"- {e}" for e in state["possible_explanations"])
        )
    if state.get("drug_interaction_warnings"):
        context_parts.append(
            "Drug interaction warnings:\n"
            + "\n".join(f"- {w}" for w in state["drug_interaction_warnings"])
        )

                                                                       
    messages = [SystemMessage(content=COMPOSER_SYSTEM_PROMPT)] + state.get("messages", [])

    if context_parts:
        messages.append(
            SystemMessage(
                content="Use the following clinical evidence and safety warnings to answer the user's latest query:\n\n"
                + "\n\n".join(context_parts)
            )
        )

    llm = get_llm("composer", temperature=0.4)
    response = await llm.ainvoke(messages)

    return {
        "final_answer": response.content,
        "disclaimer": STANDARD_DISCLAIMER,
        "messages": [AIMessage(content=response.content)],
    }
