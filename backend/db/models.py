import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.database import Base

def _uuid() -> str:
    return str(uuid.uuid4())

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    age: Mapped[int | None] = mapped_column(nullable=True)
    sex: Mapped[str | None] = mapped_column(String, nullable=True)
    known_allergies: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    current_medications: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"))
    role: Mapped[str] = mapped_column(String)                        
    content: Mapped[str] = mapped_column(Text)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    urgency_level: Mapped[str | None] = mapped_column(String, nullable=True)
    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[ChatSession] = relationship(back_populates="messages")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(String, index=True)
    node_name: Mapped[str] = mapped_column(String)                       
    event_type: Mapped[str] = mapped_column(String)                                         
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
