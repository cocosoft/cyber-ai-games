import { SvelteComponent } from 'svelte';

export interface GameSelectorProps {
  games: string[];
}

export default class GameSelector extends SvelteComponent<GameSelectorProps> {}
