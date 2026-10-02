import streamlit as st
import pandas as pd
import time
from utils.styling import init_page, clean_html
from components.ui import section_header, footer, status_badge
from core.dataset_lifecycle import invalidate_dataset_results, store_active_dataset
from core.cleaners import (
    MeanImputationCleaner,
    MedianImputationCleaner,
    KNNImputationCleaner,
    ModeImputationCleaner,
    DuplicateRemovalCleaner,
    IQROutlierCleaner,
    ZScoreOutlierCleaner,
    TextNormalizationCleaner
)

# Initialize page
init_page("Dataset Repairs")

section_header("Intelligent Cleaning Engine", "Configure and apply data cleaning strategies for missing values, outliers, and duplicates.", "🧹")

def render_pipeline_visualization(remove_dupes, impute_strategy, outlier_strategy, fix_casing):
    steps = [
        {"icon": "📁", "label": "Dataset Loaded", "active": True}
    ]
    if remove_dupes:
        steps.append({"icon": "👥", "label": "Duplicates Dropped", "active": True})
    else:
        steps.append({"icon": "👥", "label": "Duplicates Skipped", "active": False})
        
    if impute_strategy != "Do Nothing":
        steps.append({"icon": "⚠️", "label": f"Imputed ({impute_strategy})", "active": True})
    else:
        steps.append({"icon": "⚠️", "label": "Nulls Unchanged", "active": False})
        
    if outlier_strategy != "Keep Outliers":
        steps.append({"icon": "📈", "label": f"Outliers Bound ({outlier_strategy})", "active": True})
    else:
        steps.append({"icon": "📈", "label": "Outliers Kept", "active": False})
        
    if fix_casing:
        steps.append({"icon": "🔠", "label": "Text Normalized", "active": True})
    else:
        steps.append({"icon": "🔠", "label": "Text Untouched", "active": False})
        
    steps.append({"icon": "✨", "label": "Clean Output", "active": True})
    
    html = "<div style='display: flex; align-items: center; justify-content: space-between; overflow-x: auto; gap: 0.5rem; padding: 1rem 0;'>"
    for i, step in enumerate(steps):
        opacity = "1.0" if step["active"] else "0.35"
        border_color = "rgba(99, 102, 241, 0.6)" if step["active"] else "rgba(255,255,255,0.05)"
        bg_color = "rgba(99, 102, 241, 0.1)" if step["active"] else "rgba(24, 24, 27, 0.3)"
        
        html += f"""
        <div style='background: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 0.5rem 0.75rem; text-align: center; min-width: 110px; opacity: {opacity};'>
            <div style='font-size: 1.25rem;'>{step['icon']}</div>
            <div style='font-size: 0.7rem; font-weight: 600; color: #ffffff; margin-top: 0.25rem; white-space: nowrap;'>{step['label']}</div>
        </div>
        """
        if i < len(steps) - 1:
            html += "<span style='color: #71717a; font-weight: 700; font-size: 1.1rem;'>➔</span>"
            
    html += "</div>"
    return html

