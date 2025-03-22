<script lang="ts">
  import { onMount } from 'svelte';
  import { gameStore } from '../../modules/core/stores';
  
  // Initialize game state
  onMount(() => {
    gameStore.set({
      board: Array(15).fill(Array(15).fill(null)), // 15x15 grid for Gomoku
      currentPlayer: '',
      status: 'waiting',
      lastUpdated: Date.now(),
      players: []
    });
  });
</script>

<div class="gomoku-board">
  <!-- Board rendering logic here -->
</div>

<style>
  .gomoku-board {
    display: grid;
    grid-template-columns: repeat(15, 1fr);
    grid-template-rows: repeat(15, 1fr);
    width: 450px;
    height: 450px;
  }
</style>
