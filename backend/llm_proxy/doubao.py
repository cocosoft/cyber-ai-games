from .base_llm_proxy import BaseLLMProxy, LLMConfig
import os
from typing import Optional, Dict, Any

class DoubaoConfig(LLMConfig):
    base_url: str = "https://api.doubao.com/v1"
    default_model: str = "doubao-pro"

class DoubaoProxy(BaseLLMProxy):
    @classmethod
    def from_env(cls):
        """
        Create client from environment variables
        """
        return super().from_env("DOUBAO_API_KEY")

async def get_doubao_response(prompt: str, context: Optional[str] = None, model: Optional[str] = None) -> str:
    """
    Get response from Doubao model with optional context
    """
    client = DoubaoProxy.from_env()
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
            response = await get_doubao_response("Explain quantum computing in simple terms")
            print(response)
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())
