import os
import requests
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load env values
load_dotenv()

class BaseLLMProvider(ABC):
    """
    Abstract LLM Interface.
    Enables future substitution of providers (Dependency Inversion).
    """
    
    @abstractmethod
    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        Submits prompt to target LLM endpoint.
        
        Args:
            prompt (str): Text prompt payload.
            system_instruction (str): Custom system guidelines instructions.
            
        Returns:
            str: Markdown formatted response text.
        """
        pass

class GeminiProvider(BaseLLMProvider):
    """Concrete provider linking to Google Gemini API via REST HTTP."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = "gemini-1.5-flash"
        
    def generate(self, prompt: str, system_instruction: str = None) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in environment settings.")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Build contents payload
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        
        # Include system instructions if provided
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code != 200:
                raise RuntimeError(f"Gemini API returned error code {response.status_code}: {response.text}")
                
            res_json = response.json()
            # Parse standard candidates text response path
            text_out = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return text_out.strip()
            
        except Exception as e:
            raise RuntimeError(f"Failed calling Gemini API endpoint: {str(e)}")

class OpenAIProvider(BaseLLMProvider):
    """OpenAI Chat Completions provider using the standard HTTPS API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
    def generate(self, prompt: str, system_instruction: str = None) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": "gpt-4o-mini", "messages": messages, "temperature": 0.2},
                timeout=15,
            )
            if response.status_code != 200:
                raise RuntimeError(f"OpenAI API returned error code {response.status_code}: {response.text}")
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            raise RuntimeError(f"Failed calling OpenAI API endpoint: {exc}") from exc

def get_llm_provider() -> BaseLLMProvider:
    """
    Factory resolver resolving the active LLM Provider based on environmental keys.
    Prefers Gemini first.
    """
    session_keys = {}
    try:
        import streamlit as st
        session_keys = st.session_state.get("settings_api_keys", {})
    except (ImportError, RuntimeError):
        pass

    gemini_key = os.getenv("GEMINI_API_KEY") or session_keys.get("GEMINI_API_KEY")
    if gemini_key and len(gemini_key.strip()) > 0:
        return GeminiProvider(gemini_key)
        
    openai_key = os.getenv("OPENAI_API_KEY") or session_keys.get("OPENAI_API_KEY")
    if openai_key and len(openai_key.strip()) > 0:
        return OpenAIProvider(openai_key)
        
    return None
