import { SvelteComponent } from 'svelte';

export interface LLMAvatarProps {
  models: string[];
}

export default class LLMAvatar extends SvelteComponent<LLMAvatarProps> {}
