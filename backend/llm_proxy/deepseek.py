import os
from typing import Optional, Dict, Any, AsyncGenerator, Type, Union, List
from pydantic import BaseModel, validator
from backend.llm_proxy.base_llm_proxy import BaseLLMProxy, LLMConfig, ModelType, PluginConfig
import json
import logging
import aiohttp
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DeepSeekConfig(BaseModel):
    """DeepSeek 配置模型"""
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    default_model: str = "deepseek-chat"
    max_retries: int = 3
    timeout: int = 30
    temperature: float = 0.7
    max_tokens: int = 1000
    plugins: List[str] = []

    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("Invalid API key")
        return v

class DeepSeekError(Exception):
    """Base exception for DeepSeek API errors"""
    pass

class DeepSeekProxy(BaseLLMProxy):
    """DeepSeek platform implementation"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize DeepSeek proxy
        
        Args:
            config: LLM configuration including API credentials and settings
        """
        config.base_url = config.base_url or "https://api.deepseek.com/v1"
        config.default_model = config.default_model or "deepseek-chat"
        config.model_type = ModelType.TEXT
        super().__init__(config)

    async def chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Get chat completion from DeepSeek model
        
        Args:
            messages: List of message dictionaries with role and content
            model: Model name to use (defaults to config default)
            temperature: Sampling temperature
            stream: Whether to use streaming mode
            
        Returns:
            Dictionary with completion results or async generator for streaming
            
        Raises:
            DeepSeekError: For API specific errors
            ValueError: For invalid input parameters
        """
        try:
            return await super().chat_completion(messages, model, temperature, stream)
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise DeepSeekError(f"DeepSeek API request failed: {str(e)}") from e

    async def image_understanding(
        self,
        image_url: str,
        prompt: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process and understand image content using DeepSeek's multimodal capabilities
        
        Args:
            image_url: URL of the image to process
            prompt: Text prompt describing the task
            model: Optional model name
            
        Returns:
            Dictionary with image understanding results
            
        Raises:
            DeepSeekError: For API specific errors
            ValueError: For invalid input parameters
        """
        try:
            url = f"{self.config.base_url}/vision/completions"
            payload = {
                "model": model or self.config.default_model,
                "image_url": image_url,
                "prompt": prompt,
                "max_tokens": 1000
            }
            
            async with self.semaphore:
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self._validate_response(data)
                    return data
        except Exception as e:
            logger.error(f"DeepSeek image understanding error: {str(e)}")
            raise DeepSeekError(f"Image understanding failed: {str(e)}") from e

    async def audio_transcription(
        self,
        audio_url: str,
        language: str = "en",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio content using DeepSeek's speech capabilities
        
        Args:
            audio_url: URL of the audio file
            language: Language code (default: "en")
            model: Optional model name
            
        Returns:
            Dictionary with transcription results
            
        Raises:
            DeepSeekError: For API specific errors
            ValueError: For invalid input parameters
        """
        try:
            url = f"{self.config.base_url}/audio/transcriptions"
            payload = {
                "model": model or self.config.default_model,
                "audio_url": audio_url,
                "language": language,
                "response_format": "json"
            }
            
            async with self.semaphore:
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self._validate_response(data)
                    return data
        except Exception as e:
            logger.error(f"DeepSeek audio transcription error: {str(e)}")
            raise DeepSeekError(f"Audio transcription failed: {str(e)}") from e

    def _get_plugin_class(self, plugin_name: str) -> Type:
        """Get plugin class by name"""
        try:
            from .plugins import deepseek_plugins
            return getattr(deepseek_plugins, plugin_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load DeepSeek plugin {plugin_name}: {str(e)}")
            raise DeepSeekError(f"Plugin {plugin_name} not found") from e

    @classmethod
    def from_env(cls):
        """
        Create client from environment variables
        
        Returns:
            Configured DeepSeek proxy instance
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        return cls(LLMConfig(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            default_model="deepseek-chat"
        ))

    @classmethod
    def from_config(cls, config: DeepSeekConfig):
        """
        Create client from configuration
        
        Args:
            config: DeepSeek configuration
            
        Returns:
            Configured DeepSeek proxy instance
        """
        return cls(LLMConfig(
            api_key=config.api_key,
            base_url=config.base_url,
            default_model=config.default_model,
            max_retries=config.max_retries,
            timeout=config.timeout,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        ))

    async def update_config(self, config: DeepSeekConfig):
        """
        Update proxy configuration dynamically
        
        Args:
            config: New DeepSeek configuration
        """
        self.config = LLMConfig(
            api_key=config.api_key,
            base_url=config.base_url,
            default_model=config.default_model,
            max_retries=config.max_retries,
            timeout=config.timeout,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        # Reinitialize session with new config
        await self.close()
        self.session = aiohttp.ClientSession(
            headers=self._get_headers(),
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

async def get_deepseek_response(prompt: str, context: Optional[str] = None) -> str:
    """
    Get response from DeepSeek model with optional context
    
    Args:
        prompt: User input prompt
        context: Optional system context
        
    Returns:
        Generated response text
    """
    client = DeepSeekProxy.from_env()
    try:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat_completion(messages)
        return response['choices'][0]['message']['content']
    finally:
        await client.close()

# Example usage
if __name__ == "__main__":
    async def main():
        try:
            response = await get_deepseek_response("Explain quantum computing in simple terms")
            print(response)
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())
