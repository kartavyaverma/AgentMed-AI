from __future__ import annotations

RED_FLAG_PHRASES: list[str] = [
    "chest pain",
    "crushing chest",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "shortness of breath",
    "severe bleeding",
    "uncontrolled bleeding",
    "coughing up blood",
    "vomiting blood",
    "suicidal",
    "kill myself",
    "want to die",
    "overdose",
    "unconscious",
    "unresponsive",
    "seizure",
    "stroke",
    "face drooping",
    "slurred speech",
    "sudden numbness",
    "severe allergic reaction",
    "anaphylaxis",
    "throat closing",
    "swelling of face",
    "poisoning",
    "severe burn",
    "compound fracture",
    "not breathing",
]

def detect_red_flags(text: str) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in RED_FLAG_PHRASES if phrase in lowered]

def is_emergency(text: str) -> bool:
    return len(detect_red_flags(text)) > 0

EMERGENCY_RESPONSE_TEMPLATE = (
    "⚠️ **This may be a medical emergency.**\n\n"
    "Based on what you described ({flags}), please **call your local emergency "
    "number (e.g. 911/112/108) or go to the nearest emergency room immediately.**\n\n"
    "I'm an AI assistant and cannot provide emergency care. Do not wait for a "
    "chat response in a life-threatening situation."
)

STANDARD_DISCLAIMER = (
    "This information is for general educational purposes only and is not a "
    "substitute for professional medical advice, diagnosis, or treatment. "
    "Always seek the advice of a qualified physician or other health provider "
    "with any questions you may have regarding a medical condition."
)
