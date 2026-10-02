import streamlit as st
import os

def load_custom_css():
    """Reads style.css and injects it as raw HTML style into the app."""
    # Resolve style.css path relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_path = os.path.join(base_dir, "assets", "css", "style.css")
    
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.error(f"Styles not found at: {css_path}")

def init_page(title="CleanAI"):
    """
    Initializes standard UI overrides and loads styling.
    Note: st.set_page_config should be called in app.py first.
    """
    load_custom_css()

def clean_html(html_str: str) -> str:
    """Strips leading whitespace from each line of HTML and joins with no newlines to prevent code-block escaping."""
    if not html_str:
        return ""
    return "".join(line.strip() for line in html_str.split("\n"))
