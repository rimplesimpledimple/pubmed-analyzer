from dataclasses import dataclass
from typing import Optional, Type,Dict
from langchain_anthropic import ChatAnthropic
import anthropic
from pydantic import BaseModel
import json

@dataclass
class ClaudeLLMConfig:
    """Configuration for Claude LLM"""
    api_key: str
    temperature: float = 0.3
    model: str = "claude-3-5-sonnet-latest" 
    max_tokens: Optional[int] = 2048
    max_retries: int = 2

class ClaudeLLM:
    """Claude LLM implementation using LangChain"""
    
    def __init__(self, config: ClaudeLLMConfig):
        self.config = config
        self.model = ChatAnthropic(
            api_key=config.api_key,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            max_retries=config.max_retries, 
        )        

        # for pdfs
        self.client = anthropic.Anthropic(api_key=config.api_key)

    def chat(self, prompt: str, response_model: Type[BaseModel]) -> BaseModel:
        """Regular chat with structured output"""
        structured_llm = self.model.with_structured_output(response_model)
        return structured_llm.invoke(prompt)

    def chat_with_pdf(self, prompt: str, pdf_data: str, json_structure: Dict[str, str]) -> Dict[str, str]:
        """Chat with PDF support"""

        structured_prompt = f"""
        {prompt}

        Provide your response in JSON format matching exactly this structure:
        {json.dumps(json_structure, indent=2)}

        Your response must be valid JSON that can be parsed. Include only the JSON output.        
        """

        message = self.client.beta.messages.create(
            model=self.config.model,
            betas=["pdfs-2024-09-25"],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_data
                            }
                        },
                        {
                            "type": "text",
                            "text": structured_prompt
                        }
                    ]
                }
            ]
        )
        return json.loads(message.content[0].text) 