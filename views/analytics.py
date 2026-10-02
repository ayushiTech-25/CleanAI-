import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.styling import init_page, clean_html
from components.ui import section_header, footer
from core import cached_run_all_detections
from core.dataset_lifecycle import analyze_active_dataset

# Initialize page styling
init_page("Dataset Analytics")

def detect_target_column(df):
    target_keywords = ["target", "label", "class", "churn", "status", "outcome", "y", "clicked", "purchased"]
    for col in df.columns:
        if col.lower() in target_keywords:
            return col
    for col in df.columns:
        for kw in target_keywords:
            if kw in col.lower():
                return col
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        cardinalities = {col: df[col].nunique() for col in cat_cols if df[col].nunique() > 1}
        if cardinalities:
            return min(cardinalities, key=cardinalities.get)
    return df.columns[-1]

def detect_data_drift(orig_df, current_df):
    num_cols = orig_df.select_dtypes(include=["number"]).columns.tolist()
    drift_report = []
    for col in num_cols:
        if col in current_df.columns:
            o_mean = orig_df[col].mean()
            c_mean = current_df[col].mean()
            if pd.isna(o_mean) or pd.isna(c_mean) or o_mean == 0:
                mean_shift = 0
            else:
                mean_shift = abs(c_mean - o_mean) / abs(o_mean)
            drift_detected = mean_shift > 0.05
            drift_report.append({
                "Column": col,
                "Original Mean": f"{o_mean:.2f}",
                "Cleaned Mean": f"{c_mean:.2f}",
                "Shift Score": f"{mean_shift:.2%}",
                "Status": "⚠️ Shifted" if drift_detected else "✅ Stable"
            })
    return pd.DataFrame(drift_report)

def calculate_column_quality_ranking(df, reports):
    ranking = []
    total_rows = len(df)
    outliers_stat = reports.get("OutliersDetector", {}).get("statistics", {}).get("outliers_by_column", {})
    for col in df.columns:
        nulls = df[col].isnull().sum()
        null_rate = nulls / total_rows if total_rows > 0 else 0
        outliers_count = outliers_stat.get(col, {}).get("count", 0) if isinstance(outliers_stat, dict) else 0
        outlier_rate = outliers_count / total_rows if total_rows > 0 else 0
        score = 100 - (null_rate * 70 + outlier_rate * 30)
        score = max(0, min(100, int(score)))
        ranking.append({
            "Column Name": col,
            "Quality Score": f"{score}%",
            "_Quality Score Numeric": score,
            "Missing Ratio": f"{null_rate:.1%}",
            "Outliers Count": outliers_count,
            "Grade": "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 50 else "F"
        })
    return pd.DataFrame(ranking).sort_values(by="_Quality Score Numeric", ascending=False).drop(columns=["_Quality Score Numeric"])

