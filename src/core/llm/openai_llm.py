import openai
from dataclasses import dataclass
from typing import Optional, Type
from pydantic import BaseModel
from .base_llm import BaseLLM

@dataclass
class OpenAILLMConfig:
    """Configuration for OpenAI LLM"""
    api_key: str
    temperature: float = 0.3
    model: str = "gpt-4o"
    max_tokens: Optional[int] = 4096

class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation"""
    
    def __init__(self, config: OpenAILLMConfig):
        self.config = config
        self.client = openai.OpenAI(api_key=config.api_key)

    def chat(self, prompt: str, response_model: Type[BaseModel]) -> BaseModel:
        """
        Chat with structured response using Pydantic models
        
        Args:
            prompt: The input prompt
            response_model: Pydantic model class defining the response structure
            
        Returns:
            Instance of the provided response_model
        """

        completion = self.client.beta.chat.completions.parse(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an expert at structured data extraction."},
                {"role": "user", "content": prompt}
            ],
            response_format=response_model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
                
        return completion.choices[0].message.parsed

                
    def chat_with_pdf(self, prompt: str, pdf_data: str, response_model: Type[BaseModel]) -> BaseModel:
        """Chat with PDF support"""
        pass