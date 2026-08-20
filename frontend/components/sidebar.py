import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🩺 AgentMed AI")
        st.caption("Multi-agent medical information assistant")

        if "disclaimer_accepted" not in st.session_state:
            st.session_state.disclaimer_accepted = False

        if not st.session_state.disclaimer_accepted:
            st.warning(
                "This tool provides general health information only and is "
                "**not** a substitute for professional medical advice. "
                "In an emergency, call your local emergency number."
            )
            if st.button("I understand, continue"):
                st.session_state.disclaimer_accepted = True
                st.rerun()

        st.divider()
        st.markdown("#### Optional patient context")
        st.caption("Helps agents give more relevant, safer answers.")

        age = st.number_input("Age", min_value=0, max_value=120, value=0, step=1)
        sex = st.selectbox("Sex", ["unspecified", "male", "female", "other"])
        allergies = st.text_input("Known allergies (comma-separated)")
        meds = st.text_input("Current medications (comma-separated)")

        st.session_state.patient_context = {
            "age": age or None,
            "sex": sex,
            "known_allergies": [a.strip() for a in allergies.split(",") if a.strip()],
            "current_medications": [m.strip() for m in meds.split(",") if m.strip()],
        }

        st.divider()
        if st.button("🆕 Start new consultation"):
            for key in ("session_id", "messages"):
                st.session_state.pop(key, None)
            st.rerun()

        st.divider()
        st.caption("Built with FastAPI · LangGraph · MCP · Groq · Streamlit")
