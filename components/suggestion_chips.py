import streamlit as st
from typing import List, Optional

def render_suggestion_chips(suggestions: List[str], key_prefix: str = "sug_chip") -> Optional[str]:
    """
    Displays clickable suggestion chips in a uniform grid, returning
    the selected value on click.
    """
    selected = None
    cols_per_row = 3
    
    for i in range(0, len(suggestions), cols_per_row):
        chunk = suggestions[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for j, sug in enumerate(chunk):
            with cols[j]:
                if st.button(sug, key=f"{key_prefix}_{i+j}", use_container_width=True, type="secondary"):
                    selected = sug
    return selected
