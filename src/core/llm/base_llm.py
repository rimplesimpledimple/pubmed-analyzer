from abc import ABC, abstractmethod
from typing import Dict, Type
from pydantic import BaseModel

class BaseLLM(ABC):
    """Base class for LLM implementations"""
        
    @abstractmethod
    def chat(self, prompt: str, response_model: Type[BaseModel]) -> BaseModel:
        """
        Send a chat message and get response.
        
        Args:
            prompt: The message to send
        """
        pass

    # hack for anthropic pdf support
    def chat_with_pdf(self, prompt: str, pdf_data: str, json_structure: Dict[str, str]) -> Dict[str, str]:
        """Chat with PDF support"""
        pass