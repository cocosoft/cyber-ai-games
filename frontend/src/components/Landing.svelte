<script>
  import { navigate } from 'svelte-routing';
</script>

<main>
  <h1>Welcome to Cyber AI Games</h1>
  <p>Select a game to play:</p>
  
  <div class="game-options">
    <button on:click={() => navigate('/chess')}>Chess</button>
    <button on:click={() => navigate('/go')}>Go</button>
  </div>

  <style>
    main {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
      text-align: center;
    }
    
    h1 {
      color: #2c3e50;
      margin-bottom: 2rem;
    }
    
    .game-options {
      display: flex;
      gap: 1rem;
      justify-content: center;
      margin-top: 2rem;
    }
    
    button {
      padding: 1rem 2rem;
      font-size: 1.2rem;
      border: none;
      border-radius: 4px;
      background: #3498db;
      color: white;
      cursor: pointer;
      transition: background 0.2s;
    }
    
    button:hover {
      background: #2980b9;
    }
  </style>
</main>
