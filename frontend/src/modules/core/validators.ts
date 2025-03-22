import type { GameState, ChatMessage } from './stores';

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export function validateGameState(state: GameState): void {
  if (!Array.isArray(state.board)) {
    throw new ValidationError('Invalid board: must be an array');
  }
  if (typeof state.currentPlayer !== 'string') {
    throw new ValidationError('Invalid currentPlayer: must be a string');
  }
  if (!['waiting', 'playing', 'finished'].includes(state.status)) {
    throw new ValidationError(
      `Invalid status: must be one of 'waiting', 'playing', or 'finished'`
    );
  }
  if (typeof state.lastUpdated !== 'number') {
    throw new ValidationError('Invalid lastUpdated: must be a number');
  }
}

export function validateChatMessage(message: ChatMessage): void {
  if (!['user', 'ai'].includes(message.sender)) {
    throw new ValidationError(
      `Invalid sender: must be either 'user' or 'ai'`
    );
  }
  if (typeof message.text !== 'string') {
    throw new ValidationError('Invalid text: must be a string');
  }
  if (typeof message.timestamp !== 'number') {
    throw new ValidationError('Invalid timestamp: must be a number');
  }
}
