import streamlit as st
import pandas as pd
import numpy as np
from utils.styling import init_page, clean_html
from components.ui import section_header, metric_card, footer
from core import analyze_active_dataset, calculate_quality_scores
from core.dataset_lifecycle import DatasetLoadError, load_dataset_file, store_loaded_dataset
from core.session_state import initialize_session_state

# Initialize styling
init_page("Data Control Center")

# Help helper to generate our mock dataset
def generate_mock_data():
    np.random.seed(42)
    rows = 150
    data = {
        "customer_id": [f"USR-{1000+i}" for i in range(rows)],
        "age": np.random.choice([25, 34, 45, np.nan, 29, 62, 108, 12, 38, 55], size=rows), # contains null and outliers (108)
        "monthly_charges": np.random.choice([29.99, 79.99, 89.99, np.nan, 120.0, -45.0], size=rows), # contains null and outliers (-45.0)
        "tenure_months": np.random.choice([3, 12, 24, np.nan, 36, 72, 5], size=rows),
        "churn": np.random.choice(["Yes", "No", "yes", "NO", None], size=rows), # contains casing issues & nulls
        "signup_date": pd.date_range(start="2024-01-01", periods=rows).strftime("%Y-%m-%d")
    }
    df = pd.DataFrame(data)
    # Add a couple of duplicate rows intentionally
    df = pd.concat([df, df.iloc[[12, 45, 87]]], ignore_index=True)
    return df

initialize_session_state(st.session_state)

# Title section
section_header("Data Quality Control Center", "Upload your tabular dataset to inspect completeness, health index, and ML feasibility models.", "📊")

# Top upload zone
col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload Dataset (Drag & Drop)",
        type=["csv", "xlsx", "xls", "json", "parquet", "tsv", "feather"],
    )
    if uploaded_file is not None:
        try:
            df = load_dataset_file(uploaded_file)
            store_loaded_dataset(st.session_state, df, uploaded_file.name)
            st.toast(f"Successfully loaded {uploaded_file.name}!", icon="✅")
        except DatasetLoadError as e:
            st.error(f"Error loading file: {str(e)}")

with col_sample:
    st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
    if st.button("Load Sample Churn Data", use_container_width=True):
        df_mock = generate_mock_data()
        store_loaded_dataset(st.session_state, df_mock, "customer_churn_sample.csv")
        st.session_state["history"] = [{"timestamp": "Just Now", "action": "Initialized project with Churn Dataset", "affected": "All Columns"}]
        st.toast("Loaded customer churn sample dataset!", icon="🚀")

