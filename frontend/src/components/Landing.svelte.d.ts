import { SvelteComponent } from 'svelte';

export interface LandingProps {
  [key: string]: never; // No props expected
}

export default class Landing extends SvelteComponent<LandingProps> {}
