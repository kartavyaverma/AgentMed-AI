import json

import requests
import streamlit as st

from frontend.components.emergency_banner import render_emergency_banner

NODE_PROGRESS_LABELS = {
    "router": "Classifying your question…",
    "intake": "Extracting symptom details…",
    "research": "Searching medical literature…",
    "clinical_reasoning": "Reasoning through possibilities…",
    "safety": "Running safety & interaction checks…",
    "composer": "Composing final answer…",
}

def render_message(role: str, content: str, sources: list | None = None, is_emergency: bool = False):
    with st.chat_message(role):
        if is_emergency:
            render_emergency_banner()
        st.markdown(content)
        if sources:
            with st.expander(f"Sources ({len(sources)})"):
                for s in sources:
                    title = s.get("title", "Untitled")
                    url = s.get("url")
                    st.markdown(f"- [{title}]({url})" if url else f"- {title}")

def stream_chat_response(backend_base_url: str, session_id: str | None, message: str, patient_context: dict):
    payload = {"session_id": session_id, "message": message, **patient_context}

    with requests.post(
        f"{backend_base_url}/chat/stream", json=payload, stream=True, timeout=120
    ) as resp:
        resp.raise_for_status()
        event_type, data_buffer = None, ""

        for line in resp.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if line.startswith("event:"):
                event_type = line.split("event:", 1)[1].strip()
            elif line.startswith("data:"):
                data_buffer = line.split("data:", 1)[1].strip()
            elif line == "" and event_type and data_buffer:
                parsed = json.loads(data_buffer)
                if event_type == "node_update":
                    node = parsed.get("node")
                    yield {"type": "progress", "label": NODE_PROGRESS_LABELS.get(node, node)}
                elif event_type == "token":
                    token = parsed.get("token")
                    yield {"type": "token", "token": token}
                elif event_type == "final":
                    yield {"type": "final", "payload": parsed}
                event_type, data_buffer = None, ""
