import json

from backend.graph.state import MedicalChatState
from backend.mcp_clients.client import call_mcp_tool
from backend.utils.safety_rules import detect_red_flags

async def safety_node(state: MedicalChatState) -> dict:
                                                                                 
    red_flags = detect_red_flags(state["user_input"])
    is_emergency = bool(red_flags) or state.get("is_emergency", False)

    warnings: list[str] = []
    meds = state.get("current_medications") or []

    if len(meds) >= 2 and not is_emergency:
        raw = await call_mcp_tool("drugdata", "check_interactions", {"drug_names": meds})
        if raw:
            data = json.loads(raw)
            for interaction in data.get("interactions", []):
                desc = interaction.get("description")
                if desc:
                    warnings.append(desc)

    return {
        "is_emergency": is_emergency,
        "red_flags": list(set(red_flags + state.get("red_flags", []))),
        "drug_interaction_warnings": warnings,
    }
