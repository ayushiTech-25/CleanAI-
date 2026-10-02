import streamlit as st
import pandas as pd

from utils.styling import init_page
from components.ui import section_header
from core.dataset_lifecycle import DatasetLoadError, load_dataset_file, store_loaded_dataset

init_page("Upload Dataset")
section_header("Upload Dataset", "Load CSV, Excel, JSON, Parquet, and other tabular files for analysis and cleaning.", "📂")

st.markdown("### Data Upload Center")

uploaded_file = st.file_uploader(
    "Upload a dataset",
    type=["csv", "xlsx", "xls", "json", "parquet", "tsv", "feather"],
    help="CSV, Excel, JSON, Parquet, TSV, or Feather files are supported."
)

if uploaded_file is not None:
    try:
        df = load_dataset_file(uploaded_file)
        store_loaded_dataset(st.session_state, df, uploaded_file.name)
        st.success(f"Dataset loaded successfully: {uploaded_file.name}")
        st.dataframe(df.head(20), use_container_width=True)
    except DatasetLoadError as exc:
        st.error(f"Unable to load dataset: {exc}")
else:
    st.info("Choose a dataset from your computer to begin quality profiling.")

    st.markdown("### Supported formats")
    cols = st.columns(4)
    for idx, label in enumerate(["CSV", "Excel", "JSON", "Parquet"]):
        with cols[idx]:
            st.markdown(
                f"<div style='padding: 1rem; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; text-align: center;'><h4>{label}</h4></div>",
                unsafe_allow_html=True,
            )

    st.markdown("### Quick actions")
    if st.button("Load sample churn dataset", use_container_width=True):
        import numpy as np
        rows = 120
        df = pd.DataFrame({
            "customer_id": [f"USR-{1000+i}" for i in range(rows)],
            "age": np.random.choice([25, 34, 45, np.nan, 62, 38, 54], size=rows),
            "monthly_charges": np.random.choice([39.99, 79.99, 99.99, np.nan, 150.0], size=rows),
            "tenure_months": np.random.choice([3, 12, 24, 36, np.nan, 72], size=rows),
            "churn": np.random.choice(["Yes", "No", "yes", "NO", None], size=rows),
        })
        store_loaded_dataset(st.session_state, df, "sample_churn.csv")
        st.success("Sample dataset loaded.")
