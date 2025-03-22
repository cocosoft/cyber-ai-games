import { derived } from 'svelte/store';
import { persisted } from 'svelte-persisted-store';
import { validateChatMessage, validateGameState, ValidationError } from './validators.js';

export interface GameState {
  board: any[][];
  currentPlayer: string;
  status: 'waiting' | 'playing' | 'finished';
  lastUpdated: number;
  map?: {
    tiles: any[][];
  };
  players?: Array<{
    resources: {
      credits: number;
      power: number;
    };
  }>;
  // Poker specific properties
  communityCards?: string[];
  pot?: number;
  blinds?: {
    small: number;
    big: number;
  };
  currentBet?: number;
  dealerPosition?: number;
}

export interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  timestamp: number;
}

export const gameStore = persisted<GameState>('game-state', {
  board: [],
  currentPlayer: '',
  status: 'waiting',
  lastUpdated: Date.now()
});

gameStore.subscribe((value) => {
  try {
    validateGameState(value);
  } catch (error) {
    if (error instanceof ValidationError) {
      console.error('Invalid game state detected:', error.message);
      // Reset to default state
      gameStore.set({
        board: [],
        currentPlayer: '',
        status: 'waiting',
        lastUpdated: Date.now()
      });
    } else {
      console.error('Unexpected error:', error);
    }
  }
});

export const chatStore = {
  messages: persisted<ChatMessage[]>('chat-messages', []),
  
  addMessage: (message: ChatMessage) => {
    try {
      validateChatMessage(message);
      chatStore.messages.update(messages => {
        const newMessages = [...messages, message];
        return newMessages.slice(-100); // Keep last 100 messages
      });
    } catch (error) {
      if (error instanceof ValidationError) {
        console.error('Invalid chat message:', error.message);
      } else {
        console.error('Unexpected error:', error);
      }
    }
  },
  
  clear: () => {
    chatStore.messages.set([]);
  }
};

export const gameStatus = derived(
  gameStore,
  $gameStore => $gameStore.status
);

export const currentPlayer = derived(
  gameStore,
  $gameStore => $gameStore.currentPlayer
);

export const lastUpdated = derived(
  gameStore,
  $gameStore => new Date($gameStore.lastUpdated)
);
