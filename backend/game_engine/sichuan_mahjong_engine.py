from typing import List, Dict, Optional
from backend.game_engine.rule_base import GameEngineBase
import random

class SichuanMahjongEngine(GameEngineBase):
    """Sichuan Mahjong game engine implementation"""
    
    def __init__(self):
        """
        Initializes the game environment, including tile layout, player information, and game status.
        """
        super().__init__()  # Initialize the parent class constructor, if any
        self.tiles = self._initialize_tiles()  # Initialize and get the layout of all tiles
        self.players = []  # Initialize the list of players
        self.current_player = 0  # Set the starting player index to 0
        self.discards = []  # Initialize the discard pile list
        self.wall = []  # Initialize the wall (remaining tiles that have not been drawn)
        self.wind = 1  # East wind starts, indicating the starting wind direction
        self.round = 1  # The first round starts
        
    def _initialize_tiles(self) -> List[str]:
        """Initialize the standard Sichuan Mahjong tile set"""
        # Define the three suits of Mahjong tiles
        suits = ['bamboo', 'character', 'dot']
        # Define the honor tiles of Mahjong
        honors = ['east', 'south', 'west', 'north', 'red', 'green', 'white']
        
        # Create numbered tiles (1-9) for each suit
        tiles = []
        for suit in suits:
            # Each suit has 9 numbered tiles, with 4 of each tile
            tiles.extend([f'{suit}_{i}' for i in range(1, 10)] * 4)
            
        # Create honor tiles
        # There are 7 honor tiles, with 4 of each tile
        tiles.extend([f'honor_{honor}' for honor in honors] * 4)
        
        # Add flower tiles (8 total)
        # There are 8 flower tiles, representing different flowers
        tiles.extend([f'flower_{i}' for i in range(1, 9)])
        
        # Return the complete set of tiles
        return tiles
    
    def start_game(self, players: List[str]) -> Dict:
        """Initialize a new game with the given players"""
        if len(players) != 4:
            raise ValueError("Sichuan Mahjong requires exactly 4 players")
            
        self.players = players
        self.wall = self._shuffle_tiles()
        self._deal_initial_tiles()
        
        return {
            'status': 'started',
            'players': self.players,
            'current_player': self.players[self.current_player],
            'wall_count': len(self.wall)
        }
        
    def _shuffle_tiles(self) -> List[str]:
        """Shuffle the tiles to create the wall"""
        return random.sample(self.tiles, len(self.tiles))
        
    def _deal_initial_tiles(self):
        """Deal initial 13 tiles to each player"""
        for _ in range(13):
            for player in range(4):
                self.players[player].append(self.wall.pop())
                
    def draw_tile(self, player: str) -> Optional[str]:
        """Player draws a tile from the wall"""
        if player != self.players[self.current_player]:
            raise ValueError("Not your turn")
            
        if not self.wall:
            return None
            
        tile = self.wall.pop()
        self.players[self.current_player].append(tile)
        return tile
        
    def discard_tile(self, player: str, tile: str):
        """Player discards a tile"""
        if player != self.players[self.current_player]:
            raise ValueError("Not your turn")
            
        if tile not in self.players[self.current_player]:
            raise ValueError("Tile not in player's hand")
            
        self.players[self.current_player].remove(tile)
        self.discards.append(tile)
        self.current_player = (self.current_player + 1) % 4
        
    def check_win(self, player: str) -> bool:
        """Check if player has a winning hand"""
        # Basic winning condition check
        hand = self.players[self.players.index(player)]
        return len(hand) == 14 and self._is_winning_hand(hand)
        
    def _is_winning_hand(self, hand: List[str]) -> bool:
        """Check if hand meets Sichuan Mahjong winning conditions"""
        # TODO: Implement complex Sichuan Mahjong winning logic
        return True
        
    def get_game_state(self) -> Dict:
        """Return current game state"""
        return {
            'players': self.players,
            'current_player': self.players[self.current_player],
            'discards': self.discards,
            'wall_count': len(self.wall),
            'wind': self.wind,
            'round': self.round
        }

    def initial_state(self) -> dict:
        """Generate initial game state"""
        return {
            'players': [],
            'current_player': 0,
            'discards': [],
            'wall': [],
            'wind': 1,
            'round': 1
        }

    def validate_action(self, action: str, state: dict) -> bool:
        """Validate if action is legal"""
        action_type = action.get('type')
        if action_type == 'draw':
            return state['current_player'] == action['player']
        elif action_type == 'discard':
            return (state['current_player'] == action['player'] and
                    action['tile'] in state['players'][state['current_player']])
        return False

    def apply_action(self, action: str, state: dict) -> dict:
        """Apply action and return new game state"""
        new_state = state.copy()
        if action['type'] == 'draw':
            if new_state['wall']:
                tile = new_state['wall'].pop()
                new_state['players'][new_state['current_player']].append(tile)
        elif action['type'] == 'discard':
            tile = action['tile']
            player_hand = new_state['players'][new_state['current_player']]
            player_hand.remove(tile)
            new_state['discards'].append(tile)
            new_state['current_player'] = (new_state['current_player'] + 1) % 4
        return new_state
