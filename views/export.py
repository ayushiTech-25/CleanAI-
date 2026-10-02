import streamlit as st
import pandas as pd
import io
import json

from utils.styling import init_page
from components.ui import section_header

init_page("Export")
section_header("Export Center", "Download cleaned data, summaries, and reports in common ML and analytics formats.", "📤")

if st.session_state.get("dataset") is not None:
    df = st.session_state["dataset"]

    st.markdown("### Download your outputs")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False),
            file_name="cleanai_dataset.csv",
            mime="text/csv",
            width="stretch",
        )

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            "Download Excel",
            data=excel_buffer.getvalue(),
            file_name="cleanai_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    with col2:
        st.download_button(
            "Download JSON",
            data=df.to_json(orient="records", indent=2),
            file_name="cleanai_dataset.json",
            mime="application/json",
            width="stretch",
        )
        try:
            parquet_data = df.to_parquet(index=False)
            st.download_button(
                "Download Parquet",
                data=parquet_data,
                file_name="cleanai_dataset.parquet",
                mime="application/octet-stream",
                width="stretch",
            )
        except (ImportError, ValueError) as exc:
            st.warning(f"Parquet export is unavailable in this environment: {exc}")

    with col3:
        summary = df.describe(include="all").to_csv()
        st.download_button(
            "Download Summary CSV",
            data=summary,
            file_name="data_summary.csv",
            mime="text/csv",
            width="stretch",
        )

        st.download_button(
            "Download Log JSON",
            data=json.dumps(st.session_state.get("history", []), indent=2),
            file_name="cleanai_history.json",
            mime="application/json",
            width="stretch",
        )

    st.dataframe(df.head(25), width="stretch")
else:
    st.info("Load a dataset to enable export actions.")
