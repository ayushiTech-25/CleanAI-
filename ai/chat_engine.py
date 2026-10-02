import pandas as pd
from typing import Dict, Any, List
from ai.dataset_context import build_dataset_context
from ai.prompt_builder import build_ai_prompt
from ai.gemini_client import GeminiClient
from core.ai import answer_dataset_questions

class ChatEngine:
    """
    Coordinates prompt construction, query execution, API exceptions handling, 
    local analytical fallbacks, and chat log exporting.
    """
    
    def __init__(self):
        self.client = GeminiClient()
        
    def get_response(self, user_question: str, df: pd.DataFrame, dataset_name: str, reports: Dict[str, Any], history: List[Dict[str, str]]) -> str:
        if df is None or df.empty:
            return "No active dataset loaded. Please upload a file on the Dashboard first."
            
        # Build context
        context = build_dataset_context(df, dataset_name, reports)
        
        # Build prompt
        prompt = build_ai_prompt(user_question, context, history)
        
        try:
            return self.client.generate_response(prompt)
        except Exception:
            # Fall back to localized context-aware reasoning
            return answer_dataset_questions(user_question, context)
            
    def export_chat_history(self, history: List[Dict[str, str]]) -> str:
        """Formats session chat logs into a downloadable Markdown file string."""
        md = "# CleanAI Co-pilot Chat Conversation Export\n\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "CleanAI Assistant"
            md += f"### {role}\n\n{msg['text']}\n\n---\n\n"
        return md
