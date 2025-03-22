from .rule_base import GameEngineBase
from typing import Dict, List
from shared.protocol import GameType, PlayerColor, GameState, PlayerAction

class CNChessEngine(GameEngineBase):
    def __init__(self):
        super().__init__()
        self.game_type = GameType.CHINESE_CHESS
        self.board_size = (10, 9)  # 10 rows, 9 columns
        self.board = self._create_initial_board()
        self.current_player = PlayerColor.WHITE
        self.river_row = 4  # River is between row 4 and 5
        self.palace_white = [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5)]
        self.palace_black = [(9, 3), (9, 4), (9, 5), (8, 3), (8, 4), (8, 5)]

    def _create_initial_board(self) -> List[List[str]]:
        return [
            ['車', '馬', '象', '士', '帥', '士', '象', '馬', '車'],
            ['', '', '', '', '', '', '', '', ''],
            ['', '砲', '', '', '', '', '', '砲', ''],
            ['兵', '', '兵', '', '兵', '', '兵', '', '兵'],
            ['', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['兵', '', '兵', '', '兵', '', '兵', '', '兵'],
            ['', '砲', '', '', '', '', '', '砲', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['車', '馬', '象', '士', '帥', '士', '象', '馬', '車']
        ]

    def initialize_game(self, players):
        self.board = self._create_initial_board()
        self.current_player = PlayerColor.WHITE
        return super().initialize_game(players)

    def validate_move(self, action: PlayerAction) -> bool:
        x1, y1 = action.action_data['from']
        x2, y2 = action.action_data['to']
        piece = self.board[x1][y1]
        
        if not piece:
            return False
            
        # Validate piece movement rules
        # (Implementation of Chinese chess rules would go here)
        return True

    def apply_move(self, action: PlayerAction) -> GameState:
        x1, y1 = action.action_data['from']
        x2, y2 = action.action_data['to']
        piece = self.board[x1][y1]
        
        # Handle special moves (cannon capture, river crossing, palace restrictions)
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

    def validate_action(self, action: Dict, state: dict) -> bool:
        """验证动作是否合法"""
        return self.validate_move(action)

    def is_healthy(self) -> bool:
        """检查引擎是否健康"""
        return True
