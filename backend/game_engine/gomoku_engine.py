from .rule_base import GameEngineBase
from shared.protocol import GameType, PlayerColor, GameState, PlayerAction

class GomokuEngine(GameEngineBase):
    def __init__(self):
        super().__init__(GameType.GOMOKU)
        self.board_size = 15
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
        self.win_length = 5

    def initialize_game(self, players):
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
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
        
        if self.check_win(x, y, color):
            self.winner = color
            
        return self.get_game_state()

    def check_win(self, x, y, color) -> bool:
        # 检查四个方向是否五子连珠
        directions = [
            (1, 0),  # 水平
            (0, 1),  # 垂直
            (1, 1),  # 对角线
            (1, -1)  # 反对角线
        ]
        
        for dx, dy in directions:
            count = 1
            # 正向检查
            nx, ny = x + dx, y + dy
            while 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if self.board[nx][ny] == color:
                    count += 1
                    nx += dx
                    ny += dy
                else:
                    break
            # 反向检查
            nx, ny = x - dx, y - dy
            while 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if self.board[nx][ny] == color:
                    count += 1
                    nx -= dx
                    ny -= dy
                else:
                    break
            if count >= self.win_length:
                return True
        return False

    def get_game_state(self) -> GameState:
        return GameState(
            game_id=self.game_id,
            game_type=self.game_type,
            players=self.players,
            current_turn=self.current_turn,
            board_state=self.board,
            history=self.history,
            winner=self.winner
        )
