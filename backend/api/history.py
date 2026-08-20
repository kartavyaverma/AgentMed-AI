import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import ChatSession, ChatMessage
from backend.models.schemas import HistoryMessage, HistoryResponse, SessionCreateResponse

router = APIRouter(tags=["history"])

@router.post("/session", response_model=SessionCreateResponse)
def create_session(db: Session = Depends(get_db)) -> SessionCreateResponse:
    session = ChatSession(id=str(uuid.uuid4()))
    db.add(session)
    db.commit()
    return SessionCreateResponse(session_id=session.id)

@router.get("/history/{session_id}", response_model=HistoryResponse)
def get_history(session_id: str, db: Session = Depends(get_db)) -> HistoryResponse:
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    rows = db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    ).scalars().all()

    return HistoryResponse(
        session_id=session_id,
        messages=[
            HistoryMessage(role=r.role, content=r.content, created_at=r.created_at) for r in rows
        ],
    )
