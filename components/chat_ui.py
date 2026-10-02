import streamlit as st
from typing import List, Dict

def render_chat_ui(messages: List[Dict[str, str]], container_height: int = 450) -> None:
    """
    Renders historical message bubbles inside a native scrollable container block.
    """
    with st.container(height=container_height):
        for msg in messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["text"])
