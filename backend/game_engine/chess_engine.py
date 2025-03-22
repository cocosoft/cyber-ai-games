from .rule_base import GameEngineBase
from shared.protocol import GameType, PlayerColor, GameState, PlayerAction
from typing import List, Tuple, Dict, Optional
import enum

class PieceType(enum.Enum):
    PAWN = 'p'
    KNIGHT = 'n'
    BISHOP = 'b'
    ROOK = 'r'
    QUEEN = 'q'
    KING = 'k'

class ChessEngine(GameEngineBase):
    def __init__(self):
        super().__init__()
        self.game_type = GameType.CHESS
        self.board_size = 8
        self.board = self._create_initial_board()
        self.current_player = PlayerColor.WHITE
        self.castling_rights = {
            PlayerColor.WHITE: {'king_side': True, 'queen_side': True},
            PlayerColor.BLACK: {'king_side': True, 'queen_side': True}
        }
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def _create_initial_board(self) -> List[List[str]]:
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

    def initialize_game(self, players):
        self.board = self._create_initial_board()
        self.current_player = PlayerColor.WHITE
        self.castling_rights = {
            PlayerColor.WHITE: {'king_side': True, 'queen_side': True},
            PlayerColor.BLACK: {'king_side': True, 'queen_side': True}
        }
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        return super().initialize_game(players)

    def validate_action(self, action: Dict, state: dict) -> bool:
        """Validate if action is legal"""
        if not isinstance(action, dict):
            return False
            
        try:
            x1, y1 = action['from']
            x2, y2 = action['to']
            piece = self.board[x1][y1]
            
            if not piece:
                return False
                
            # Validate piece movement rules
            # (Implementation of chess rules would go here)
            return True
        except (KeyError, TypeError, IndexError):
            return False

    def apply_move(self, action: PlayerAction) -> GameState:
        x1, y1 = action.action_data['from']
        x2, y2 = action.action_data['to']
        piece = self.board[x1][y1]
        
        # Handle special moves (castling, en passant, promotion)
        # Update game state
        
        self.board[x2][y2] = piece
        self.board[x1][y1] = ''
        
        # Switch players
        self.current_player = PlayerColor.BLACK if self.current_player == PlayerColor.WHITE else PlayerColor.WHITE
        
        return self.get_game_state()

    def get_game_state(self) -> GameState:
        return GameState(
            game_id=self.game_id,
            game_type=self.game_type,
            players=self.players,
            current_turn=self.current_player,
            board_state=self.board,
            history=self.history
        )

    def apply_action(self, action: PlayerAction) -> GameState:
        """应用玩家动作并返回新的游戏状态"""
        return self.apply_move(action)

    def initial_state(self) -> GameState:
        """返回游戏的初始状态"""
        return GameState(
            game_id=self.game_id,
            game_type=self.game_type,
            players=self.players,
            current_turn=PlayerColor.WHITE,
            board_state=self._create_initial_board(),
            history=[]
        )

    def is_healthy(self) -> bool:
        """检查引擎是否健康运行"""
        return True  # 简单返回True表示健康
