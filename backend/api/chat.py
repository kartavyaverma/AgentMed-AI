import json
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from backend.db.database import get_db
from backend.db.models import ChatSession, ChatMessage
from backend.graph.graph import get_compiled_graph
from backend.models.schemas import ChatRequest, ChatResponse, SourceRef

router = APIRouter(prefix="/chat", tags=["chat"])

def _ensure_session(db: Session, req: ChatRequest) -> str:
    if req.session_id:
        existing = db.get(ChatSession, req.session_id)
        if existing:
            return existing.id

    session = ChatSession(
        id=str(uuid.uuid4()),
        age=req.age,
        sex=req.sex,
        known_allergies=req.known_allergies or [],
        current_medications=req.current_medications or [],
    )
    db.add(session)
    db.commit()
    return session.id

def _persist_turn(db: Session, session_id: str, req: ChatRequest, result: dict) -> None:
    db.add(ChatMessage(session_id=session_id, role="user", content=req.message))
    db.add(
        ChatMessage(
            session_id=session_id,
            role="assistant",
            content=result["final_answer"],
            is_emergency=result.get("is_emergency", False),
            urgency_level=result.get("urgency_level", "low"),
            sources=result.get("sources", []),
        )
    )
    db.commit()

async def _run_graph(session_id: str, req: ChatRequest) -> dict:
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "user_input": req.message,
        "session_id": session_id,
        "age": req.age,
        "sex": req.sex,
        "known_allergies": req.known_allergies or [],
        "current_medications": req.current_medications or [],
    }
    result = await graph.ainvoke(initial_state, config=config)
    return result

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    session_id = _ensure_session(db, req)
    result = await _run_graph(session_id, req)
    _persist_turn(db, session_id, req, result)

    return ChatResponse(
        session_id=session_id,
        answer=result["final_answer"],
        is_emergency=result.get("is_emergency", False),
        urgency_level=result.get("urgency_level", "low"),
        sources=[SourceRef(**s) for s in result.get("sources", [])],
        disclaimer=result.get("disclaimer", ""),
    )

@router.post("/stream")
async def chat_stream(req: ChatRequest, db: Session = Depends(get_db)):
    session_id = _ensure_session(db, req)

    async def event_generator():
        graph = await get_compiled_graph()
        config = {"configurable": {"thread_id": session_id}}
        initial_state = {
            "user_input": req.message,
            "session_id": session_id,
            "age": req.age,
            "sex": req.sex,
            "known_allergies": req.known_allergies or [],
            "current_medications": req.current_medications or [],
        }

        final_result = {}
        
                                                                                     
        async for event in graph.astream_events(initial_state, config=config, version="v2"):
            kind = event["event"]
            node_name = event["metadata"].get("langgraph_node")

                                                               
            if kind == "on_chain_start" and node_name:
                yield {
                    "event": "node_update",
                    "data": json.dumps({"node": node_name}),
                }

                                                                             
            elif kind == "on_chat_model_stream" and node_name == "composer":
                content = event["data"]["chunk"].content
                if content:
                    yield {
                        "event": "token",
                        "data": json.dumps({"token": content}),
                    }

                                                                  
            elif kind == "on_chain_end" and node_name:
                output = event["data"].get("output")
                if isinstance(output, dict):
                    final_result.update(output)

        _persist_turn(db, session_id, req, final_result)

        yield {
            "event": "final",
            "data": json.dumps(
                {
                    "session_id": session_id,
                    "answer": final_result.get("final_answer", ""),
                    "is_emergency": final_result.get("is_emergency", False),
                    "urgency_level": final_result.get("urgency_level", "low"),
                    "sources": final_result.get("sources", []),
                    "disclaimer": final_result.get("disclaimer", ""),
                }
            ),
        }

    return EventSourceResponse(event_generator())

def _safe(obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return {k: v for k, v in obj.items() if k != "messages"}
