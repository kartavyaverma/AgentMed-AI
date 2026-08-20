from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages

class SourceDict(TypedDict):
    title: str
    url: str | None
    source_type: str

class MedicalChatState(TypedDict, total=False):
                  
    messages: Annotated[list, add_messages]
    session_id: str
    user_input: str

                                                                         
    age: int | None
    sex: str | None
    known_allergies: list[str]
    current_medications: list[str]

                   
    intent: Literal["casual", "general_info", "symptom_check", "drug_question", "emergency"]
    urgency_level: Literal["low", "moderate", "high", "emergency"]

                   
    extracted_symptoms: list[str]
    symptom_duration: str | None

                     
    research_notes: str
    sources: list[SourceDict]

                               
    possible_explanations: list[str]

                   
    is_emergency: bool
    red_flags: list[str]
    drug_interaction_warnings: list[str]

                  
    final_answer: str
    disclaimer: str
