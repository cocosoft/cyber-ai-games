import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

# 日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 日志格式
class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "location": f"{record.pathname}:{record.lineno}",
            "function": record.funcName,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data, ensure_ascii=False)

# 日志处理器配置
def setup_logging():
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = StructuredFormatter()
    console_handler.setFormatter(console_formatter)

    # 文件日志
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = StructuredFormatter()
    file_handler.setFormatter(file_formatter)

    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # 禁用第三方库的日志
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

# 初始化日志配置
setup_logging()

# 获取日志实例
logger = logging.getLogger(__name__)

# 动态调整日志级别
def set_log_level(level: str):
    """动态设置日志级别"""
    level = level.upper()
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise ValueError(f"Invalid log level: {level}")
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.setLevel(level)
    logger.info(f"Log level changed to {level}")
