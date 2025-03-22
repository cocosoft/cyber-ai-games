from backend.game_engine.chess_engine import ChessEngine
from backend.game_engine.cn_chess_engine import CNChessEngine
from backend.game_engine.js_red_alert_engine import JSRedAlertEngine
from typing import Dict, Any, Optional
import time
import logging
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential

# 配置日志
logger = logging.getLogger(__name__)

class GameManager:
    """游戏管理器，负责管理所有游戏引擎实例"""
    
    def __init__(self):
        self._game_engines: Dict[str, Any] = {}
        self._initialized = False

    def initialize(self):
        """初始化游戏管理器"""
        if not self._initialized:
            # 预加载常用游戏引擎
            self.get_game_engine("chess")
            self.get_game_engine("cn_chess")
            self._initialized = True
            logger.info("GameManager initialized")

    @lru_cache(maxsize=10)
    def _init_game_engine(self, game_type: str):
        """初始化游戏引擎并缓存"""
        if game_type == "chess":
            return ChessEngine()
        elif game_type == "cn_chess":
            return CNChessEngine()
        elif game_type == "js_red_alert":
            return JSRedAlertEngine()
        else:
            raise ValueError(f"Unsupported game type: {game_type}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying game engine initialization (attempt {retry_state.attempt_number})..."
        )
    )
    def get_game_engine(self, game_type: str):
        """根据游戏类型获取对应的游戏引擎"""
        if game_type not in self._game_engines:
            start_time = time.time()
            self._game_engines[game_type] = self._init_game_engine(game_type)
            elapsed_time = time.time() - start_time
            logger.info(f"Initialized {game_type} engine in {elapsed_time:.2f}s")
        
        # 健康检查
        if not self._game_engines[game_type].is_healthy():
            logger.warning(f"Game engine {game_type} is not healthy, reinitializing...")
            self._game_engines[game_type] = self._init_game_engine(game_type)
        
        return self._game_engines[game_type]

    def get_game_engine_stats(self) -> Dict[str, Any]:
        """获取游戏引擎统计信息"""
        stats = {}
        for game_type, engine in self._game_engines.items():
            stats[game_type] = {
                "initialized": engine is not None,
                "healthy": engine.is_healthy() if hasattr(engine, "is_healthy") else True,
                "last_used": getattr(engine, "last_used", None),
                "usage_count": getattr(engine, "usage_count", 0)
            }
        return stats

# 全局游戏管理器实例
game_manager = GameManager()
