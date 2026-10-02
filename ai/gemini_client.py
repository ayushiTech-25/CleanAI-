from core.llm import get_llm_provider
from ai.prompt_builder import SYSTEM_INSTRUCTION

class GeminiClient:
    """
    Interface for submitting prompts to the active Gemini Provider 
    and returning markdown-formatted responses.
    """
    
    def __init__(self):
        self.provider = get_llm_provider()
        
    def generate_response(self, prompt: str) -> str:
        if not self.provider:
            raise ValueError("No active LLM Provider configured. Please enter API keys in the Settings page.")
        return self.provider.generate(prompt, system_instruction=SYSTEM_INSTRUCTION)
