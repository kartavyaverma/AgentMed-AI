from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from backend.config import get_settings
from backend.graph.state import MedicalChatState
from backend.graph.nodes.router import router_node
from backend.graph.nodes.intake import intake_node
from backend.graph.nodes.research import research_node
from backend.graph.nodes.clinical_reasoning import clinical_reasoning_node
from backend.graph.nodes.safety import safety_node
from backend.graph.nodes.composer import composer_node

settings = get_settings()

def _route_after_router(state: MedicalChatState) -> str:
    if state.get("is_emergency"):
        return "safety"
                                                                                    
    if state.get("intent") == "casual": 
        return "safety"                                           
    return "research"

def build_graph_builder() -> StateGraph:
    builder = StateGraph(MedicalChatState)

    builder.add_node("router", router_node)
    builder.add_node("intake", intake_node)
    builder.add_node("research", research_node)
    builder.add_node("clinical_reasoning", clinical_reasoning_node)
    builder.add_node("safety", safety_node)
    builder.add_node("composer", composer_node)

    builder.set_entry_point("router")
    builder.add_edge("router", "intake")
    builder.add_conditional_edges(
        "intake",
        _route_after_router,
        {"safety": "safety", "research": "research"},
    )
    builder.add_edge("research", "clinical_reasoning")
    builder.add_edge("clinical_reasoning", "safety")
    builder.add_edge("safety", "composer")
    builder.add_edge("composer", END)

    return builder

_compiled_graph = None
_checkpointer_cm = None

async def get_compiled_graph():
    global _compiled_graph, _checkpointer_cm

    if _compiled_graph is not None:
        return _compiled_graph

    _checkpointer_cm = AsyncPostgresSaver.from_conn_string(settings.database_url)
    checkpointer = await _checkpointer_cm.__aenter__()
    await checkpointer.setup()

    builder = build_graph_builder()
    _compiled_graph = builder.compile(checkpointer=checkpointer)
    return _compiled_graph

async def close_graph():
    global _checkpointer_cm
    if _checkpointer_cm is not None:
        await _checkpointer_cm.__aexit__(None, None, None)
        _checkpointer_cm = None
