import json
from typing import Dict, Any, List

SYSTEM_INSTRUCTION = """
You are a Senior AI Data Scientist and Machine Learning Architect at CleanAI. You analyze datasets with absolute statistical precision.

Guidelines:
1. Explain like a Data Scientist. Use formal, professional data science terminology (e.g., variance, skewness, collinearity, imputation, estimators).
2. Never hallucinate. Stick strictly to the statistics, schemas, and counts provided in the prompt.
3. Always respond in markdown format. Use structured headings, bullet points, and code blocks where applicable.
4. Avoid conversational filler. Start directly with the analysis.
5. If the required information is not in the dataset context, clearly state that you do not have access to that information.
"""

def build_ai_prompt(user_question: str, context: Dict[str, Any], history: List[Dict[str, str]] = None) -> str:
    """
    Assembles the detailed context metadata, conversation history logs, 
    and the user query into a single prompt string for the Gemini provider.
    """
    history_str = ""
    if history:
        history_str = "\n".join([f"{msg['role'].upper()}: {msg['text']}" for msg in history[-5:]])
        
    prompt = f"""
    Active Dataset Context:
    {json.dumps(context, indent=2)}
    
    Conversation History:
    {history_str}
    
    Current User Question: "{user_question}"
    
    Formulate a mathematically sound answer utilizing the columns, null counts, outliers, and duplicates provided. Use the exact column names from the context. Do not invent facts.
    """
    return prompt
