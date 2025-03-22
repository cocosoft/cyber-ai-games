from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union, List, Dict

class GameType(Enum):
    CHESS = "chess"  # 国际象棋
    GO = "go"  # 围棋
    CHINESE_CHESS = "chinese_chess"  # 中国象棋
    POKER = "poker"  # 斗地主
    GOMOKU = "gomoku"  # 五子棋
    WEREWOLF = "werewolf"  # 狼人杀

class PlayerColor(Enum):
    WHITE = "white"
    BLACK = "black"

@dataclass
class Player:
    id: str
    name: str
    color: PlayerColor

@dataclass
class GameState:
    game_id: str
    game_type: GameType
    players: List[Player]
    current_turn: PlayerColor
    board_state: Union[Dict, List]  # 棋盘状态，具体格式由游戏类型决定
    history: List[Dict]  # 历史记录
    winner: Optional[PlayerColor] = None

@dataclass
class PlayerAction:
    player_id: str
    action_type: str  # 如 "move", "resign" 等
    action_data: Dict  # 具体动作数据

@dataclass
class GameMessage:
    message_type: str  # 如 "state_update", "action", "error" 等
    game_id: str
    data: Union[GameState, PlayerAction, Dict]

@dataclass
class ErrorMessage:
    error_code: str
    message: str
    details: Optional[Dict] = None

# 定义一些常用的错误代码
class ErrorCodes:
    INVALID_MOVE = "invalid_move"
    NOT_YOUR_TURN = "not_your_turn"
    GAME_NOT_FOUND = "game_not_found"
    INVALID_ACTION = "invalid_action"
    PLAYER_NOT_FOUND = "player_not_found"
    INVALID_CARD = "invalid_card"  # 无效的牌（斗地主）
    INVALID_ROLE = "invalid_role"  # 无效的角色（狼人杀）
    INVALID_VOTE = "invalid_vote"  # 无效的投票（狼人杀）
    INVALID_PIECE = "invalid_piece"  # 无效的棋子（象棋类游戏）


class ModelType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

@dataclass
class LLMConfig:
    api_key: str
    base_url: str
    default_model: str
    max_retries: int = 3
    timeout: int = 30
    temperature: float = 0.7
    max_tokens: int = 1000
    model_type: ModelType = ModelType.TEXT
    
    model_config = {
        'protected_namespaces': ()
    }

@dataclass
class LLMRequest:
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False

@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str

@dataclass
class LLMError:
    error_code: str
    message: str
    details: Optional[Dict] = None

class LLMErrorCodes:
    INVALID_API_KEY = "invalid_api_key"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MODEL_NOT_FOUND = "model_not_found"
    INVALID_REQUEST = "invalid_request"
    SERVICE_UNAVAILABLE = "service_unavailable"
