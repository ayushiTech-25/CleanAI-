import streamlit as st

def render_chat_message(role: str, text: str, time_str: str = "Just now"):
    """
    Generates a beautifully formatted HTML speech bubble matching the Dark/Glassmorphic theme.
    Returns the HTML string to be injected.
    """
    align = "flex-end" if role == "user" else "flex-start"
    bubble_class = "chat-user" if role == "user" else "chat-ai"
    avatar = "👤" if role == "user" else "🤖"
    name = "You" if role == "user" else "CleanAI Assistant"
    
    html = f"""
    <div style='display: flex; flex-direction: column; align-items: {align}; width: 100%; margin-bottom: 1.25rem;' class='animate-fade-in'>
        <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem; font-size: 0.8rem; color: #71717a;'>
            <span>{avatar}</span>
            <span style='font-weight: 600; color: #a1a1aa;'>{name}</span>
            <span>•</span>
            <span>{time_str}</span>
        </div>
        <div class='chat-bubble {bubble_class}' style='white-space: pre-wrap;'>{text}</div>
    </div>
    """
    return clean_html(html)

def render_suggestion_chips(suggestions: list):
    """
    Displays grid-aligned button suggestions that users can prompt next.
    Returns the selected suggestion if clicked, else None.
    """
    selected = None
    cols_per_row = 3
    
    # Render suggestion buttons in rows of cols_per_row columns to ensure adequate spacing
    for i in range(0, len(suggestions), cols_per_row):
        chunk = suggestions[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for j, sug in enumerate(chunk):
            with cols[j]:
                if st.button(sug, key=f"sug_{i+j}", use_container_width=True, type="secondary"):
                    selected = sug
    return selected
