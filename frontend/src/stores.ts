import { writable } from 'svelte/store';

export interface GameState {
  board: any[][];
  currentPlayer: string;
  status: string;
  communityCards: string[];
  pot: number;
}

export interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  timestamp: number;
}

import { persisted } from 'svelte-local-storage-store';

export const gameStore = persisted<GameState>('gameStore', {
  board: [],
  currentPlayer: '',
  status: 'waiting',
  communityCards: [],
  pot: 0
});

export const chatStore = {
  messages: writable<ChatMessage[]>([]),
  addMessage: (message: ChatMessage) => {
    chatStore.messages.update(messages => [...messages, message]);
  }
};

// WebSocket连接管理
export const wsStore = (() => {
  const { subscribe, set } = writable<WebSocket | null>(null);
  let ws: WebSocket | null = null;

  const connect = () => {
    ws = new WebSocket(`ws://${import.meta.env.VITE_API_BASE_URL}/ws/game/default`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      set(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch(data.type) {
        case 'state_update':
          gameStore.set(data.state);
          break;
        case 'chat_message':
          chatStore.addMessage({
            sender: 'ai',
            text: data.message,
            timestamp: Date.now()
          });
          break;
        case 'game_action_result':
          gameStore.update(state => ({
            ...state,
            status: data.result.status
          }));
          break;
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      set(null);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const send = (data: any) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  };

  const disconnect = () => {
    if (ws) {
      ws.close();
      set(null);
    }
  };

  return {
    subscribe,
    connect,
    send,
    disconnect
  };
})();
