declare module './validators' {
  import type { GameState, ChatMessage } from './stores';
  
  export function validateGameState(state: GameState): boolean;
  export function validateChatMessage(message: ChatMessage): boolean;
}
