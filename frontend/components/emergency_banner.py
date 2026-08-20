import streamlit as st

def render_emergency_banner():
    st.markdown(
        """
        <div style="background-color:#dc2626;color:white;padding:14px 20px;
                    border-radius:8px;margin-bottom:12px;font-weight:600;">
        ⚠️ Emergency indicators detected. If this is a life-threatening situation,
        call your local emergency number now (e.g. 911 / 112 / 108) or go to the
        nearest emergency room.
        </div>
        """,
        unsafe_allow_html=True,
    )
