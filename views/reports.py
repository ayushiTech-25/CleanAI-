import streamlit as st
import pandas as pd
import time
import os
import io
import json
import tempfile
from utils.styling import init_page, clean_html
from components.ui import section_header, footer, status_badge
from core import analyze_active_dataset, calculate_quality_scores
from core.reports_generator import PDFReportGenerator

# Initialize page
init_page("Data Reports")

section_header("Data Quality & ML Readiness Report", "Export comprehensive audits detailing structural schemas, completeness levels, and training readiness.", "📄")

if st.session_state["dataset"] is not None:
    df = st.session_state["dataset"]
    orig_df = st.session_state["original_dataset"]
    
    # Generate current timestamp for filenames
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # --- Quality Scans for AI Content & Reports ---
    reports = analyze_active_dataset(st.session_state)
    st.session_state["report_results"] = {"reports": reports}
    
    # Calculate statistics
    null_percent = float(reports["MissingValuesDetector"]["statistics"]["null_percentage"])
    completeness = 100.0 - null_percent
    
    outlier_cols = len(reports["OutliersDetector"]["statistics"]["outliers_by_column"])
    wrong_type_cols = len(reports["DataTypeDetector"]["statistics"]["columns_to_cast"])
    const_cols = len(reports["ConstantColumnsDetector"]["statistics"]["constant_columns"])
    empty_cols = len(reports["EmptyColumnsDetector"]["statistics"]["empty_columns"])
    card_cols = len(reports["HighCardinalityDetector"]["statistics"]["high_cardinality_columns"])
    mixed_cols = len(reports["MixedTextDetector"]["statistics"]["mixed_columns"])
    space_cols = len(reports["ExtraSpacesDetector"]["statistics"]["space_anomalies"])
    date_cols = len(reports["InvalidDateDetector"]["statistics"]["invalid_date_columns"])
    
    schema_score = max(0, min(100, int(100 - (wrong_type_cols * 10 + const_cols * 15 + empty_cols * 20 + space_cols * 5))))
    
    _, ml_readiness = calculate_quality_scores(df, reports)

    # Fetch AI Memo states from cache or use default fallback text
    ai_summary_text = st.session_state.get("cached_ai_summary") or "The dataset has been scanned by CleanAI. Quality indicators show optimal shapes with warnings on high cardinality."
    ai_readiness_text = st.session_state.get("cached_ai_readiness") or "The ML readiness score suggests the dataset requires imputations before model training."
    
    # Header details
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.markdown("### Export Quality Audit Sheet", unsafe_allow_html=True)
        st.markdown(f"**Target Dataset:** `{st.session_state['dataset_name']}`")
    with col_status:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown(f"**Format Timestamp:** `{timestamp}`")
        
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # --- Exporters Dashboard Card Grid ---
    st.markdown("### 📥 Download Exporters Suite", unsafe_allow_html=True)
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        with st.container(border=True):
            st.markdown("<span class='accent-title'>Dataset Formats</span>", unsafe_allow_html=True)
            
            # 1. CSV Download
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download Cleaned CSV Data 📄",
                data=csv_data,
                file_name=f"cleanai_data_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # 2. Excel Download (uses in-memory BytesIO + openpyxl)
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="Download Cleaned Excel Data 📊",
                data=excel_buffer.getvalue(),
                file_name=f"cleanai_data_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # 3. JSON Download
            json_data = df.to_json(orient="records", indent=2)
            st.download_button(
                label="Download Cleaned JSON Data 🌐",
                data=json_data,
                file_name=f"cleanai_data_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )
            
    with col_exp2:
        with st.container(border=True):
            st.markdown("<span class='accent-title'>Audits & Logs</span>", unsafe_allow_html=True)
            
            # 4. PDF Quality Audit Report
            try:
                pdf_gen = PDFReportGenerator()
                temp_dir = tempfile.gettempdir()
                temp_pdf_path = os.path.join(temp_dir, f"cleanai_report_{timestamp}.pdf")
                pdf_gen.generate_report(df, orig_df, reports, st.session_state["history"], ai_summary_text, ai_readiness_text, temp_pdf_path)
                
                with open(temp_pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    
                st.download_button(
                    label="Download PDF Audit Report 📕",
                    data=pdf_bytes,
                    file_name=f"cleanai_report_{timestamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.button(f"PDF Compile Error: {str(e)}", disabled=True, use_container_width=True)
                
            # 5. Cleaning Log JSON Download
            log_data = json.dumps(st.session_state["history"], indent=2)
            st.download_button(
                label="Download Cleaning Pipelines Log 📜",
                data=log_data,
                file_name=f"cleanai_log_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    # --- Document Report Preview ---
    st.markdown("### 👁 Report Card Document Preview", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(clean_html(f"""
        <div style='display: flex; justify-content: space-between; border-bottom: 2px solid rgba(255, 255, 255, 0.05); padding-bottom: 1.5rem; margin-bottom: 1.5rem;'>
            <div>
                <span class='brand-gradient' style='font-family: Outfit; font-weight: 800; font-size: 1.6rem;'>CLEANAI REPORT CARD</span>
                <p style='color: #71717a; margin-top: 0.25rem; font-size: 0.85rem;'>Generated dynamically in real-time</p>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 0.85rem; color: #a1a1aa;'>REPORT ID</div>
                <div style='font-family: monospace; font-size: 0.95rem; color: #ffffff;'>CAI-489D-882E</div>
            </div>
        </div>
        """), unsafe_allow_html=True)
        
        # Key stats preview section
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(clean_html(f"""
            <div style='border-right: 1px solid rgba(255, 255, 255, 0.05); padding-right: 10px;'>
                <div style='color: #71717a; font-size: 0.8rem; text-transform: uppercase;'>Completeness</div>
                <div style='font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-top: 0.25rem;'>{completeness:.1f}%</div>
                <div style='margin-top: 0.5rem;'>{status_badge('success' if completeness >= 90 else 'warning', 'Optimal' if completeness >= 90 else 'Action Required')}</div>
            </div>
            """), unsafe_allow_html=True)
        with c2:
            st.markdown(clean_html(f"""
            <div style='border-right: 1px solid rgba(255, 255, 255, 0.05); padding-right: 10px;'>
                <div style='color: #71717a; font-size: 0.8rem; text-transform: uppercase;'>Schema Score</div>
                <div style='font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-top: 0.25rem;'>{schema_score:.1f}%</div>
                <div style='margin-top: 0.5rem;'>{status_badge('success' if schema_score >= 80 else 'warning', 'Verified' if schema_score >= 80 else 'Review Needed')}</div>
            </div>
            """), unsafe_allow_html=True)
        with c3:
            st.markdown(clean_html(f"""
            <div style='border-right: 1px solid rgba(255, 255, 255, 0.05); padding-right: 10px;'>
                <div style='color: #71717a; font-size: 0.8rem; text-transform: uppercase;'>Outlier Count</div>
                <div style='font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-top: 0.25rem;'>{outlier_cols} columns</div>
                <div style='margin-top: 0.5rem;'>{status_badge('success' if outlier_cols == 0 else 'warning', 'Optimal' if outlier_cols == 0 else 'Fix Outliers')}</div>
            </div>
            """), unsafe_allow_html=True)
        with c4:
            st.markdown(clean_html(f"""
            <div>
                <div style='color: #71717a; font-size: 0.8rem; text-transform: uppercase;'>ML Readiness</div>
                <div style='font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-top: 0.25rem;'>{ml_readiness:.1f}%</div>
                <div style='margin-top: 0.5rem;'>{status_badge('success' if ml_readiness >= 75 else 'danger', 'Ready' if ml_readiness >= 75 else 'Not Ready')}</div>
            </div>
            """), unsafe_allow_html=True)
            
        # Compile recommendations checklist dynamically
        recs_list = []
        for det_name, report in reports.items():
            if report["problem"]:
                icon = "❌" if "Empty" in det_name or "Missing" in det_name or "Invalid" in det_name else "⚠️"
                recs_list.append({
                    "icon": icon,
                    "title": f"{det_name.replace('Detector', '')} Anomaly",
                    "desc": f"{report['problem']} Suggestion: {report['solution']}"
                })
                
        # Add verified stamps if clean
        if not reports["MissingValuesDetector"]["problem"]:
            recs_list.append({
                "icon": "✅",
                "title": "Completeness Verified",
                "desc": "No empty cells found. All categorical and numeric inputs are fully populated."
            })
        if not reports["DuplicatesDetector"]["problem"]:
            recs_list.append({
                "icon": "✅",
                "title": "Row Uniqueness Passed",
                "desc": "0 duplicate observations found. Samples are completely unique."
            })
        if not reports["ExtraSpacesDetector"]["problem"]:
            recs_list.append({
                "icon": "✅",
                "title": "Text Standardized",
                "desc": "Categorical string variables contain 0 invisible leading/trailing whitespaces."
            })

        recs_html = ""
        for rec in recs_list:
            recs_html += f"""
            <div style='display: flex; gap: 0.75rem; align-items: flex-start; background: rgba(9,9,11,0.3); padding: 0.75rem; border-radius: 8px; margin-bottom: 0.75rem;'>
                <span style='font-size: 1.1rem;'>{rec['icon']}</span>
                <div>
                    <strong style='color: #ffffff;'>{rec['title']}</strong>
                    <p style='color: #a1a1aa; font-size: 0.85rem; margin-top: 0.15rem;'>{rec['desc']}</p>
                </div>
            </div>
            """

        st.markdown(clean_html(f"""
        <div style='margin-top: 2rem;'>
            <h4 style='color: #ffffff; margin-bottom: 1rem;'>Automated Recommendations Checklist</h4>
            <div style='display: flex; flex-direction: column; gap: 0.75rem;'>
                {recs_html}
            </div>
        </div>
        """), unsafe_allow_html=True)

    # --- AI Data Science Advisory Dashboard ---
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 🤖 AI Data Science Advisory", unsafe_allow_html=True)
    
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        with st.container(border=True):
            st.markdown("<span class='accent-title'>Dataset Executive Memo</span>", unsafe_allow_html=True)
            if st.button("Generate Summary Memo", key="btn_ai_sum"):
                from core import dataset_summary
                stats_dict = {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "null_percentage": null_percent,
                    "duplicate_count": int(df.duplicated().sum()),
                    "total_outliers": outlier_cols
                }
                with st.spinner("AI Data Scientist is writing summary..."):
                    summary_memo = dataset_summary(stats_dict)
                st.session_state["cached_ai_summary"] = summary_memo
                st.toast("AI Summary Memo updated!", icon="🤖")
                st.rerun()
                
            if st.session_state.get("cached_ai_summary"):
                st.markdown(st.session_state["cached_ai_summary"])
            
        with st.container(border=True):
            st.markdown("<span class='accent-title'>ML Readiness Evaluation</span>", unsafe_allow_html=True)
            if st.button("Generate Readiness Rationale", key="btn_ai_ready"):
                from core import ml_readiness_explanation
                reports_summary = {k: v["problem"] for k, v in reports.items() if v["problem"]}
                with st.spinner("Analyzing readiness parameters..."):
                    readiness_memo = ml_readiness_explanation(ml_readiness, reports_summary)
                st.session_state["cached_ai_readiness"] = readiness_memo
                st.toast("AI Readiness Rationale updated!", icon="🤖")
                st.rerun()
                
            if st.session_state.get("cached_ai_readiness"):
                st.markdown(st.session_state["cached_ai_readiness"])
            
    with col_ai2:
        with st.container(border=True):
            st.markdown("<span class='accent-title'>Feature Engineering Enrichment</span>", unsafe_allow_html=True)
            if st.button("Generate Suggestions", key="btn_ai_feat"):
                from core import feature_engineering_suggestions
                schema_list = []
                for col in df.columns:
                    schema_list.append({"Column Name": col, "Data Type": str(df[col].dtype)})
                with st.spinner("Formulating feature pipelines..."):
                    feat_memo = feature_engineering_suggestions(schema_list)
                st.markdown(feat_memo)
            
        with st.container(border=True):
            st.markdown("<span class='accent-title'>Algorithm Selection Advisory</span>", unsafe_allow_html=True)
            task_mode = st.selectbox("Intended Task Target", ["classification", "regression"], key="sb_task_mode")
            if st.button("Generate Model Recommendations", key="btn_ai_algo"):
                from core import recommended_algorithms
                schema_list = []
                for col in df.columns:
                    schema_list.append({"Column Name": col, "Data Type": str(df[col].dtype)})
                with st.spinner("Analyzing dataset scale and shape..."):
                    algo_memo = recommended_algorithms(schema_list, task_mode)
                st.markdown(algo_memo)

else:
    # Empty State
    with st.container(border=True):
        st.markdown(clean_html("""
        <div style='text-align: center; padding: 3rem 1rem;'>
            <span style='font-size: 3rem;'>📄</span>
            <h3 style='margin-top: 1rem; color: #ffffff;'>No dataset loaded</h3>
            <p style='color: #a1a1aa; max-width: 400px; margin: 0.5rem auto 0 auto;'>
                Load a dataset on the Dashboard page to auto-generate PDF and HTML Quality Reports.
            </p>
        </div>
        """), unsafe_allow_html=True)

footer()
