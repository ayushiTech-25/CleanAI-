import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.styling import init_page
from components.ui import section_header

init_page("Visualization Studio")
section_header("Visualization Studio", "Explore interactive charts for distributions, correlations, outliers, and feature relationships.", "📉")

if st.session_state.get("dataset") is not None:
    df = st.session_state["dataset"]
    st.markdown("### Chart Builder")
    chart_type = st.selectbox(
        "Select chart type",
        ["Histogram", "Scatter", "Bar", "Line", "Pie", "Heatmap", "Box Plot", "Violin Plot", "Correlation Matrix"],
    )

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    if chart_type == "Histogram":
        col = st.selectbox("Column", numeric_cols or df.columns.tolist())
        fig = px.histogram(df, x=col, nbins=25, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter":
        x_col = st.selectbox("X axis", numeric_cols or df.columns.tolist(), key="viz_x")
        y_col = st.selectbox("Y axis", numeric_cols or df.columns.tolist(), key="viz_y")
        fig = px.scatter(df, x=x_col, y=y_col, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Bar":
        x_col = st.selectbox("Category", cat_cols or df.columns.tolist(), key="viz_bar_x")
        y_col = st.selectbox("Value", numeric_cols or df.columns.tolist(), key="viz_bar_y")
        fig = px.bar(df, x=x_col, y=y_col, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Line":
        x_col = st.selectbox("X axis", df.columns.tolist(), key="viz_line_x")
        y_col = st.selectbox("Y axis", numeric_cols or df.columns.tolist(), key="viz_line_y")
        fig = px.line(df, x=x_col, y=y_col, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie":
        col = st.selectbox("Category", cat_cols or df.columns.tolist())
        fig = px.pie(df, names=col, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Heatmap":
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            fig = px.imshow(corr, template="plotly_dark", title="Numeric Feature Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("A heatmap requires at least two numeric columns.")

    elif chart_type == "Box Plot":
        col = st.selectbox("Numeric column", numeric_cols or df.columns.tolist())
        fig = px.box(df, y=col, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Violin Plot":
        col = st.selectbox("Numeric column", numeric_cols or df.columns.tolist())
        fig = px.violin(df, y=col, box=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Correlation Matrix":
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            fig = px.imshow(corr.round(3), text_auto=True, color_continuous_scale="Viridis", template="plotly_dark", title="Pearson Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("A correlation matrix requires at least two numeric columns.")

    st.dataframe(df.head(20), use_container_width=True)
else:
    st.info("Load a dataset first to render the visualization studio.")