def plot_feature_importance(df, target_col):
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if target_col in num_cols and len(num_cols) > 1:
        corrs = df[num_cols].corr()[target_col].abs().drop(target_col).reset_index()
        corrs.columns = ["Feature", "Importance Score"]
        corrs = corrs.sort_values(by="Importance Score", ascending=True)
        fig = px.bar(
            corrs, 
            y="Feature", 
            x="Importance Score", 
            orientation="h",
            title=f"Feature Correlation Strength with Target '{target_col}'",
            color="Importance Score",
            color_continuous_scale="Purples",
            template="plotly_dark"
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
        return fig
    return None

section_header("Advanced Data Quality Analytics", "Interactive Plotly profiling metrics, feature correlations, category balances, and cleaning deltas.", "📈")

if st.session_state["dataset"] is not None:
    df = st.session_state["dataset"]
    orig_df = st.session_state["original_dataset"]
    
    # --- Sidebar Filter Engine ---
    st.sidebar.markdown("### 🎛 Dataset Filters")
    st.sidebar.markdown("Charts will update in real-time based on filter criteria below.")
    
    # Filter 1: Row sampler
    total_len = len(df)
    if total_len == 0:
        st.warning("The active dataset has no rows to analyze. Load or restore a dataset first.")
        st.stop()
    sample_size = st.sidebar.slider("Observations limit to plot", 1, total_len, min(total_len, 500))
    df_filtered = df.iloc[:sample_size].copy()
    
    # Filter 2: Numerical range selectors
    num_cols = df_filtered.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df_filtered.select_dtypes(include=["object", "category"]).columns.tolist()
    
    if num_cols:
        st.sidebar.markdown("#### Numerical Limits")
        filter_col = st.sidebar.selectbox("Select feature to clip filter", ["None"] + num_cols)
        if filter_col != "None":
            min_val = float(df_filtered[filter_col].min())
            max_val = float(df_filtered[filter_col].max())
            if not pd.isna(min_val) and not pd.isna(max_val) and min_val != max_val:
                val_range = st.sidebar.slider(f"Filter range of '{filter_col}'", min_val, max_val, (min_val, max_val))
                df_filtered = df_filtered[(df_filtered[filter_col] >= val_range[0]) & (df_filtered[filter_col] <= val_range[1])]

    if df_filtered.empty:
        st.warning("The selected filters return no rows. Broaden the filters to continue analysis.")
        st.stop()

    # --- Live Quality Gauges ---
    # Keep the canonical analysis tied to the active dataset; chart filters remain local.
    analyze_active_dataset(st.session_state)
    reports = cached_run_all_detections(df_filtered)
    
    null_percent = float(reports["MissingValuesDetector"]["statistics"]["null_percentage"])
    duplicate_percent = float(reports["DuplicatesDetector"]["statistics"]["duplicate_percentage"])
    outlier_cols = len(reports["OutliersDetector"]["statistics"]["outliers_by_column"])
    wrong_type_cols = len(reports["DataTypeDetector"]["statistics"]["columns_to_cast"])
    const_cols = len(reports["ConstantColumnsDetector"]["statistics"]["constant_columns"])
    empty_cols = len(reports["EmptyColumnsDetector"]["statistics"]["empty_columns"])
    card_cols = len(reports["HighCardinalityDetector"]["statistics"]["high_cardinality_columns"])
    mixed_cols = len(reports["MixedTextDetector"]["statistics"]["mixed_columns"])
    space_cols = len(reports["ExtraSpacesDetector"]["statistics"]["space_anomalies"])
    date_cols = len(reports["InvalidDateDetector"]["statistics"]["invalid_date_columns"])
    
    health_score = 100.0
    health_score -= (null_percent * 1.2 + duplicate_percent * 1.0 + outlier_cols * 4.0 + wrong_type_cols * 5.0 + const_cols * 10.0 + empty_cols * 15.0 + card_cols * 4.0 + mixed_cols * 4.0 + space_cols * 2.0 + date_cols * 8.0)
    health_score = max(0, min(100, int(health_score)))
    
    ml_readiness = 100.0
    ml_readiness -= (null_percent * 2.2 + duplicate_percent * 0.5 + outlier_cols * 8.0 + wrong_type_cols * 6.0 + const_cols * 12.0 + empty_cols * 20.0 + card_cols * 5.0 + mixed_cols * 4.0 + space_cols * 1.0 + date_cols * 10.0)
    ml_readiness = max(0, min(100, int(ml_readiness)))

    col_gauge1, col_gauge2 = st.columns(2)
    
    with col_gauge1:
        fig_g1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            title={'text': "Dataset Quality Health Index"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#71717a"},
                'bar': {'color': "#6366f1"},
                'bgcolor': "rgba(24,24,27,0.4)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.05)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.15)'}
                ]
            }
        ))
        fig_g1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            font_color="#ffffff",
            height=220,
            margin=dict(l=30, r=30, t=50, b=20)
        )
        st.plotly_chart(fig_g1, use_container_width=True)
        
    with col_gauge2:
        fig_g2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ml_readiness,
            title={'text': "ML Estimator Readiness Score"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#71717a"},
                'bar': {'color': "#c084fc"},
                'bgcolor': "rgba(24,24,27,0.4)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.05)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.15)'}
                ]
            }
        ))
        fig_g2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            font_color="#ffffff",
            height=220,
            margin=dict(l=30, r=30, t=50, b=20)
        )
        st.plotly_chart(fig_g2, use_container_width=True)

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    st.info("💡 **Export Tip:** Hover over any chart's top-right corner and click the 📷 Camera icon to export the chart instantly as a high-resolution PNG.")

    # --- Dashboard Tabs ---
    tab_nulls, tab_uni, tab_cat, tab_bi, tab_comp, tab_dupes, tab_drift = st.tabs([
        "⚠️ Completeness Matrix", 
        "📊 Numerical Profiles", 
        "🍩 Categorical Profiles", 
        "🔗 Bivariate Correlations", 
        "🔄 Before vs After Repairs",
        "👥 Duplicate Explorer",
        "📡 Drift & Quality Leaderboard"
    ])
    
    # 1. Tab: Completeness Matrix
    with tab_nulls:
        st.markdown("### Missing Values Density Matrix")
        # Build binary matrix: 1 = Missing, 0 = Present
        null_matrix = df_filtered.isnull().astype(int)
        
        fig_matrix = px.imshow(
            null_matrix,
            labels=dict(x="Feature Column", y="Observation Row", color="Status"),
            color_continuous_scale=[[0, "#18181b"], [1, "#f87171"]],
            title="Interactive Null Matrix Heatmap (Red denotes empty cell)",
            template="plotly_dark"
        )
        fig_matrix.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        
    # 2. Tab: Numerical Profiles
    with tab_uni:
        st.markdown("### Numerical Column Distributions")
        if num_cols:
            sel_num = st.selectbox("Select numerical column to graph", num_cols, key="sb_sel_num")
            chart_type_num = st.selectbox("Select distribution chart type", ["Histogram & Boxplot (Side-by-Side)", "Violin Plot", "Density Distribution Plot"], key="sb_chart_type_num")
            
            if chart_type_num == "Histogram & Boxplot (Side-by-Side)":
                c_uni1, c_uni2 = st.columns(2)
                with c_uni1:
                    fig_hist = px.histogram(
                        df_filtered, 
                        x=sel_num, 
                        title=f"Histogram of '{sel_num}'", 
                        color_discrete_sequence=["#6366f1"],
                        template="plotly_dark",
                        marginal="rug"
                    )
                    fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                    st.plotly_chart(fig_hist, use_container_width=True)
                    
                with c_uni2:
                    fig_box = px.box(
                        df_filtered, 
                        y=sel_num, 
                        title=f"Boxplot of '{sel_num}' (Outliers check)",
                        color_discrete_sequence=["#c084fc"],
                        template="plotly_dark"
                    )
                    fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                    st.plotly_chart(fig_box, use_container_width=True)
            elif chart_type_num == "Violin Plot":
                fig_violin = px.violin(
                    df_filtered,
                    y=sel_num,
                    box=True,
                    points="all",
                    title=f"Violin Plot of '{sel_num}'",
                    color_discrete_sequence=["#c084fc"],
                    template="plotly_dark"
                )
                fig_violin.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                st.plotly_chart(fig_violin, use_container_width=True)
            else:
                fig_dist = px.histogram(
                    df_filtered,
                    x=sel_num,
                    color_discrete_sequence=["#818cf8"],
                    histnorm="probability density",
                    template="plotly_dark",
                    cumulative=False
                )
                fig_dist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.warning("No numerical features available.")
            
    # 3. Tab: Categorical Profiles
    with tab_cat:
        st.markdown("### Categorical Class Proportions")
        if cat_cols:
            sel_cat = st.selectbox("Select categorical column to graph", cat_cols, key="sb_sel_cat")
            chart_type_cat = st.selectbox("Select category chart type", ["Bar & Pie (Side-by-Side)", "Treemap", "Sunburst Chart"], key="sb_chart_type_cat")
            
            counts = df_filtered[sel_cat].value_counts(dropna=False).reset_index()
            counts.columns = ["Category", "Count"]
            
            if chart_type_cat == "Bar & Pie (Side-by-Side)":
                c_cat1, c_cat2 = st.columns(2)
                with c_cat1:
                    fig_bar = px.bar(
                        counts, 
                        x="Category", 
                        y="Count", 
                        title=f"Category Frequencies for '{sel_cat}'",
                        color_discrete_sequence=["#818cf8"],
                        template="plotly_dark"
                    )
                    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                with c_cat2:
                    fig_pie = px.pie(
                        counts, 
                        names="Category", 
                        values="Count", 
                        hole=0.4,
                        title=f"Category Balances for '{sel_cat}'",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        template="plotly_dark"
                    )
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                    st.plotly_chart(fig_pie, use_container_width=True)
            elif chart_type_cat == "Treemap":
                fig_tree = px.treemap(
                    counts,
                    path=["Category"],
                    values="Count",
                    title=f"Treemap Class Proportions: '{sel_cat}'",
                    color="Count",
                    color_continuous_scale="Purples",
                    template="plotly_dark"
                )
                fig_tree.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                st.plotly_chart(fig_tree, use_container_width=True)
            else:
                fig_sun = px.sunburst(
                    counts,
                    path=["Category"],
                    values="Count",
                    title=f"Sunburst Proportions: '{sel_cat}'",
                    color="Count",
                    color_continuous_scale="Purples",
                    template="plotly_dark"
                )
                fig_sun.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.warning("No categorical features available.")
            
    # 4. Tab: Bivariate Relationships & Correlations
    with tab_bi:
        st.markdown("### Feature Interactions")
        if len(num_cols) >= 2:
            sel_x = st.selectbox("Select X axis variable", num_cols, index=0)
            sel_y = st.selectbox("Select Y axis variable", num_cols, index=min(1, len(num_cols)-1))
            
            col_sc, col_corr = st.columns(2)
            
            with col_sc:
                # Scatter Plot
                fig_scatter = px.scatter(
                    df_filtered, 
                    x=sel_x, 
                    y=sel_y, 
                    title=f"Scatter: {sel_x} vs {sel_y}",
                    color_discrete_sequence=["#c084fc"],
                    template="plotly_dark"
                )
                fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            with col_corr:
                # Correlation Heatmap
                corr_df = df_filtered[num_cols].corr()
                fig_heat = px.imshow(
                    corr_df,
                    text_auto=".2f",
                    color_continuous_scale="RdBu",
                    zmin=-1, zmax=1,
                    title="Pearson Correlation Heatmap",
                    template="plotly_dark"
                )
                fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Inter")
                st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.warning("Needs at least 2 numerical columns to plot interaction heatmaps.")
            
    # 5. Tab: Before vs After Repaired Comparison
    with tab_comp:
        st.markdown("### Overlaid Repaired Distributions Comparison")
        if num_cols:
            sel_comp = st.selectbox("Select numeric feature to compare deltas", num_cols, key="sb_sel_comp")
            
            fig_comp = go.Figure()
            # Original distribution
            fig_comp.add_trace(go.Histogram(
                x=orig_df[sel_comp],
                name="Original (Before Cleaning)",
                marker_color="rgba(99, 102, 241, 0.4)",
                nbinsx=30
            ))
            # Current cleaned distribution
            fig_comp.add_trace(go.Histogram(
                x=df_filtered[sel_comp],
                name="Cleaned/Current (After Cleaning)",
                marker_color="rgba(192, 132, 252, 0.5)",
                nbinsx=30
            ))
            fig_comp.update_layout(
                barmode="overlay",
                title=f"Distribution Overlap Comparison: '{sel_comp}'",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Inter"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Print statistical deltas
            st.markdown("#### Statistical Shift Summary")
            delta_col1, delta_col2 = st.columns(2)
            with delta_col1:
                st.markdown(f"""
                **Original `{sel_comp}` Stats:**
                - Mean: `{orig_df[sel_comp].mean():.2f}`
                - Standard Deviation: `{orig_df[sel_comp].std():.2f}`
                - Null Cells: `{orig_df[sel_comp].isnull().sum()}`
                """)
            with delta_col2:
                st.markdown(f"""
                **Cleaned `{sel_comp}` Stats:**
                - Mean: `{df_filtered[sel_comp].mean():.2f}`
                - Standard Deviation: `{df_filtered[sel_comp].std():.2f}`
                - Null Cells: `{df_filtered[sel_comp].isnull().sum()}`
                """)
        else:
            st.warning("No numerical features available.")

    # 6. Tab: Duplicate Row Explorer
    with tab_dupes:
        st.markdown("### Duplicate Row Explorer")
        dupe_df = df_filtered[df_filtered.duplicated(keep=False)]
        if len(dupe_df) > 0:
            st.warning(f"Found {len(dupe_df)} duplicated row observations inside the filtered subset.")
            st.dataframe(dupe_df, use_container_width=True)
        else:
            st.success("🎉 No duplicate row observations exist in the active dataset subset!")
            
    # 7. Tab: Drift & Quality Leaderboard
    with tab_drift:
        st.markdown("### Feature Quality Ranking Leaderboard")
        rank_df = calculate_column_quality_ranking(df_filtered, reports)
        st.table(rank_df)
        
        st.markdown("### Data Drift Analysis (Cleaned vs Original)")
        drift_df = detect_data_drift(orig_df, df_filtered)
        if not drift_df.empty:
            st.table(drift_df)
        else:
            st.info("No numeric columns available to measure drift shifts.")
            
        st.markdown("### AI Feature Importance Matrix")
        target_col = detect_target_column(df_filtered)
        st.info(f"🎯 **Auto-Detected Target Feature**: `{target_col}` (Used as modeling label context)")
        fig_importance = plot_feature_importance(df_filtered, target_col)
        if fig_importance is not None:
            st.plotly_chart(fig_importance, use_container_width=True)
        else:
            st.info("Feature importance requires a numeric target and at least one numeric feature; no proxy values are shown.")

else:
    # Empty State
    with st.container(border=True):
        st.markdown(clean_html("""
        <div style='text-align: center; padding: 3rem 1rem;'>
            <span style='font-size: 3rem;'>📊</span>
            <h3 style='margin-top: 1rem; color: #ffffff;'>No dataset loaded</h3>
            <p style='color: #a1a1aa; max-width: 400px; margin: 0.5rem auto 0 auto;'>
                Load a dataset on the Dashboard page to unlock the Plotly Interactive Analytics dashboard.
            </p>
        </div>
        """), unsafe_allow_html=True)

footer()
