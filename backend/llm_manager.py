from typing import Dict, Optional, List, TypedDict
from dataclasses import dataclass
from backend.llm_proxy.base_llm_proxy import BaseLLMProxy
from backend.logging_config import logger
import json
import os

# 模型配置类型
class ModelConfig(TypedDict):
    api_key: str
    endpoint: Optional[str]
    enabled: bool

# 模型状态类型
@dataclass
class ModelStatus:
    name: str
    enabled: bool
    config: ModelConfig

class LLMManager:
    def __init__(self):
        self.llm_proxies: Dict[str, BaseLLMProxy] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self.config_file = "llm_config.json"
        self.load_config()

    def load_config(self) -> None:
        """加载模型配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.model_configs = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")
                self.model_configs = {}

    def save_config(self) -> None:
        """保存模型配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_configs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")

    def init_llm_proxy(self, model_name: str, config: ModelConfig) -> Optional[BaseLLMProxy]:
        """根据模型名称和配置初始化LLM代理"""
        try:
            if model_name == "deepseek":
                from backend.llm_proxy.deepseek import DeepSeekProxy
                return DeepSeekProxy.from_config(config)
            elif model_name == "baichuan":
                from backend.llm_proxy.baichuan import BaichuanProxy
                return BaichuanProxy.from_config(config)
            # 其他模型初始化...
            else:
                logger.warning(f"Unsupported model: {model_name}")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize {model_name}: {str(e)}")
            return None

    def validate_config(self, config: ModelConfig) -> bool:
        """验证模型配置"""
        if not config.get('api_key'):
            return False
        return True

    def add_model(self, model_name: str, config: ModelConfig) -> bool:
        """添加一个新模型"""
        if model_name in self.model_configs:
            logger.warning(f"Model {model_name} already exists")
            return False
            
        if not self.validate_config(config):
            logger.error(f"Invalid config for model {model_name}")
            return False
            
        self.model_configs[model_name] = config
        self.save_config()
        
        # 如果启用则初始化代理
        if config.get('enabled', False):
            proxy = self.init_llm_proxy(model_name, config)
            if proxy:
                self.llm_proxies[model_name] = proxy
                return True
        return True

    def remove_model(self, model_name: str) -> bool:
        """移除一个模型"""
        if model_name in self.model_configs:
            del self.model_configs[model_name]
            if model_name in self.llm_proxies:
                del self.llm_proxies[model_name]
            self.save_config()
            return True
        return False

    def enable_model(self, model_name: str) -> bool:
        """启用一个已存在的模型"""
        if model_name in self.model_configs:
            config = self.model_configs[model_name]
            config['enabled'] = True
            proxy = self.init_llm_proxy(model_name, config)
            if proxy:
                self.llm_proxies[model_name] = proxy
                self.save_config()
                return True
        return False

    def disable_model(self, model_name: str) -> bool:
        """禁用一个已存在的模型"""
        if model_name in self.model_configs:
            self.model_configs[model_name]['enabled'] = False
            if model_name in self.llm_proxies:
                del self.llm_proxies[model_name]
            self.save_config()
            return True
        return False

    def get_model_status(self) -> List[ModelStatus]:
        """获取所有模型状态"""
        return [
            ModelStatus(
                name=name,
                enabled=config.get('enabled', False),
                config=config
            )
            for name, config in self.model_configs.items()
        ]

    def get_active_models(self) -> Dict[str, BaseLLMProxy]:
        """获取当前激活的模型"""
        return {name: proxy for name, proxy in self.llm_proxies.items() 
                if self.model_configs.get(name, {}).get('enabled', False)}

    def get_available_models(self) -> List[str]:
        """获取所有可用的模型名称"""
        return list(self.model_configs.keys())

    def get_llm_proxy(self, model: Optional[str] = None) -> BaseLLMProxy:
        """获取LLM代理，如果指定模型则返回该模型，否则返回优先级最高的可用模型"""
        if model:
            if model in self.llm_proxies:
                return self.llm_proxies[model]
            raise ValueError(f"Model {model} is not active")
        
        # 返回第一个可用的模型
        if self.llm_proxies:
            return next(iter(self.llm_proxies.values()))
        
        raise ValueError("No active models available")

# 单例实例
llm_manager = LLMManager()
