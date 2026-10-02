import streamlit as st

from core.session_state import initialize_session_state
from utils.styling import load_custom_css

PAGES = {
    "🏠 Home": "views/home.py",
    "📂 Upload Dataset": "views/upload_dataset.py",
    "📊 Dashboard": "views/dashboard.py",
    "🧹 Data Cleaning": "views/cleaning.py",
    "📈 Analytics": "views/analytics.py",
    "📉 Visualization Studio": "views/visualization_studio.py",
    "🧠 AI Assistant": "views/ai_assistant.py",
    "📋 Reports": "views/reports.py",
    "📤 Export": "views/export.py",
    "⚙ Settings": "views/settings.py",
    "📚 Documentation": "views/documentation.py",
    "ℹ️ About": "views/about.py",
}

PAGE_SECTIONS = {
    "MAIN": ["🏠 Home", "📂 Upload Dataset", "📊 Dashboard"],
    "DATA QUALITY": ["🧹 Data Cleaning", "📈 Analytics", "📉 Visualization Studio"],
    "AI & INSIGHTS": ["🧠 AI Assistant", "📋 Reports"],
    "TOOLS": ["📤 Export", "⚙ Settings"],
        "HELP": ["📚 Documentation", "ℹ️ About"],
}

st.set_page_config(
    page_title="CleanAI – Intelligent Data Quality & ML Readiness",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_custom_css()

initialize_session_state(st.session_state)

st.sidebar.markdown(
    """
    <div style='text-align: center; padding-top: 1rem; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.2rem; font-weight: 800; margin: 0; line-height: 1; font-family: Outfit, sans-serif;'>
            <span class='brand-gradient'>CleanAI</span>
        </h1>
        <span style='font-size: 0.7rem; color: #71717a; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; display: block; margin-top: 0.25rem;'>
            Intelligent Data Quality
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

navigation_pages = [
    st.Page(
        page_path,
        title=page_title,
        url_path=page_path.removesuffix(".py").removeprefix("views/"),
        default=page_title == "🏠 Home",
    )
    for page_title, page_path in PAGES.items()
]

pages_by_title = dict(zip(PAGES, navigation_pages))
navigation = {
    section: [pages_by_title[page_title] for page_title in page_titles]
    for section, page_titles in PAGE_SECTIONS.items()
}
current_page = st.navigation(navigation, position="hidden")
st.session_state["active_page"] = current_page.title

for section, page_titles in PAGE_SECTIONS.items():
    st.sidebar.markdown(f"<div class='sidebar-section-title'>{section}</div>", unsafe_allow_html=True)
    for page_title in page_titles:
        st.sidebar.page_link(pages_by_title[page_title], label=page_title)

dataset = st.session_state.get("dataset")
if dataset is None:
    sidebar_status = "● Dataset not loaded"
else:
    sidebar_status = (
        f"● Dataset loaded<br><strong>{st.session_state.get('dataset_name', 'Unnamed dataset')}</strong>"
        f"<br>{len(dataset):,} rows · {len(dataset.columns):,} columns"
    )
st.sidebar.markdown(
    f"<div class='sidebar-status'>{sidebar_status}</div>",
    unsafe_allow_html=True,
)
current_page.run()
