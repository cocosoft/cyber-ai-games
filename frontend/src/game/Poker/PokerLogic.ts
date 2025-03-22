import { gameStore } from '../../modules/core/stores';

export interface GameState {
  board: string[];
  players: Player[];
  communityCards: string[];
  pot: number;
  currentPlayer: string;
  status: 'waiting' | 'in_progress' | 'finished';
  lastUpdated: number;
}

export interface Player {
  id: string;
  name: string;
  chips: number;
}

export function handleAction(action: 'fold' | 'call' | 'raise') {
  gameStore.update(state => {
    switch(action) {
      case 'fold':
        return { ...state, status: 'finished' };
      case 'call':
        return { ...state, pot: (state.pot || 0) + 10 };
      case 'raise':
        return { ...state, pot: (state.pot || 0) + 20 };
      default:
        return state;
    }
  });
}

export function initializeGame() {
  gameStore.set({
    board: [],
    players: [],
    communityCards: [],
    pot: 0,
    currentPlayer: '',
    status: 'waiting',
    lastUpdated: Date.now()
  });
}