if st.session_state["dataset"] is not None:
    df = st.session_state["dataset"]
    orig_df = st.session_state["original_dataset"]
    
    col_ctrl, col_preview = st.columns([1, 2])
    
    with col_ctrl:
        with st.container(border=True):
            st.markdown("<span class='accent-title'>Repairs Pipeline</span>", unsafe_allow_html=True)
            
            # Section 1: Duplicates
            st.markdown("<h4 style='color: #ffffff; margin-top: 1rem;'>👥 Duplicates</h4>", unsafe_allow_html=True)
            remove_dupes = st.checkbox("Drop identical rows", value=True, help="Removes exact duplicate observations.")
            
            # Section 2: Missing Values
            st.markdown("<h4 style='color: #ffffff; margin-top: 1rem;'>⚠️ Missing Values</h4>", unsafe_allow_html=True)
            impute_strategy = st.selectbox(
                "Imputation Strategy", 
                ["Do Nothing", "Drop Missing Rows", "Mean Imputation", "Median Imputation", "Mode Imputation", "Advanced KNN"]
            )
            
            # Section 3: Outliers
            st.markdown("<h4 style='color: #ffffff; margin-top: 1rem;'>📈 Outliers Detection</h4>", unsafe_allow_html=True)
            outlier_strategy = st.selectbox(
                "Handling Method",
                ["Keep Outliers", "Clip at thresholds (IQR)", "Drop Rows with Outliers"]
            )
            iqr_threshold = st.slider("IQR Bound Threshold", 1.0, 3.0, 1.5, 0.1)
            
            # Section 4: Categoricals
            st.markdown("<h4 style='color: #ffffff; margin-top: 1rem;'>🔠 Standardizations</h4>", unsafe_allow_html=True)
            fix_casing = st.checkbox("Normalize categoricals casing", value=True, help="Converts strings to lowercase and trims whitespace.")
            st.session_state["cleaning_config"] = {
                "remove_duplicates": remove_dupes,
                "imputation_strategy": impute_strategy,
                "outlier_strategy": outlier_strategy,
                "iqr_threshold": iqr_threshold,
                "normalize_text": fix_casing,
            }
            
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            
            # Submit Button
            if st.button("Apply Cleaning Pipeline", use_container_width=True):
                with st.spinner("Executing Data Quality Pipeline..."):
                    time.sleep(1.5)
                    
                    cleaned_df = df.copy()
                    actions = []
                    
                    # 1. Duplicates
                    if remove_dupes:
                        cleaner = DuplicateRemovalCleaner()
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                        
                    # 2. Missing Values
                    if impute_strategy == "Mean Imputation":
                        cleaner = MeanImputationCleaner()
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                    elif impute_strategy == "Median Imputation":
                        cleaner = MedianImputationCleaner()
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                    elif impute_strategy == "Mode Imputation":
                        cleaner = ModeImputationCleaner()
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                    elif impute_strategy == "Advanced KNN":
                        cleaner = KNNImputationCleaner(n_neighbors=5)
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                    elif impute_strategy == "Drop Missing Rows":
                        before = len(cleaned_df)
                        cleaned_df = cleaned_df.dropna()
                        after = len(cleaned_df)
                        if before != after:
                            actions.append(f"Dropped {before - after} rows with missing cells")
                    
                    # 3. Outliers
                    if outlier_strategy == "Clip at thresholds (IQR)":
                        cleaner = IQROutlierCleaner(multiplier=iqr_threshold)
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                    elif outlier_strategy == "Drop Rows with Outliers":
                        cleaner = ZScoreOutlierCleaner(threshold=3.0)
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                        
                    # 4. Categoricals Normalization
                    if fix_casing:
                        cleaner = TextNormalizationCleaner()
                        cleaned_df, report = cleaner.clean(cleaned_df)
                        actions.extend(report["logs"])
                    
                    # Update Session State
                    if actions:
                        action_summary = "; ".join(actions)
                        store_active_dataset(
                            st.session_state,
                            cleaned_df,
                            action_summary,
                            before_df=df,
                        )
                        st.toast("Pipeline applied successfully using Backend Engine!", icon="✅")
                    else:
                        st.toast("No repair steps were selected or needed.", icon="ℹ️")
                    st.rerun()
        
    with col_preview:
        st.markdown("### Clean Preview Dashboard", unsafe_allow_html=True)
        st.markdown(clean_html(render_pipeline_visualization(remove_dupes, impute_strategy, outlier_strategy, fix_casing)), unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        
        # Undo / Redo controls row
        col_ur1, col_ur2, col_ur3 = st.columns([1, 1, 4])
        with col_ur1:
            undo_disabled = len(st.session_state.get("dataset_history_stack", [])) <= 1
            if st.button("⏪ Undo", disabled=undo_disabled, use_container_width=True, key="btn_undo"):
                # Pop current state from history stack and save it to redo stack
                curr_df, curr_action = st.session_state["dataset_history_stack"].pop()
                st.session_state["redo_stack"].append((st.session_state["dataset"].copy(), curr_action))
                
                # Restore previous state
                prev_df, prev_action = st.session_state["dataset_history_stack"][-1]
                st.session_state["dataset"] = prev_df.copy()
                invalidate_dataset_results(st.session_state)
                
                # Remove from visual logs
                if len(st.session_state["history"]) > 0:
                    st.session_state["history"].pop()
                    
                st.toast("Undid last repair operation!", icon="⏪")
                st.rerun()
                
        with col_ur2:
            redo_disabled = len(st.session_state.get("redo_stack", [])) == 0
            if st.button("Redo ⏩", disabled=redo_disabled, use_container_width=True, key="btn_redo"):
                # Pop from redo stack and restore it
                next_df, next_action = st.session_state["redo_stack"].pop()
                st.session_state["dataset_history_stack"].append((next_df.copy(), next_action))
                st.session_state["dataset"] = next_df.copy()
                invalidate_dataset_results(st.session_state)
                
                # Restore to visual logs
                st.session_state["history"].append({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "action": next_action,
                    "affected": "Redo Pipeline Run"
                })
                st.toast("Redid repair operation!", icon="⏩")
                st.rerun()
        
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        # Dashboard Tabs
        tab_curr, tab_orig, tab_history, tab_versions = st.tabs([
            "⚡ Cleaned/Current Dataset", 
            "📂 Original Dataset", 
            "📜 Pipeline History",
            "🏷 Version Timeline"
        ])
        
        with tab_curr:
            st.dataframe(df, use_container_width=True, height=450)
            
            # Show summary stats comparison
            st.markdown("#### Quality Metrics Delta", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Rows", len(df), delta=len(df) - len(orig_df))
            with c2:
                missing_now = int(df.isnull().sum().sum())
                missing_then = int(orig_df.isnull().sum().sum())
                st.metric("Missing Count", missing_now, delta=int(missing_now - missing_then), delta_color="inverse")
            with c3:
                dupes_now = int(df.duplicated().sum())
                dupes_then = int(orig_df.duplicated().sum())
                st.metric("Duplicates", dupes_now, delta=int(dupes_now - dupes_then), delta_color="inverse")
                
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            
            # AI Repair Explainer Accordion
            with st.expander("🤖 AI Co-Pilot: Explain mathematical impact of repairs"):
                if len(st.session_state["history"]) > 0:
                    if st.button("Generate Rationale Memo", key="btn_explain_repairs"):
                        from core import explain_cleaning_steps
                        
                        # Compute current statistics context
                        null_cells = df.isnull().sum().sum()
                        null_percent = (null_cells / (len(df) * len(df.columns))) * 100 if len(df) > 0 and len(df.columns) > 0 else 0
                        stats_ctx = {
                            "rows": len(df),
                            "columns": len(df.columns),
                            "null_cells": int(null_cells),
                            "null_percentage": float(null_percent),
                            "duplicate_rows": int(df.duplicated().sum())
                        }
                        
                        with st.spinner("AI is analyzing history..."):
                            memo = explain_cleaning_steps(st.session_state["history"], stats_ctx)
                        st.markdown(memo)
                else:
                    st.info("Apply at least one repair step to analyze historical impact.")
                
        with tab_orig:
            st.dataframe(orig_df, use_container_width=True, height=450)
            
        with tab_history:
            if len(st.session_state["history"]) > 0:
                for idx, log in enumerate(reversed(st.session_state["history"])):
                    st.markdown(clean_html(f"""
                    <div style='background: rgba(24, 24, 27, 0.4); padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem; border-left: 3px solid #6366f1;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong style='color: #ffffff;'>{log['action']}</strong>
                            <span style='color: #71717a; font-size: 0.85rem;'>{log['timestamp']}</span>
                        </div>
                        <div style='color: #a1a1aa; font-size: 0.85rem; margin-top: 0.25rem;'>Affected: {log['affected']}</div>
                    </div>
                    """), unsafe_allow_html=True)
            else:
                st.info("No cleaning pipelines have been run on this dataset yet.")
                
        with tab_versions:
            st.markdown("#### Dataset Version Timeline")
            history_stack = st.session_state.get("dataset_history_stack", [])
            for idx, (df_state, action) in enumerate(history_stack):
                v_name = f"v{idx + 1}"
                badge_type = "success" if idx == len(history_stack) - 1 else "info"
                badge_lbl = "Current Active" if idx == len(history_stack) - 1 else "Archived State"
                st.markdown(clean_html(f"""
                <div style='background: rgba(24, 24, 27, 0.4); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong style='color: #ffffff;'>Version {v_name}</strong>
                        <span style='color: #a1a1aa; font-size: 0.85rem; margin-left: 0.5rem;'>({action})</span>
                        <div style='color: #71717a; font-size: 0.8rem; margin-top: 0.15rem;'>Observations: {len(df_state)}  |  Features: {len(df_state.columns)}</div>
                    </div>
                    <div>
                        {status_badge(badge_type, badge_lbl)}
                    </div>
                </div>
                """), unsafe_allow_html=True)
                
else:
    # Empty State
    with st.container(border=True):
        st.markdown(clean_html("""
        <div style='text-align: center; padding: 3rem 1rem;'>
            <span style='font-size: 3rem;'>📥</span>
            <h3 style='margin-top: 1rem; color: #ffffff;'>No dataset loaded</h3>
            <p style='color: #a1a1aa; max-width: 400px; margin: 0.5rem auto 0 auto;'>
                Load data on the Dashboard page to unlock the Cleaning Engine pipeline configurations.
            </p>
        </div>
        """), unsafe_allow_html=True)

footer()
