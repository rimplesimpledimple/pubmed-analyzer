from abc import ABC, abstractmethod
from typing import Dict

class BaseLLM(ABC):
    """Base class for LLM implementations"""
        
    @abstractmethod
    def chat(self, prompt: str, json_structure: Dict[str, str], clear_history: bool = False) -> Dict[str, str]:
        """
        Send a chat message and get response.
        
        Args:
            prompt: The message to send
            clear_history: Whether to clear chat history before sending
        """
        pass
