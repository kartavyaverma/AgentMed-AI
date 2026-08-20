import os

import streamlit as st
from dotenv import load_dotenv

from frontend.components.chat_ui import render_message, stream_chat_response
from frontend.components.sidebar import render_sidebar

load_dotenv()
BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AgentMed AI", layout="centered")

render_sidebar()

if not st.session_state.get("disclaimer_accepted"):
    st.title("AgentMed AI")
    st.info("Please accept the disclaimer in the sidebar to begin.")
    st.stop()

st.title("AgentMed AI")
st.caption("Ask about symptoms, general health info, or medication questions.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

for msg in st.session_state.messages:
    render_message(
        msg["role"], msg["content"], msg.get("sources"), msg.get("is_emergency", False)
    )

user_input = st.chat_input("Describe your symptoms or ask a question…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_message("user", user_input)

    with st.chat_message("assistant"):
        progress_placeholder = st.empty()
        text_placeholder = st.empty()
        accumulated_text = ""
        final_payload = None

        try:
            for event in stream_chat_response(
                BACKEND_BASE_URL,
                st.session_state.session_id,
                user_input,
                st.session_state.patient_context,
            ):
                if event["type"] == "progress":
                    progress_placeholder.markdown(f"*{event['label']}*")
                elif event["type"] == "token":
                                                                            
                    progress_placeholder.empty()
                    accumulated_text += event["token"]
                    text_placeholder.markdown(accumulated_text)
                elif event["type"] == "final":
                    final_payload = event["payload"]
        except Exception as exc:                
            progress_placeholder.empty()
            text_placeholder.empty()
            st.error(f"Something went wrong talking to the backend: {exc}")
            st.stop()

        progress_placeholder.empty()
        text_placeholder.empty()

        if final_payload:
            st.session_state.session_id = final_payload["session_id"]

            if final_payload.get("is_emergency"):
                from frontend.components.emergency_banner import render_emergency_banner
                render_emergency_banner()

            st.markdown(final_payload["answer"])

            sources = final_payload.get("sources", [])
            if sources:
                with st.expander(f"Sources ({len(sources)})"):
                    for s in sources:
                        title = s.get("title", "Untitled")
                        url = s.get("url")
                        st.markdown(f"- [{title}]({url})" if url else f"- {title}")

            st.caption(final_payload.get("disclaimer", ""))

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": final_payload["answer"],
                    "sources": sources,
                    "is_emergency": final_payload.get("is_emergency", False),
                }
            )
