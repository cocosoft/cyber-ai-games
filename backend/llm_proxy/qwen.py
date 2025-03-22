import os
from typing import Optional, Dict, Any, AsyncGenerator, Union
from pydantic import BaseModel, validator
from backend.llm_proxy.base_llm_proxy import BaseLLMProxy, LLMConfig, ModelType
import json
import logging
import aiohttp
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class QwenConfig(BaseModel):
    """通义千问配置模型"""
    api_key: str
    base_url: str = "https://dashscope.aliyuncs.com"
    default_model: str = "qwen-chat"
    max_retries: int = 3
    timeout: int = 30
    temperature: float = 0.7
    max_tokens: int = 1000

    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("Invalid API key")
        return v

class QwenProxy(BaseLLMProxy):
    """通义千问平台实现"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.config.base_url = config.base_url or "https://dashscope.aliyuncs.com"
        self.config.default_model = config.default_model or "qwen-chat"
        self.config.model_type = ModelType.TEXT

    async def chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        try:
            return await super().chat_completion(messages, model, temperature, stream)
        except Exception as e:
            logger.error(f"Qwen API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Qwen API request failed: {str(e)}")

    @classmethod
    def from_config(cls, config: QwenConfig):
        return cls(LLMConfig(
            api_key=config.api_key,
            base_url=config.base_url,
            default_model=config.default_model,
            max_retries=config.max_retries,
            timeout=config.timeout,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        ))
