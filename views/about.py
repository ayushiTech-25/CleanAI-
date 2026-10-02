import streamlit as st
from utils.styling import init_page
from components.ui import section_header, footer, status_badge

# Initialize page
init_page("About Platform")

section_header("About CleanAI Platform", "System architectures, SOLID framework designs, and accessibility guidelines.", "ℹ️")

col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.markdown("<span class='accent-title'>Core Technology Stack</span>", unsafe_allow_html=True)
        st.markdown("""
        CleanAI leverages modern, high-performance data science and machine learning libraries:
        - **Frontend Shell**: Streamlit (wide layout engine) styled with custom CSS overrides.
        - **Visualizations**: Plotly Express (rendering dynamic heatmaps, correlation grids, and box plots).
        - **Data Wrangling**: Pandas (vectorized series transformations) and NumPy.
        - **Machine Learning**: Scikit-Learn (KNN Imputation, Standard/MinMax Scalers, Isolation Forest anomalies).
        - **Generative AI Engine**: Google Gemini API via lightweight HTTP REST clients.
        - **Document Reporting**: FPDF2 (compiled vector PDFs) and OpenPyXL (Excel engine).
        """)

    with st.container(border=True):
        st.markdown("<span class='accent-title'>Keyboard Shortcuts Cheat Sheet</span>", unsafe_allow_html=True)
        st.markdown("""
        Streamlit and CleanAI support quick browser-based keyboard actions:
        * <span class='kbd-badge'>R</span> : Rerun the current application view.
        * <span class='kbd-badge'>C</span> : Clear cache and reload data arrays.
        * <span class='kbd-badge'>Tab</span> : Cycle through forms and input buttons sequentially.
        * <span class='kbd-badge'>Space</span> / <span class='kbd-badge'>Enter</span> : Submit active sliders or checkbox configurations.
        """, unsafe_allow_html=True)

with col_right:
    with st.container(border=True):
        st.markdown("<span class='accent-title'>SOLID Architecture Patterns</span>", unsafe_allow_html=True)
        st.markdown("""
        The cleaning engine is designed following strict object-oriented paradigms:
        1. **Single Responsibility (SRP)**: Each detector (e.g. `MissingValuesDetector`) is isolated to a single calculation.
        2. **Open/Closed (OCP)**: Cleaners inherit from `BaseCleaner`. Adding new repairs (e.g., TargetEncoder) requires creating a subclass, avoiding modifications to existing code.
        3. **Liskov Substitution (LSP)**: All detectors return a uniform structured dictionary diagnosis report.
        4. **Interface Segregation (ISP)**: Concrete classes implement only their designated method contracts.
        5. **Dependency Inversion (DIP)**: View pages import from the `BaseDetector` and `BaseCleaner` abstraction interfaces, not direct modules.
        """)

    with st.container(border=True):
        st.markdown("<span class='accent-title'>Accessibility & Optimizations</span>", unsafe_allow_html=True)
        st.markdown("""
        We optimize accessibility and rendering speeds:
        - **ARIA Labels**: Screen-reader friendly structures for forms and sliders.
        - **High Contrast**: Dark Zinc background matching bright Indigo/Purple status tags.
        - **State Caching**: `@st.cache_data` bindings prevent redundant calculations on data re-loads.
        - **Dockerized footprint**: Multi-stage Docker builds reduce image layers to optimize memory load.
        """)

footer()
