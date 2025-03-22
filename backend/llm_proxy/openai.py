import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.llm_proxy.base_llm_proxy import BaseLLMProxy, LLMConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OpenAIConfig:
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 5  # requests per second
    default_model: str = "gpt-4"

class OpenAIProxy(BaseLLMProxy):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        self.semaphore = asyncio.Semaphore(5)  # Default rate limit

    async def close(self):
        await self.session.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def chat_completion(self, messages: list, model: Optional[str] = None, temperature: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        Get chat completion from OpenAI model
        """
        model = model or self.config.default_model
        url = f"{self.config.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000
        }

        async with self.semaphore:
            try:
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"API request failed: {str(e)}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response: {str(e)}")
                raise

    @classmethod
    def from_config(cls, config: OpenAIConfig):
        """
        Create proxy from config
        """
        return cls(LLMConfig(
            api_key=config.api_key,
            base_url=config.base_url,
            default_model=config.default_model,
            max_retries=config.max_retries,
            timeout=config.timeout
        ))

async def get_openai_response(prompt: str, context: Optional[str] = None, model: Optional[str] = None) -> str:
    """
    Get response from OpenAI model with optional context
    """
    client = OpenAIClient.from_env()
    try:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat_completion(messages, model=model)
        return response['choices'][0]['message']['content']
    finally:
        await client.close()

# Example usage
if __name__ == "__main__":
    async def main():
        try:
            response = await get_openai_response("Explain quantum computing in simple terms")
            print(response)
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())
