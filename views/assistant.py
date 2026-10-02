import streamlit as st
import time
from utils.styling import init_page, clean_html
from components.ui import section_header, footer
from components.assistant_ui import render_chat_message, render_suggestion_chips
from core.session_state import initialize_session_state
from core import analyze_active_dataset, calculate_quality_scores

# Initialize style overlays
init_page("AI Assistant")

section_header("AI Data Co-Pilot", "Interact with our conversational model to diagnose dataset schemas, draft repair scripts, or perform quality audits.", "🤖")

initialize_session_state(st.session_state)

# If we have a dataset loaded, provide custom suggestion chips
has_data = st.session_state["dataset"] is not None
active_reports = analyze_active_dataset(st.session_state) if has_data else {}
active_health_score = calculate_quality_scores(st.session_state["dataset"], active_reports)[0] if has_data else None
suggestions = []
if has_data:
    suggestions = [
        "📊 Profile schema", 
        "💡 Suggest feature engineering ideas", 
        "📝 Generate Python cleaning script",
        "🎯 Predict target & preprocessing",
        "💾 Generate SQL ETL query",
        "📈 Generate EDA summary"
    ]
else:
    suggestions = ["💡 What can this assistant do?", "⚡ Load sample data first", "📜 Read safety guidelines"]

# Layout columns: Main chat area (left) and dataset info (right)
chat_col, info_col = st.columns([3, 1])

with chat_col:
    # Render historical messages in a native scrollable container
    with st.container(height=450):
        for msg in st.session_state["chat_messages"]:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["text"])
    
    # 2. Render Suggestion chips
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    selected_chip = render_suggestion_chips(suggestions)
    
    # Input field handling
    user_query = st.chat_input("Ask a question about your dataset...")
    
    # If a chip is clicked or text is entered
    query_to_send = user_query or selected_chip
    
    if query_to_send:
        # Avoid handling "Load sample data first" chip directly as chat if we want actions
        if query_to_send == "⚡ Load sample data first":
            st.toast("Go to the Dashboard page to load sample churn data!", icon="ℹ️")
        else:
            # Append User message
            st.session_state["chat_messages"].append({"role": "user", "text": query_to_send, "time": "Just Now"})
            
            # Re-run page to display user's message immediately
            st.rerun()

# Logic to compute AI response if user just asked something
if len(st.session_state["chat_messages"]) > 0 and st.session_state["chat_messages"][-1]["role"] == "user":
    user_query = st.session_state["chat_messages"][-1]["text"]
    
    # Spinner
    with st.spinner("AI Co-pilot is reading schema and compiling analysis..."):
        time.sleep(1.2)
        
        # Build intelligent responses based on context
        df = st.session_state["dataset"]
        
        if df is not None:
            from core import analyze_active_dataset, answer_dataset_questions
            reports = analyze_active_dataset(st.session_state)
            
            # Prepare statistical context dictionary
            null_cells = int(reports["MissingValuesDetector"]["statistics"]["total_null_count"])
            null_percent = float(reports["MissingValuesDetector"]["statistics"]["null_percentage"])
            duplicate_rows = int(reports["DuplicatesDetector"]["statistics"]["duplicate_count"])
            
            dataset_context = {
                "dataset_name": st.session_state["dataset_name"],
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns),
                "null_cells": null_cells,
                "null_percentage": null_percent,
                "duplicate_count": duplicate_rows,
                "numerical_columns": df.select_dtypes(include=['number']).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
                "quality_reports": {k: {"problem": v["problem"], "statistics": v["statistics"]} for k, v in reports.items()}
            }
            
            response = answer_dataset_questions(user_query, dataset_context)
        else:
            response = "No active dataset loaded. Please upload a file on the Dashboard or load sample data first."
            
        st.session_state["chat_messages"].append({"role": "assistant", "text": response, "time": "Just Now"})
        st.toast("AI Co-pilot completed reasoning!", icon="🤖")
        st.rerun()

with info_col:
    with st.container(border=True):
        st.markdown("<span class='accent-title'>Active Context</span>", unsafe_allow_html=True)
        if has_data:
            st.markdown(clean_html(f"""
            <div style='margin-top: 1rem;'>
                <div style='font-size: 0.8rem; color: #71717a;'>Active File</div>
                <div style='font-size: 0.95rem; font-weight: 600; color: #ffffff;'>{st.session_state['dataset_name']}</div>
                
                <div style='font-size: 0.8rem; color: #71717a; margin-top: 1rem;'>Quality Index</div>
                <div style='font-size: 1.2rem; font-weight: 700; color: #34d399;'>{active_health_score}%</div>
                
                <div style='font-size: 0.8rem; color: #71717a; margin-top: 1rem;'>Schema Status</div>
                <div style='font-size: 0.9rem; color: #fbbf24;'>⚠️ Anomalies detected</div>
            </div>
            """), unsafe_allow_html=True)
        else:
            st.markdown(clean_html("""
            <div style='margin-top: 1rem; color: #71717a; font-size: 0.9rem;'>
                No active dataset loaded in this session. Go to the Dashboard page to set up data context.
            </div>
            """), unsafe_allow_html=True)

footer()
