from typing import Dict, List, Optional
from datetime import datetime
from .rule_base import GameEngineBase

class JSRedAlertEngine(GameEngineBase):
    def __init__(self):
        super().__init__()
        self.map_size = (10, 10)
        self.players = []
        self.game_state = {
            'map': {
                'tiles': [[{'terrain': 'grass', 'unit': None} for _ in range(self.map_size[1])] 
                          for _ in range(self.map_size[0])]
            },
            'players': [],
            'current_player': None,
            'status': 'waiting',
            'lastUpdated': datetime.now().timestamp()
        }

    def add_player(self, player_id: str) -> bool:
        if len(self.players) >= 2:
            return False
            
        # 验证玩家ID格式
        if not isinstance(player_id, str) or len(player_id) < 8:
            return False
            
        # 检查是否已存在相同ID的玩家
        if any(p['id'] == player_id for p in self.players):
            return False
            
        self.players.append({
            'id': player_id,
            'resources': {
                'credits': 1000,
                'power': 100
            },
            'units': [],
            'connection_time': datetime.now().timestamp()
        })
        
        if len(self.players) == 2:
            self.game_state['status'] = 'playing'
            self.game_state['current_player'] = self.players[0]['id']
            self.game_state['players'] = [p['id'] for p in self.players]
            
        return True

    def get_state(self) -> Dict:
        return self.game_state

    def handle_action(self, player_id: str, action: Dict) -> Dict:
        result = {
            'success': False,
            'message': '',
            'new_state': None
        }
        
        if self.game_state['status'] != 'playing':
            result['message'] = 'Game is not in playing state'
            return result
            
        if player_id != self.game_state['current_player']:
            result['message'] = 'Not your turn'
            return result
            
        action_type = action.get('type')
        if action_type == 'move':
            result['success'] = self._handle_move_action(player_id, action)
        elif action_type == 'build':
            result['success'] = self._handle_build_action(player_id, action)
        elif action_type == 'attack':
            result['success'] = self._handle_attack_action(player_id, action)
        elif action_type == 'end_turn':
            result['success'] = self.end_turn(player_id)
        else:
            result['message'] = 'Invalid action type'
            return result
            
        if result['success']:
            result['new_state'] = self.get_state()
            result['message'] = 'Action successful'
            
        return result

    def _handle_move_action(self, player_id: str, action: Dict) -> bool:
        try:
            unit_id = action.get('unit_id')
            to_pos = action.get('to')
            
            # Find unit and validate ownership
            player = next(p for p in self.players if p['id'] == player_id)
            unit = next((u for u in player['units'] if u['id'] == unit_id), None)
            if not unit:
                return False
                
            # Validate move position
            if not (0 <= to_pos['row'] < self.map_size[0] and 
                    0 <= to_pos['col'] < self.map_size[1]):
                return False
                
            # Check if target tile is empty
            target_tile = self.game_state['map']['tiles'][to_pos['row']][to_pos['col']]
            if target_tile.get('unit') or target_tile.get('building'):
                return False
                
            # Update unit position
            old_pos = unit['position']
            self.game_state['map']['tiles'][old_pos['row']][old_pos['col']]['unit'] = None
            self.game_state['map']['tiles'][to_pos['row']][to_pos['col']]['unit'] = unit
            unit['position'] = to_pos
            
            self.game_state['lastUpdated'] = datetime.now().timestamp()
            return True
        except Exception as e:
            print(f'Move action error: {str(e)}')
            return False

    def _handle_build_action(self, player_id: str, action: Dict) -> bool:
        building_type = action.get('building')
        position = action.get('position')
        player = next(p for p in self.players if p['id'] == player_id)
        
        # Validate position and resources
        if not self._can_build_at(position, building_type, player):
            return False
            
        # Deduct resources
        cost = self._get_building_cost(building_type)
        player['resources']['credits'] -= cost
        
        # Add building
        self.game_state['map']['tiles'][position['row']][position['col']]['building'] = {
            'type': building_type,
            'owner': player_id
        }
        
        self.game_state['lastUpdated'] = datetime.now().timestamp()
        return True

    def _handle_attack_action(self, player_id: str, action: Dict) -> bool:
        attacker_id = action.get('attacker_id')
        target_id = action.get('target_id')
        
        # Find units
        attacker = self._find_unit(attacker_id, player_id)
        target = self._find_unit(target_id)
        
        if not attacker or not target:
            return False
            
        # Calculate damage
        damage = self._calculate_damage(attacker, target)
        target['health'] -= damage
        
        # Check if target is destroyed
        if target['health'] <= 0:
            self._remove_unit(target)
            
        self.game_state['lastUpdated'] = datetime.now().timestamp()
        return True

    def _can_build_at(self, position: Dict, building_type: str, player: Dict) -> bool:
        # Check if position is valid and empty
        if not (0 <= position['row'] < self.map_size[0] and 
                0 <= position['col'] < self.map_size[1]):
            return False
            
        tile = self.game_state['map']['tiles'][position['row']][position['col']]
        if tile.get('building') or tile.get('unit'):
            return False
            
        # Check if player has enough resources
        cost = self._get_building_cost(building_type)
        return player['resources']['credits'] >= cost

    def _get_building_cost(self, building_type: str) -> int:
        # Return cost based on building type
        costs = {
            'power_plant': 800,
            'barracks': 500,
            'refinery': 1000
        }
        return costs.get(building_type, 0)

    def _find_unit(self, unit_id: str, owner_id: Optional[str] = None) -> Optional[Dict]:
        for player in self.players:
            if owner_id and player['id'] != owner_id:
                continue
            for unit in player['units']:
                if unit['id'] == unit_id:
                    return unit
        return None

    def _remove_unit(self, unit: Dict):
        # Remove unit from map and player
        pos = unit['position']
        self.game_state['map']['tiles'][pos['row']][pos['col']]['unit'] = None
        for player in self.players:
            player['units'] = [u for u in player['units'] if u['id'] != unit['id']]

    def _calculate_damage(self, attacker: Dict, target: Dict) -> int:
        # Simple damage calculation
        return max(0, attacker['attack'] - target['defense'])

    def end_turn(self, player_id: str) -> bool:
        if player_id != self.game_state['current_player']:
            return False
            
        current_index = self.players.index(
            next(p for p in self.players if p['id'] == player_id))
        next_index = (current_index + 1) % len(self.players)
        
        self.game_state['current_player'] = self.players[next_index]['id']
        self.game_state['lastUpdated'] = datetime.now().timestamp()
        return True
