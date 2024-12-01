import anthropic
from dataclasses import dataclass
from typing import Optional, List, Dict
import json
from .base_llm import BaseLLM
from ...utils.exceptions import InternalError

@dataclass
class ClaudeLLMConfig:
    """Configuration for Claude LLM"""
    api_key: str
    temperature: float = 0.3
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: Optional[int] = 1024

class ClaudeLLM(BaseLLM):
    """Claude LLM implementation"""
    
    def __init__(self, config: ClaudeLLMConfig):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.chat_history: List[Dict[str, str]] = []


    def chat(self, prompt: str, json_structure: Dict[str, str], clear_history: bool = False, max_retries: int = 3) -> Dict[str, str]:
        """Regular chat with retry logic for malformed JSON responses"""
        if clear_history:
            self.chat_history = []

        structured_prompt = f"""
        {prompt}

        Provide your response in JSON format matching exactly this structure:
        {json.dumps(json_structure, indent=2)}

        Your response must be valid JSON that can be parsed. Include only the JSON output.        
        """

        retries = 0
        while retries < max_retries:
            try:
                message = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=[{"role": "user", "content": structured_prompt}]
                )
                
                response = message.content[0].text
                self.chat_history.append({"role": "user", "content": structured_prompt})
                self.chat_history.append({"role": "assistant", "content": response})

                return json.loads(response)

            except json.JSONDecodeError as e:
                retries += 1
                if retries == max_retries:
                    raise InternalError(f"Failed to get valid JSON after {max_retries} attempts. Last error: {e}")
                
                # Add a retry prompt
                structured_prompt = f"""
                The previous response was not valid JSON. Please provide your response in valid JSON format matching exactly this structure:
                {json.dumps(json_structure, indent=2)}

                Include only the JSON output with no additional text.
                """
        
    def chat_with_pdf(self, prompt: str, pdf_data: str, json_structure: Dict[str, str]) -> Dict[str, str]:
        """Chat with PDF support"""
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
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return message.content[0].text 