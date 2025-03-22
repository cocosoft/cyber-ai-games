from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.database import SessionLocal, LLMConfig
from backend.security.encryption import encryption_manager
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """管理应用配置"""
    def __init__(self):
        self.config = {}

    def load_config(self):
        """加载配置"""
        # TODO: 实现配置加载逻辑
        pass

    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value

class LLMConfigModel(BaseModel):
    model: str
    api_key: str
    endpoint: str

def save_config(model: str, api_key: str, endpoint: str, db: SessionLocal) -> bool:
    """保存LLM配置"""
    try:
        # 加密API密钥
        encrypted_api_key = encryption_manager.encrypt(api_key)
        
        # 检查是否已存在该模型的配置
        existing_config = db.query(LLMConfig).filter(LLMConfig.model == model).first()
        
        if existing_config:
            # 更新现有配置
            existing_config.api_key = encrypted_api_key
            existing_config.endpoint = endpoint
        else:
            # 创建新配置
            new_config = LLMConfig(
                model=model,
                api_key=encrypted_api_key,
                endpoint=endpoint
            )
            db.add(new_config)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save config for {model}: {str(e)}")
        raise e

def get_config(model: str, db: SessionLocal) -> Optional[Dict[str, Any]]:
    """获取指定模型的配置"""
    try:
        config = db.query(LLMConfig).filter(LLMConfig.model == model).first()
        if config:
            # 解密API密钥
            decrypted_api_key = encryption_manager.decrypt(config.api_key)
            return {
                "model": config.model,
                "api_key": decrypted_api_key,
                "endpoint": config.endpoint
            }
        return None
    except Exception as e:
        logger.error(f"Failed to get config for {model}: {str(e)}")
        raise e
