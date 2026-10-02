import streamlit as st
import pandas as pd
import numpy as np
import time
from utils.styling import init_page, clean_html
from components.ui import section_header, footer
from components.chat_ui import render_chat_ui
from components.suggestion_chips import render_suggestion_chips
from components.ai_cards import render_ai_insights_panel
from ai.chat_engine import ChatEngine
from ai.dataset_context import build_dataset_context
from core import analyze_active_dataset
from core.dataset_lifecycle import store_loaded_dataset

# Initialize page overlay
init_page("AI Assistant")

section_header("AI Dataset Assistant", "Discuss, script, and profile your dataset with our context-aware ML Co-pilot.", "🤖")

# Help helper to generate our mock dataset (matching dashboard for workspace actions)
def generate_mock_data():
    np.random.seed(42)
    rows = 150
    data = {
        "customer_id": [f"USR-{1000+i}" for i in range(rows)],
        "age": np.random.choice([25, 34, 45, np.nan, 29, 62, 108, 12, 38, 55], size=rows),
        "monthly_charges": np.random.choice([29.99, 79.99, 89.99, np.nan, 120.0, -45.0], size=rows),
        "tenure_months": np.random.choice([3, 12, 24, np.nan, 36, 72, 5], size=rows),
        "churn": np.random.choice(["Yes", "No", "yes", "NO", None], size=rows),
        "signup_date": pd.date_range(start="2024-01-01", periods=rows).strftime("%Y-%m-%d")
    }
    df = pd.DataFrame(data)
    df = pd.concat([df, df.iloc[[12, 45, 87]]], ignore_index=True)
    return df

# Main logic
if st.session_state["dataset"] is not None:
    df = st.session_state["dataset"]
    dataset_name = st.session_state["dataset_name"]
    
    # Calculate detections and context once
    reports = analyze_active_dataset(st.session_state)
    context = build_dataset_context(df, dataset_name, reports)
    
    # Layout columns: Main chat area (left) and dataset info (right)
    chat_col, info_col = st.columns([3, 1])
    
    with chat_col:
        # Top utilities row: Clear & Export
        col_ut1, col_ut2, col_ut3 = st.columns([2, 2, 8])
        with col_ut1:
            if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_assistant_chat"):
                st.session_state["chat_messages"] = [
                    {"role": "assistant", "text": "Conversation cleared. How can I assist you with your data quality profile today?", "time": "Just Now"}
                ]
                st.rerun()
        with col_ut2:
            chat_eng = ChatEngine()
            chat_md = chat_eng.export_chat_history(st.session_state["chat_messages"])
            st.download_button(
                "📥 Export Chat",
                data=chat_md,
                file_name="cleanai_chat_log.md",
                mime="text/markdown",
                use_container_width=True,
                key="btn_export_chat"
            )
            
        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # 1. Render historical chat container
        render_chat_ui(st.session_state["chat_messages"], container_height=420)
        
        # 2. Render Suggestion Chips
        st.markdown("##### Quick Suggestions")
        sug_list = [
            "📈 Generate EDA summary", 
            "⚠️ Explain Missing Values", 
            "🤖 Recommend ML Algorithms", 
            "💡 Suggest feature engineering ideas", 
            "📝 Generate Python cleaning script",
            "🎯 Predict target & preprocessing"
        ]
        selected_sug = render_suggestion_chips(sug_list, key_prefix="assistant_sug")
        
        # 3. Render Quick Actions Grid
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("##### Quick Actions")
        qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)
        selected_action_query = None
        with qa_col1:
            if st.button("📊 Summary", use_container_width=True, key="qa_sum"):
                selected_action_query = "Generate EDA statistical summary of the dataset."
        with qa_col2:
            if st.button("💡 Preprocessing", use_container_width=True, key="qa_prep"):
                selected_action_query = "Suggest preprocessing and target column strategies."
        with qa_col3:
            if st.button("📝 Pandas Script", use_container_width=True, key="qa_pandas"):
                selected_action_query = "Generate a Python/Pandas cleaning script for this dataset."
        with qa_col4:
            if st.button("💾 SQL Query", use_container_width=True, key="qa_sql"):
                selected_action_query = "Generate a SQL ETL query to load this dataset staging table."
                
        # Sticky Input Chat box
        user_query = st.chat_input("Ask a question about your dataset...")
        
        # Resolve active query input
        active_query = user_query or selected_sug or selected_action_query
        
        if active_query:
            # Save user query
            st.session_state["chat_messages"].append({"role": "user", "text": active_query, "time": "Just Now"})
            
            # Send message and get response
            chat_eng = ChatEngine()
            with st.spinner("AI Co-pilot is reading schema and compiling analysis..."):
                response = chat_eng.get_response(
                    active_query,
                    df,
                    dataset_name,
                    reports,
                    st.session_state["chat_messages"][:-1]
                )
            # Append AI response
            st.session_state["chat_messages"].append({"role": "assistant", "text": response, "time": "Just Now"})
            st.toast("AI Co-pilot finished reasoning!", icon="🤖")
            st.rerun()
            
    with info_col:
        # Render Insights panel cards
        render_ai_insights_panel(context)

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
            if st.button("Resume Project ➔", key="resume_churn_assistant", use_container_width=True):
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
            if st.button("Load Leads Dataset ➔", key="resume_leads_assistant", use_container_width=True):
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
            if st.button("Load Boston Dataset ➔", key="resume_boston_assistant", use_container_width=True):
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

footer()
