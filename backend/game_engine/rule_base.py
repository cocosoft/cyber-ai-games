from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging

class GameEngineBase(ABC):
    """Base class for all game engines implementations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.players = []
        self.current_player = 0
        self.game_state = {}
        self.history = []
        
    @abstractmethod
    def initial_state(self) -> dict:
        """Generate initial game state"""
        pass
    
    @abstractmethod
    def validate_action(self, action: Dict, state: dict) -> bool:
        """Validate if action is legal"""
        pass
    
    @abstractmethod
    def apply_action(self, action: Dict, state: dict) -> dict:
        """Apply action and return new game state"""
        pass
        
    def add_player(self, player_id: str) -> bool:
        """Add a player to the game"""
        if player_id in self.players:
            self.logger.warning(f"Player {player_id} already in game")
            return False
        self.players.append(player_id)
        return True
        
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game"""
        if player_id not in self.players:
            self.logger.warning(f"Player {player_id} not found")
            return False
        self.players.remove(player_id)
        return True
        
    def next_turn(self) -> str:
        """Advance to next player's turn"""
        self.current_player = (self.current_player + 1) % len(self.players)
        return self.players[self.current_player]
        
    def get_current_player(self) -> str:
        """Get current player ID"""
        return self.players[self.current_player]
        
    def get_game_history(self) -> List[dict]:
        """Get complete game history"""
        return self.history.copy()
        
    def save_state(self) -> None:
        """Save current game state to history"""
        self.history.append({
            'state': self.game_state.copy(),
            'players': self.players.copy(),
            'current_player': self.current_player
        })
        
    def load_state(self, state_index: int) -> bool:
        """Load game state from history"""
        if state_index < 0 or state_index >= len(self.history):
            return False
        saved_state = self.history[state_index]
        self.game_state = saved_state['state'].copy()
        self.players = saved_state['players'].copy()
        self.current_player = saved_state['current_player']
        return True
        
    @classmethod
    def get_legal_actions(cls, state: dict) -> List[Dict]:
        """Get list of legal actions for current state"""
        return []
        
    def is_game_over(self) -> bool:
        """Check if game has ended"""
        return False
        
    def get_winner(self) -> Optional[str]:
        """Get winning player if game is over"""
        return None
