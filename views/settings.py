import streamlit as st
from utils.styling import init_page
from components.ui import section_header, footer

# Initialize page
init_page("Platform Settings")

section_header("Platform Configurations", "Manage API connection keys, profiling thresholds, and database connection strings.", "⚙")

# Create tabs for settings categories
tab_api, tab_thresholds, tab_db, tab_pref = st.tabs(["🔑 API Keys", "🎚 Quality Thresholds", "🔌 Database Connectors", "🎨 Preferences & Shortcuts"])

with tab_api:
    st.markdown("### AI Co-Pilot Integrations", unsafe_allow_html=True)
    st.markdown("Enter API keys below to enable conversational reasoning and smart imputation logic.")
    
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-proj-...", help="Used for chat assistance and summary code generation.")
    anthropic_key = st.text_input("Anthropic Claude API Key", type="password", placeholder="sk-ant-...", help="Alternative model for advanced profiling reasoning.")
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...", help="Used for multimodality analysis.")
    
    if st.button("Save Credentials"):
        st.session_state["settings_api_keys"] = {
            "OPENAI_API_KEY": openai_key.strip(),
            "ANTHROPIC_API_KEY": anthropic_key.strip(),
            "GEMINI_API_KEY": gemini_key.strip(),
        }
        st.success("Credentials saved for this session. Values are not displayed or written to disk.")

with tab_thresholds:
    st.markdown("### System Flag Thresholds", unsafe_allow_html=True)
    st.markdown("Customize flags which impact the Dataset Health Score and ML Readiness calculations.")
    
    null_warning = st.slider("Missing values warning limit (%)", 1, 50, 10, help="Flags columns with missing cell ratios exceeding this rate.")
    outlier_limit = st.slider("Outliers density warning limit (%)", 1, 30, 5, help="Flags features containing high density distribution outliers.")
    cardinality_limit = st.number_input("High Cardinality threshold", min_value=10, max_value=500, value=50, step=10, help="Classifies text categories as high cardinality if unique values exceed this count.")
    
    if st.button("Save Threshold Parameters"):
        st.session_state["quality_thresholds"] = {
            "null_warning_percent": null_warning,
            "outlier_limit_percent": outlier_limit,
            "cardinality_limit": cardinality_limit,
        }
        st.toast("Updated warning rulesets successfully.", icon="🎚")

with tab_db:
    st.markdown("### Data Warehouses & Integrations", unsafe_allow_html=True)
    st.markdown("Connect pipelines directly to relational databases to pull clean datasets directly.")
    
    db_type = st.selectbox("Database Type", ["PostgreSQL", "Snowflake", "Google BigQuery", "AWS Redshift", "MySQL"])
    db_host = st.text_input("Host Address", placeholder="db.example.gcp.com")
    db_port = st.number_input("Port", value=5432)
    db_name = st.text_input("Database Name", placeholder="production_ml_data")
    db_user = st.text_input("Username", placeholder="cleanai_reader")
    db_pass = st.text_input("Password", type="password")
    
    col_test, col_save = st.columns(2)
    with col_test:
        if st.button("Test Connection Link", use_container_width=True, type="secondary"):
                st.info("Configuration preview only. Live database connections are not implemented.")
    with col_save:
        if st.button("Register Data Source", use_container_width=True):
            st.session_state["database_configuration"] = {
                "type": db_type,
                "host": db_host.strip(),
                "port": int(db_port),
                "name": db_name.strip(),
                "user": db_user.strip(),
            }
            st.success("Database configuration preview saved for this session; no connection was opened.")

with tab_pref:
    st.markdown("### Preferences & Client Layout Settings", unsafe_allow_html=True)
    
    # 1. Dark/Light Mode Theme Selection
    theme_mode = st.selectbox("Application Color Palette Theme", ["Dark Mode (Premium Glassmorphic)", "Workspace Light Mode"], key="sb_theme_mode")
    
    if theme_mode == "Workspace Light Mode":
        st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f4f4f5 !important;
            background-image: none !important;
            color: #18181b !important;
        }
        .glass-card, [data-testid="stVerticalBlockBorder"], [data-testid="stContainerBorder"] {
            background: #ffffff !important;
            border: 1px solid #e4e4e7 !important;
            color: #18181b !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        }
        h1, h2, h3, h4, h5, h6, p, label, span, div, th, td {
            color: #18181b !important;
        }
        .accent-title {
            color: #4f46e5 !important;
        }
        .brand-gradient {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        </style>
        """, unsafe_allow_html=True)
        st.toast("Switched workspace theme to Light Mode!", icon="🎨")
        
    # 2. System Alerts
    st.markdown("#### System Alerts & Notifications Settings", unsafe_allow_html=True)
    st.checkbox("Enable in-app Toast Notification banners on successful repair steps", value=True)
    st.checkbox("Show ML readiness status badges in document exports", value=True)
    st.checkbox("Send webhook triggers on automated dataset pipeline rollbacks", value=False)
    
    # 3. Keyboard Shortcuts Cheat Sheet
    st.markdown("#### Platform Keyboard Shortcuts Cheatsheet", unsafe_allow_html=True)
    st.markdown("""
    | Keybinding Combo | Action Command Triggered | Scope |
    | :--- | :--- | :--- |
    | `Ctrl + Z` | Undo last applied cleaning step pipeline action | Repairs View |
    | `Ctrl + Y` | Redo last reverted cleaning step pipeline action | Repairs View |
    | `Ctrl + Enter` | Trigger repairs script compile handshake | Pipeline Controls |
    | `Esc` | Focus out of active LLM chat query message input | AI Co-pilot Panel |
    """)

footer()
