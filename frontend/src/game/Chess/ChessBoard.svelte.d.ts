import type { SvelteComponent } from 'svelte';

export interface ChessBoardProps {
  boardSize?: number;
  orientation?: 'white' | 'black';
  fen?: string;
  onMove?: (move: string) => void;
}

export default class ChessBoard extends SvelteComponent<ChessBoardProps> {}
