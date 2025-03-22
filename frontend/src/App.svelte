<script lang="ts">
import { Router, Route } from 'svelte-routing';
import Landing from './components/Landing.svelte';
import ChessBoard from './game/Chess/ChessBoard.svelte';
import GameSelector from './components/GameSelector.svelte';
import LLMAvatar from './components/LLMAvatar.svelte';
import { chatStore, wsStore } from './stores';
import { onMount } from 'svelte';
import { get } from 'svelte/store';

import type { ChatMessage } from './stores';

interface DebugInfo {
  serverStatus: string;
  lastRequest: string | null;
  requestCount: number;
  errors: string[];
}

let debugInfo: DebugInfo = {
  serverStatus: 'connecting...',
  lastRequest: null,
  requestCount: 0,
  errors: []
};

// Global error state
let globalError: {
  message: string;
  details?: string;
  timestamp: number;
} | null = null;

const showError = (message: string, details?: string) => {
  globalError = {
    message,
    details,
    timestamp: Date.now()
  };
  debugInfo.errors.push(`${new Date().toLocaleString()}: ${message} - ${details || 'No details'}`);
  console.error(message, details);
};

const clearError = () => {
  globalError = null;
};

const playVoice = (msg: ChatMessage): () => void => {
  return () => {
    console.log('Playing voice for:', msg);
  };
};

const toggleRecord = () => {
  isRecording = !isRecording;
  console.log('Recording:', isRecording);
};

let isRecording = false;
let isLoading = false;

// 获取调试信息
const fetchDebugInfo = async () => {
  try {
    const response = await fetch('/api/v1/status');
    if (response.ok) {
      const data = await response.json();
      debugInfo = {
        ...debugInfo,
        serverStatus: data.status,
        lastRequest: data.lastRequest,
        requestCount: data.requestCount,
        errors: data.errors
      };
    }
  } catch (err) {
    showError('获取调试信息失败', (err as Error).message);
  }
};

// 初始化WebSocket连接
onMount(() => {
  try {
    wsStore.connect();
    const interval = setInterval(fetchDebugInfo, 5000);
    return () => {
      wsStore.disconnect();
      clearInterval(interval);
    };
  } catch (err) {
    showError('WebSocket连接失败', (err as Error).message);
    return () => {};
  }
});

const startGame = async () => {
  try {
    isLoading = true;
    clearError();
    wsStore.send({ type: 'start_game' });
    isLoading = false;
  } catch (e) {
    showError('开始游戏失败', (e as Error).message);
    isLoading = false;
  }
};

$: chatMessages = get(chatStore.messages);
</script>

<Router>
  <Route path="/"><Landing /></Route>
  <Route path="/chess">
    <div class="container" role="main">
      <header>
        <GameSelector games={['中国象棋', '围棋', '斗地主']} />
        <LLMAvatar models={['Deepseek', 'GPT', '通义']} />
        <button 
          on:click={startGame}
          disabled={isLoading}
          aria-busy={isLoading}
        >
          {isLoading ? '连接中...' : '开始'}
        </button>
        <button 
          on:click={toggleRecord}
          aria-label={isRecording ? '停止录屏' : '开始录屏'}
        >
          {isRecording ? '停止录屏' : '开始录屏'}
        </button>
      </header>

      {#if globalError}
        <div class="error" role="alert">
          <h3>错误: {globalError.message}</h3>
          {#if globalError.details}
            <p>{globalError.details}</p>
          {/if}
          <button on:click={clearError}>关闭</button>
        </div>
      {/if}

      <div class="debug-panel">
        <h3>调试信息</h3>
        <div>服务器状态: {debugInfo.serverStatus}</div>
        <div>请求总数: {debugInfo.requestCount}</div>
        <div>最后请求: {debugInfo.lastRequest || '无'}</div>
        {#if debugInfo.errors.length > 0}
          <div class="errors">
            <h4>错误日志</h4>
            {#each debugInfo.errors as err, i}
              <div>{i + 1}. {err}</div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="main-panel">
        <ChessBoard />

        <div class="chat-panel" role="log" aria-live="polite">
          {#each chatMessages as msg}
            <div 
              class="message {msg.sender}"
              role="article"
              aria-label={`来自${msg.sender}的消息`}
            >
              <button 
                class="voice-icon" 
                on:click={playVoice(msg)}
                aria-label="播放语音"
              >
                🎤
              </button>
              {msg.text}
            </div>
          {/each}
        </div>
      </div>
    </div>
  </Route>
  <Route path="*">
    <div class="not-found">
      <h1>404 - 页面未找到</h1>
      <p>您访问的页面不存在，请检查URL是否正确</p>
      <a href="/">返回首页</a>
    </div>
  </Route>
</Router>

<style>
.error {
  background: #ffebee;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
  color: #c62828;
}

.debug-panel {
  background: #f5f5f5;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.errors {
  color: #d32f2f;
  margin-top: 0.5rem;
}
</style>
