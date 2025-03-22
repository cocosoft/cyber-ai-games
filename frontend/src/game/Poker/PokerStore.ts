import { writable } from 'svelte/store';
import type { Player } from './PokerLogic';

export const pokerStore = writable<{
  players: Player[];
  currentPlayer: string;
  pot: number;
  communityCards: string[];
  status: 'waiting' | 'playing' | 'finished';
}>({
  players: [],
  currentPlayer: '',
  pot: 0,
  communityCards: [],
  status: 'waiting'
});

export function addPlayer(player: Player) {
  pokerStore.update(state => ({
    ...state,
    players: [...state.players, player]
  }));
}

export function removePlayer(playerId: string) {
  pokerStore.update(state => ({
    ...state,
    players: state.players.filter(p => p.id !== playerId)
  }));
}
