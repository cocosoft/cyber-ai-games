"""敏感数据过滤模块"""
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class SensitiveDataFilter:
    """敏感数据过滤器"""
    
    def __init__(self):
        self.patterns = [
            r"(?i)password",
            r"(?i)token",
            r"(?i)secret",
            r"(?i)api[_-]?key",
            r"(?i)credit[_-]?card",
            r"\d{3}-\d{2}-\d{4}",  # SSN
            r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",  # Credit card
        ]
        self.replacement = "[REDACTED]"

    def filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤字典中的敏感数据
        
        Args:
            data: 需要过滤的字典数据
            
        Returns:
            过滤后的字典
        """
        filtered = {}
        for key, value in data.items():
            if isinstance(value, dict):
                filtered[key] = self.filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = self.filter_list(value)
            elif isinstance(value, str):
                filtered[key] = self.filter_string(key, value)
            else:
                filtered[key] = value
        return filtered

    def filter_list(self, data: List[Any]) -> List[Any]:
        """过滤列表中的敏感数据
        
        Args:
            data: 需要过滤的列表数据
            
        Returns:
            过滤后的列表
        """
        return [self.filter_dict(item) if isinstance(item, dict) else item for item in data]

    def filter_string(self, key: str, value: str) -> str:
        """过滤字符串中的敏感数据
        
        Args:
            key: 字段名
            value: 字段值
            
        Returns:
            过滤后的字符串
        """
        if any(re.search(pattern, key) for pattern in self.patterns):
            return self.replacement
            
        for pattern in self.patterns:
            value = re.sub(pattern, self.replacement, value)
            
        return value

    def filter_model(self, model: BaseModel) -> Dict[str, Any]:
        """过滤Pydantic模型中的敏感数据
        
        Args:
            model: 需要过滤的Pydantic模型
            
        Returns:
            过滤后的字典
        """
        return self.filter_dict(model.dict())
