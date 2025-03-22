from .rule_base import GameEngineBase
from shared.protocol import GameType, PlayerColor, GameState, PlayerAction

class GoEngine(GameEngineBase):
    def __init__(self):
        super().__init__(GameType.GO)
        self.board_size = 19
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
        self.komi = 6.5  # 贴目
        self.captured_stones = {PlayerColor.BLACK: 0, PlayerColor.WHITE: 0}

    def initialize_game(self, players):
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
        self.captured_stones = {PlayerColor.BLACK: 0, PlayerColor.WHITE: 0}
        return super().initialize_game(players)

    def validate_move(self, action: PlayerAction) -> bool:
        x, y = action.action_data['x'], action.action_data['y']
        if not (0 <= x < self.board_size and 0 <= y < self.board_size):
            return False
        if self.board[x][y] is not None:
            return False
        return True

    def apply_move(self, action: PlayerAction) -> GameState:
        x, y = action.action_data['x'], action.action_data['y']
        color = self.get_player_color(action.player_id)
        self.board[x][y] = color
        self.capture_stones(x, y, color)
        return self.get_game_state()

    def capture_stones(self, x, y, color):
        # 实现提子逻辑
        pass

    def calculate_score(self):
        # 实现终局计分逻辑
        pass

    def get_game_state(self) -> GameState:
        return GameState(
            game_id=self.game_id,
            game_type=self.game_type,
            players=self.players,
            current_turn=self.current_turn,
            board_state=self.board,
            history=self.history
        )
