from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str | None = Field(
        default=None, description="Existing session id. Omit to start a new one."
    )
    message: str = Field(..., min_length=1, max_length=4000)
                                                                       
    age: int | None = None
    sex: Literal["male", "female", "other", "unspecified"] | None = None
    known_allergies: list[str] | None = None
    current_medications: list[str] | None = None

class SourceRef(BaseModel):
    title: str
    url: str | None = None
    source_type: Literal["pubmed", "drug_db", "internal_kb", "web"] = "internal_kb"

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    is_emergency: bool
    urgency_level: Literal["low", "moderate", "high", "emergency"]
    sources: list[SourceRef] = []
    disclaimer: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

class HistoryResponse(BaseModel):
    session_id: str
    messages: list[HistoryMessage]

class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
