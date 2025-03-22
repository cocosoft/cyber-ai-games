from .rule_base import GameEngineBase
from shared.protocol import GameType, GameState, PlayerAction
from typing import List, Dict
import random

class WerewolfEngine(GameEngineBase):
    def __init__(self):
        """
        初始化狼人杀游戏对象。
        
        该构造函数设置了游戏的基本属性，包括游戏类型、角色列表、存活玩家列表、游戏阶段，
        以及投票和死亡玩家的情况。
        """
        # 初始化游戏类型为狼人杀
        super().__init__(GameType.WEREWOLF)
        
        # 初始化角色列表为空，用于存储游戏中所有角色
        self.roles = []
        
        # 初始化存活玩家列表为空，用于存储当前还存活的玩家
        self.alive_players = []
        
        # 初始化游戏阶段为夜晚，表示游戏开始时总是处于夜晚阶段
        self.night_phase = True
        
        # 初始化投票情况为空字典，键为玩家编号，值为该玩家投票给其他玩家的列表
        self.votes: Dict[str, List[str]] = {}
        
        # 初始化死亡玩家列表为空，用于存储游戏中已经死亡的玩家
        self.dead_players = []

    def initialize_game(self, players):
        self.roles = self.assign_roles(len(players))
        self.alive_players = [player.id for player in players]
        self.votes = {}
        self.dead_players = []
        self.night_phase = True
        return super().initialize_game(players)

    def assign_roles(self, player_count) -> List[str]:
        """
        根据玩家数量分配狼人杀游戏中的角色。
    
        参数:
        player_count -- 参与游戏的玩家数量
    
        返回:
        一个打乱顺序的角色列表，列表长度等于玩家数量。
        """
        # 基本角色分配：2狼人，1预言家，1女巫，1猎人，其余村民
        roles = ['werewolf'] * 2 + ['seer', 'witch', 'hunter']
        # 根据玩家数量补充村民角色，确保角色总数与玩家数量一致
        roles += ['villager'] * (player_count - len(roles))
        # 打乱角色顺序以随机分配
        random.shuffle(roles)
        # 返回打乱顺序后的角色列表
        return roles

    def validate_action(self, action: PlayerAction) -> bool:
        action_type = action.action_type
        if action_type == 'vote':
            target = action.action_data.get('target')
            return target in self.alive_players
        elif action_type == 'use_ability':
            role = self.get_player_role(action.player_id)
            ability = action.action_data.get('ability')
            return self.validate_ability(role, ability)
        return False

    def validate_ability(self, role: str, ability: str) -> bool:
        # 验证角色能力使用是否合法
        if role == 'werewolf':
            return ability == 'kill'
        elif role == 'seer':
            return ability == 'check'
        elif role == 'witch':
            return ability in ['save', 'poison']
        elif role == 'hunter':
            return ability == 'shoot'
        return False

    def apply_action(self, action: PlayerAction) -> GameState:
        action_type = action.action_type
        if action_type == 'vote':
            self.handle_vote(action.player_id, action.action_data['target'])
        elif action_type == 'use_ability':
            self.handle_ability(action.player_id, action.action_data)
        return self.get_game_state()

    def handle_vote(self, voter_id: str, target_id: str):
        if voter_id not in self.votes:
            self.votes[voter_id] = []
        self.votes[voter_id].append(target_id)

    def handle_ability(self, player_id: str, action_data: Dict):
        role = self.get_player_role(player_id)
        ability = action_data['ability']
        
        if role == 'werewolf' and ability == 'kill':
            target = action_data['target']
            self.dead_players.append(target)
        elif role == 'seer' and ability == 'check':
            target = action_data['target']
            # 返回目标角色信息
        elif role == 'witch' and ability == 'save':
            target = action_data['target']
            # 救人逻辑
        elif role == 'witch' and ability == 'poison':
            target = action_data['target']
            self.dead_players.append(target)
        elif role == 'hunter' and ability == 'shoot':
            target = action_data['target']
            self.dead_players.append(target)

    def get_player_role(self, player_id: str) -> str:
        player_index = self.alive_players.index(player_id)
        return self.roles[player_index]

    def get_game_state(self) -> GameState:
        return GameState(
            game_id=self.game_id,
            game_type=self.game_type,
            players=self.players,
            current_turn=self.current_turn,
            board_state={
                'phase': 'night' if self.night_phase else 'day',
                'alive_players': self.alive_players,
                'dead_players': self.dead_players
            },
            history=self.history
        )
