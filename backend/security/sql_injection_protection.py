"""SQL注入防护模块"""
import re
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException

class SQLInjectionProtector:
    """SQL注入防护器"""
    
    def __init__(self):
        self.patterns = [
            r"(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})\b)",
            r"(\b(OR|AND)\b\s*(\d+|\'[^\']*\')\s*=\s*(\d+|\'[^\']*\')",
            r"(--|#|\/\*[\s\S]*?\*\/)",
            r"(\b(WAITFOR|DELAY)\b\s*[\'\"]?\d",
            r"(\b(SLEEP|BENCHMARK)\b\s*\(.*?\))",
            r"(\b(LOAD_FILE|INTO\s+(OUTFILE|DUMPFILE))\b",
            r"(\b(XPATH|EXTRACTVALUE|UPDATEXML)\b\s*\(.*?\))",
            r"(\b(CHAR|ASCII|ORD|CONCAT)\b\s*\(.*?\))",
        ]
        self.replacement = "[REDACTED]"

    def sanitize_input(self, input_data: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """清理输入数据中的潜在SQL注入
        
        Args:
            input_data: 需要清理的输入数据
            
        Returns:
            清理后的数据
            
        Raises:
            HTTPException: 如果检测到SQL注入
        """
        if isinstance(input_data, dict):
            return self._sanitize_dict(input_data)
        elif isinstance(input_data, list):
            return self._sanitize_list(input_data)
        elif isinstance(input_data, str):
            return self._sanitize_string(input_data)
        return input_data

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理字典中的输入数据"""
        sanitized = {}
        for key, value in data.items():
            sanitized[key] = self.sanitize_input(value)
        return sanitized

    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """清理列表中的输入数据"""
        return [self.sanitize_input(item) for item in data]

    def _sanitize_string(self, value: str) -> str:
        """清理字符串中的输入数据"""
        for pattern in self.patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=400,
                    detail="Potential SQL injection detected"
                )
        return value
