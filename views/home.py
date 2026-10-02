import streamlit as st
from utils.styling import init_page
from components.ui import hero_section, feature_card, footer

# Initialize style overlays
init_page("Platform Overview")

# Hero Section
hero_section(
    title="CleanAI – Intelligent Data Quality & ML Readiness",
    subtitle="Accelerate your AI pipeline. Clean datasets, detect anomalies, measure ML readiness, and collaborate with our context-aware AI Data Assistant in real-time.",
    badge_text="Now Live: CleanAI 2.0 with ML Feature Scoring"
)

# Call-to-actions
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Enter Dashboard ➔", use_container_width=True):
        st.switch_page("views/dashboard.py")

st.markdown("<div style='margin-bottom: 4rem;'></div>", unsafe_allow_html=True)

# Platform capabilities
st.markdown("<h3 style='text-align: center; color: #a1a1aa; font-size: 0.9rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 2rem;'>Built-in Data Quality Workflow</h3>", unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; color: #ffffff; margin: 0;'>10</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #71717a; font-size: 0.75rem; text-transform: uppercase; margin: 0.5rem 0 0 0;'>Quality Detectors</p>", unsafe_allow_html=True)
with m_col2:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; color: #ffffff; margin: 0;'>14</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #71717a; font-size: 0.75rem; text-transform: uppercase; margin: 0.5rem 0 0 0;'>Cleaning Strategies</p>", unsafe_allow_html=True)
with m_col3:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; color: #ffffff; margin: 0;'>7</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #71717a; font-size: 0.75rem; text-transform: uppercase; margin: 0.5rem 0 0 0;'>Upload Formats</p>", unsafe_allow_html=True)
with m_col4:
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; color: #ffffff; margin: 0;'>2</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #71717a; font-size: 0.75rem; text-transform: uppercase; margin: 0.5rem 0 0 0;'>History Controls</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 4rem;'></div>", unsafe_allow_html=True)

# Feature grid
st.markdown("<h2 style='text-align: center; color: #ffffff; font-size: 1.8rem; font-weight: 700; margin-bottom: 3rem;'>Enterprise-Grade Data Scaffolding</h2>", unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    feature_card(
        title="Automated Data Profiling",
        description="Instantly generate schemas, assess data completeness, track drift, and view missing value heatmaps with our high-performance profiling engine.",
        icon="🔍"
    )
with f_col2:
    feature_card(
        title="One-Click Anomalies Cleaning",
        description="Handle outliers, impute missing numbers using mean, median, mode, or KNN, normalize categories, and remove identical records with configurable safety guidelines.",
        icon="🧹"
    )
with f_col3:
    feature_card(
        title="Generative AI Co-Pilot",
        description="Discuss your dataset directly with a GPT model trained on data quality protocols. Instruct changes through standard text commands.",
        icon="🤖"
    )

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

f_col4, f_col5, f_col6 = st.columns(3)
with f_col4:
    feature_card(
        title="Interactive Dashboards",
        description="Interact with charts that automatically map feature distributions, check correlations, and display class imbalances cleanly.",
        icon="📈"
    )
with f_col5:
    feature_card(
        title="Production Readiness Report",
        description="Render and download PDF compliance sheets outlining column null thresholds, quality indices, and model training feasibility checks.",
        icon="📄"
    )
with f_col6:
    feature_card(
        title="Audit Logs & Session Settings",
        description="Review execution history, rollback applied edits, and connect storage APIs with secure credentials store management.",
        icon="⚙"
    )

# Footer
footer()
