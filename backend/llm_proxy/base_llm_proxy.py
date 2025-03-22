import os
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, AsyncGenerator, Type, Union
import aiohttp
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field, validator
from enum import Enum

logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"

class PluginConfig(BaseModel):
    name: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)

class LLMConfig(BaseModel):
    model_config = {'protected_namespaces': ()}
    
    api_key: str
    base_url: str
    default_model: str
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 5
    model_type: ModelType = ModelType.TEXT
    plugins: List[PluginConfig] = Field(default_factory=list)

class BaseLLMProxy:
    """Base class for LLM proxy implementations"""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM proxy with configuration
        
        Args:
            config: LLM configuration including API credentials and settings
        """
        self.config = config
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        self.semaphore = asyncio.Semaphore(self.config.rate_limit)
        self._plugins = self._initialize_plugins()

    async def close(self):
        """Clean up resources"""
        await self.session.close()
        for plugin in self._plugins.values():
            if hasattr(plugin, 'close'):
                await plugin.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Base implementation for chat completion
        
        Args:
            messages: List of message dictionaries with role and content
            model: Model name to use (defaults to config default)
            temperature: Sampling temperature
            stream: Whether to use streaming mode
            
        Returns:
            Dictionary with completion results or async generator for streaming
        """
        model = model or self.config.default_model
        url = f"{self.config.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000,
            "stream": stream
        }

        async with self.semaphore:
            try:
                logger.info(f"Sending request to {self.config.base_url}")
                async with self.session.post(url, json=payload) as response:
                    response.raise_for_status()
                    
                    if stream:
                        return self._handle_stream_response(response)
                    else:
                        data = await response.json()
                        self._validate_response(data)
                        logger.info("Successfully received valid response")
                        return data
            except aiohttp.ClientError as e:
                logger.error(f"API request failed: {str(e)}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response: {str(e)}")
                raise
            except ValueError as e:
                logger.error(f"Invalid response format: {str(e)}")
                raise

    async def _handle_stream_response(self, response: aiohttp.ClientResponse) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming response"""
        async for line in response.content:
            if line.startswith(b"data: "):
                chunk = line[len(b"data: "):].strip()
                if chunk == b"[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    yield data
                except json.JSONDecodeError:
                    continue

    def _validate_response(self, data: Dict[str, Any]):
        """
        Validate the response structure
        
        Args:
            data: Response data to validate
            
        Raises:
            ValueError: If response structure is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid response format: expected dictionary")
        if 'choices' not in data or not isinstance(data['choices'], list):
            raise ValueError("Invalid response format: missing or invalid choices")
        if len(data['choices']) == 0:
            raise ValueError("No choices in response")
        if 'message' not in data['choices'][0]:
            raise ValueError("Invalid response format: missing message")
        if 'content' not in data['choices'][0]['message']:
            raise ValueError("Invalid response format: missing content")

    @classmethod
    def from_env(cls, env_var: str):
        """
        Create client from environment variables
        
        Args:
            env_var: Environment variable name containing API key
            
        Returns:
            Configured LLM proxy instance
        """
        # Extract prefix by removing _API_KEY suffix if present
        prefix = env_var.replace("_API_KEY", "")
        
        api_key = os.getenv(env_var)
        base_url = os.getenv(f"{prefix}_BASE_URL")
        default_model = os.getenv(f"{prefix}_DEFAULT_MODEL")
        
        if not api_key:
            raise ValueError(f"{env_var} environment variable is required")
        if not base_url:
            raise ValueError(f"{prefix}_BASE_URL environment variable is required")
        if not default_model:
            raise ValueError(f"{prefix}_DEFAULT_MODEL environment variable is required")
            
        return cls(LLMConfig(
            api_key=api_key,
            base_url=base_url,
            default_model=default_model
        ))

    async def image_understanding(
        self,
        image_url: str,
        prompt: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process and understand image content
        
        Args:
            image_url: URL of the image to process
            prompt: Text prompt describing the task
            model: Optional model name
            
        Returns:
            Dictionary with image understanding results
        """
        raise NotImplementedError("Image understanding not implemented")

    async def audio_transcription(
        self,
        audio_url: str,
        language: str = "en",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio content
        
        Args:
            audio_url: URL of the audio file
            language: Language code (default: "en")
            model: Optional model name
            
        Returns:
            Dictionary with transcription results
        """
        raise NotImplementedError("Audio transcription not implemented")

    def _initialize_plugins(self) -> Dict[str, Any]:
        """Initialize configured plugins"""
        plugins = {}
        for plugin_config in self.config.plugins:
            if plugin_config.enabled:
                try:
                    plugin_class = self._get_plugin_class(plugin_config.name)
                    plugin = plugin_class(plugin_config.config)
                    plugins[plugin_config.name] = plugin
                except Exception as e:
                    logger.error(f"Failed to initialize plugin {plugin_config.name}: {str(e)}")
        return plugins

    def _get_plugin_class(self, plugin_name: str) -> Type:
        """Get plugin class by name"""
        # Implementation should be provided by concrete classes
        raise NotImplementedError("Plugin system not implemented")
