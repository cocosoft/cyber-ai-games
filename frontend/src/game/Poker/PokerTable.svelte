<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { gameStore } from '../../stores';
  import { handleAction, initializeGame } from './PokerLogic';
  import type { GameState } from '../../stores';

  export const tableId = 'default-table';
  export const players: Player[] = [];

  interface Player {
    id: string;
    name: string;
    chips: number;
  }

  let gameState: GameState;
  let unsubscribe: () => void;

  onMount(() => {
    unsubscribe = gameStore.subscribe(value => {
      gameState = value;
    });
    initializeGame();
  });

  onDestroy(() => {
    unsubscribe();
  });
</script>

<div class="poker-table">
  <div class="community-cards">
    {#each gameState.communityCards as card}
      <div class="card">{card}</div>
    {/each}
  </div>
  
  <div class="pot">
    Pot: ${gameState.pot}
  </div>
  
  <div class="controls">
    <button on:click={() => handleAction('fold')}>Fold</button>
    <button on:click={() => handleAction('call')}>Call</button>
    <button on:click={() => handleAction('raise')}>Raise</button>
  </div>
</div>

<style>
  .poker-table {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 600px;
    height: 400px;
    background: green;
    border-radius: 50%;
  }

  .community-cards {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
  }

  .card {
    width: 50px;
    height: 70px;
    background: white;
    border: 1px solid black;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .pot {
    font-size: 1.2rem;
    margin-bottom: 20px;
    color: white;
  }

  .controls {
    display: flex;
    gap: 10px;
  }

  button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background: #007bff;
    color: white;
    cursor: pointer;
  }

  button:hover {
    background: #0056b3;
  }
</style>
