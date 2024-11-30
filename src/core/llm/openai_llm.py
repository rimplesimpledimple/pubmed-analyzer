from typing import List, Dict
import openai
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class OpenAIConfig:
    """Configuration for OpenAI models"""
    model_name: str
    api_key: str
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    additional_params: Dict[str, Any] = None

class OpenAILLM:
    """Handles OpenAI API interactions with chat history management."""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client = openai.OpenAI(api_key=config.api_key)
        self.chat_history: List[Dict[str, str]] = []
    
    def chat(self, prompt: str, json_structure: Optional[Dict[str, str]] = None, clear_history: bool = False) -> str:
        """
        Send a chat message and get response.
        
        Args:
            prompt: The message to send
            json_structure: Example JSON structure that response should match
            clear_history: Whether to clear chat history before sending message
        """
        if clear_history:
            self.chat_history = []
            
        messages = self.chat_history + [{"role": "user", "content": prompt}]
        
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **self.config.additional_params or {}
        )
        
        response_content = response.choices[0].message.content
        
        self.chat_history.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response_content}
        ])
        
        return response_content 