# Dashboard Content if dataset exists
if st.session_state["dataset"] is not None:
    df = st.session_state["dataset"]
    
    # Calculate dataset stats using core backend PipelineManager
    total_rows = len(df)
    total_cols = len(df.columns)
    
    reports = analyze_active_dataset(st.session_state)
    
    # Extract specific stats
    null_cells = int(reports["MissingValuesDetector"]["statistics"]["total_null_count"])
    null_percent = float(reports["MissingValuesDetector"]["statistics"]["null_percentage"])
    duplicate_rows = int(reports["DuplicatesDetector"]["statistics"]["duplicate_count"])
    duplicate_percent = float(reports["DuplicatesDetector"]["statistics"]["duplicate_percentage"])
    
    health_score, ml_readiness = calculate_quality_scores(df, reports)

    # Metrics grid
    st.markdown("### Dataset Overview", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Total Observations", f"{total_rows:,}", icon="🔢")
    with m2:
        metric_card("Total Features", f"{total_cols}", icon="📐")
    with m3:
        metric_card("Missing Cells", f"{null_percent:.1f}%", f"{null_cells} total", is_positive=False, icon="⚠️")
    with m4:
        metric_card("Duplicate Rows", f"{duplicate_rows}", f"{duplicate_rows} rows", is_positive=False, icon="👥")

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Score Cards side by side
    score_col1, score_col2 = st.columns(2)
    
    with score_col1:
        with st.container(border=True):
            st.markdown("<span class='accent-title'>Dataset Health Score</span>", unsafe_allow_html=True)
            health_color = "#34d399" if health_score >= 80 else "#fbbf24" if health_score >= 50 else "#f87171"
            st.markdown(f"<h1 style='text-align: center; color: {health_color}; font-size: 3.5rem; margin: 0.5rem 0;'>{health_score}%</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #a1a1aa; font-size: 0.9rem; margin: 0;'>Overall score compiled from completeness, schema accuracy, and row uniqueness ratios.</p>", unsafe_allow_html=True)
        
    with score_col2:
        with st.container(border=True):
            st.markdown("<span class='accent-title'>ML Readiness Score</span>", unsafe_allow_html=True)
            ml_color = "#34d399" if ml_readiness >= 80 else "#fbbf24" if ml_readiness >= 50 else "#f87171"
            st.markdown(f"<h1 style='text-align: center; color: {ml_color}; font-size: 3.5rem; margin: 0.5rem 0;'>{ml_readiness}%</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #a1a1aa; font-size: 0.9rem; margin: 0;'>Determines viability for feature input. Looks at nulls, bounds, and categorical skewness.</p>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Active Quality Anomaly Alerts
    st.markdown("### Quality Anomaly Alerts", unsafe_allow_html=True)
    alerts_found = False
    for det_name, report in reports.items():
        if report["problem"]:
            alerts_found = True
            st.markdown(clean_html(f"""
            <div style='background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); 
                        border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.75rem; display: flex; 
                        justify-content: space-between; align-items: center;'>
                <div>
                    <strong style='color: #f87171;'>⚠️ {det_name.replace('Detector', '')}</strong>
                    <div style='color: #ffffff; font-size: 0.9rem; margin-top: 0.15rem;'>{report['problem']}</div>
                    <div style='color: #a1a1aa; font-size: 0.8rem; margin-top: 0.1rem;'><em>Suggested fix:</em> {report['solution']}</div>
                </div>
                <div style='text-align: right; min-width: 120px;'>
                    <span style='background: rgba(255,255,255,0.05); color: #e4e4e7; border-radius: 9999px; 
                                 padding: 2px 8px; font-size: 0.75rem;'>Conf: {int(report['confidence_score']*100)}%</span>
                </div>
            </div>
            """), unsafe_allow_html=True)
            
    if not alerts_found:
        st.success("🎉 No active quality anomalies detected! Your dataset is fully clean.")

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Interactive Table Preview
    st.markdown(f"### Interactive Preview: `{st.session_state['dataset_name']}`", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=350)
    
    # Detailed schema inspect accordion
    with st.expander("🔍 Detailed Schema Inspections"):
        search_col = st.text_input("🔍 Search columns by name", "", key="schema_search_col")
        schema_data = []
        for col in df.columns:
            if search_col.strip() != "" and search_col.lower() not in col.lower():
                continue
            nulls = df[col].isnull().sum()
            null_pct = (nulls / len(df)) * 100
            dtype = str(df[col].dtype)
            unique = df[col].nunique()
            schema_data.append({
                "Column Name": col,
                "Data Type": dtype,
                "Unique Values": unique,
                "Missing Values": nulls,
                "Missing %": f"{null_pct:.1f}%"
            })
        if schema_data:
            st.table(pd.DataFrame(schema_data))
        else:
            st.info("No columns match your search term.")

else:
    # Workspace overview when no data loaded
    st.markdown("### 📁 Project Workspace & Upload History", unsafe_allow_html=True)
    st.markdown("Select a recently loaded project from your workspace history to quickly resume your profiling sessions.")
    
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        with st.container(border=True):
            st.markdown("#### 📄 customer_churn_sample.csv")
            st.markdown("""
            * **Rows**: 153
            * **Columns**: 6
            * **Feasible Target**: `churn`
            * **Status**: *Draft Profile*
            """)
            if st.button("Resume Project ➔", key="resume_churn", use_container_width=True):
                df_mock = generate_mock_data()
                store_loaded_dataset(st.session_state, df_mock, "customer_churn_sample.csv")
                st.session_state["history"] = [{"timestamp": "Just Now", "action": "Initialized project from Workspace history", "affected": "All Columns"}]
                st.toast("Loaded customer churn sample from workspace history!", icon="🚀")
                st.rerun()
                
    with col_w2:
        with st.container(border=True):
            st.markdown("#### 📊 marketing_campaign_leads.xlsx")
            st.markdown("""
            * **Rows**: 200
            * **Columns**: 4
            * **Feasible Target**: `converted`
            * **Status**: *Drift Detected*
            """)
            if st.button("Load Leads Dataset ➔", key="resume_leads", use_container_width=True):
                # Generate a mock leads dataset
                np.random.seed(10)
                leads_data = {
                    "lead_id": [f"LD-{1000+i}" for i in range(200)],
                    "campaign_channel": np.random.choice(["Social", "Email", "SEO", "PPC"], size=200),
                    "leads_score": np.random.uniform(10.0, 100.0, size=200),
                    "converted": np.random.choice([0, 1], size=200)
                }
                df_leads = pd.DataFrame(leads_data)
                store_loaded_dataset(st.session_state, df_leads, "marketing_campaign_leads.xlsx")
                st.session_state["history"] = [{"timestamp": "Just Now", "action": "Loaded campaign dataset from history", "affected": "All Columns"}]
                st.toast("Loaded marketing campaign leads dataset!", icon="🚀")
                st.rerun()

    with col_w3:
        with st.container(border=True):
            st.markdown("#### 🏠 boston_housing_dirty.csv")
            st.markdown("""
            * **Rows**: 150
            * **Columns**: 4
            * **Feasible Target**: `medv`
            * **Status**: *Clean Pipeline Run*
            """)
            if st.button("Load Boston Dataset ➔", key="resume_boston", use_container_width=True):
                # Generate a mock boston dataset
                np.random.seed(20)
                boston_data = {
                    "crim": np.random.uniform(0.01, 10.0, size=150),
                    "rm": np.random.uniform(4.0, 9.0, size=150),
                    "age": np.random.uniform(2.0, 100.0, size=150),
                    "medv": np.random.uniform(5.0, 50.0, size=150)
                }
                df_boston = pd.DataFrame(boston_data)
                store_loaded_dataset(st.session_state, df_boston, "boston_housing_dirty.csv")
                st.session_state["history"] = [{"timestamp": "Just Now", "action": "Loaded Boston housing dataset from history", "affected": "All Columns"}]
                st.toast("Loaded Boston housing dataset!", icon="🚀")
                st.rerun()

    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    # Upload Zone Empty State
    with st.container(border=True):
        st.markdown(clean_html("""
        <div style='text-align: center; padding: 2rem 1rem;'>
            <span style='font-size: 3rem;'>📥</span>
            <h3 style='margin-top: 1rem; color: #ffffff;'>No active dataset loaded</h3>
            <p style='color: #a1a1aa; max-width: 400px; margin: 0.5rem auto 0 auto;'>
                Drag and drop a CSV/Excel file or click a card above to begin.
            </p>
        </div>
        """), unsafe_allow_html=True)

# Footer
footer()
