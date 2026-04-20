<template>
  <div class="container">
    <!-- Header -->
    <header class="header">
      <h1>🌟 Star Office UI</h1>
      <p>实时 Agent 监控系统 - Vue 3 + Vite</p>
    </header>
    
    <!-- Status Bar -->
    <div class="status-bar">
      <SocketStatus />
      <div class="agent-count">
        <span>Agent 数量：{{ agents.length }}</span>
      </div>
    </div>
    
    <!-- Error Notification -->
    <ErrorNotification 
      v-if="error" 
      :message="error.message" 
      :attempt="error.attempt"
      @close="clearError"
    />
    
    <!-- Loading State -->
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <!-- Agents Grid -->
    <div v-if="!loading && agents.length > 0" class="agents-grid">
      <AgentCard 
        v-for="agent in agents" 
        :key="agent.agentId" 
        :agent="agent"
      />
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && agents.length === 0" class="empty-state">
      暂无 Agent 数据
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSocket } from './composables/useSocket'
import AgentCard from './components/AgentCard.vue'
import TaskInfo from './components/TaskInfo.vue'
import SocketStatus from './components/SocketStatus.vue'
import ErrorNotification from './components/ErrorNotification.vue'

const { 
  agents, 
  loading, 
  error, 
  connect, 
  clearError: clearSocketError 
} = useSocket()

const clearError = () => {
  clearSocketError()
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.header h1 {
  color: var(--accent);
  margin-bottom: 10px;
  font-size: 2.5em;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: var(--bg-card);
  border-radius: 8px;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.loading, .empty-state {
  text-align: center;
  padding: 50px;
  color: var(--text-secondary);
}
</style>
