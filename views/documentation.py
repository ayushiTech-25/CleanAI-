import streamlit as st

from utils.styling import init_page
from components.ui import section_header

init_page("Documentation")
section_header("Documentation", "Reference the CleanAI platform guides and operational workflow.", "📖")

st.markdown("### Platform Overview")
st.markdown("- Upload a dataset from the Data Upload page or load a sample dataset.")
st.markdown("- Review the dashboard to inspect data quality, missingness, and ML readiness.")
st.markdown("- Use the cleaning page to apply imputation, outlier handling, and normalization strategies.")
st.markdown("- Explore visual insights in the Visualization Studio.")
st.markdown("- Ask the AI Assistant for dataset guidance and recommendations.")
st.markdown("- Export results from the Reports and Export pages.")

st.markdown("### Typical workflow")
steps = [
    "1. Upload data",
    "2. Inspect quality scores",
    "3. Apply cleaning rules",
    "4. Review analytics",
    "5. Generate export or PDF report",
]
for step in steps:
    st.markdown(step)

st.markdown("### Enterprise features supported")
for feature in ["Missing-value detection", "Outlier management", "Duplicate removal", "ML readiness scoring", "Plotly dashboards", "AI-assisted analysis"]:
    st.markdown(f"- {feature}")
