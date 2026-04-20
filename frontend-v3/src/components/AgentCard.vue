<template>
  <div class="agent-card">
    <div class="agent-header">
      <img 
        :src="avatarUrl" 
        alt="Avatar" 
        class="agent-avatar"
        @error="handleImageError"
      />
      <div class="agent-info">
        <h3>{{ agent.name }}</h3>
        <span class="agent-role">{{ agent.role || 'Agent' }}</span>
      </div>
    </div>
    
    <div class="agent-state" :class="'state-' + agent.state">
      {{ agent.state }}
    </div>
    
    <TaskInfo 
      v-if="agent.task_title" 
      :title="agent.task_title" 
      :progress="agent.task_progress"
    />
    
    <div class="updated-time">
      更新：{{ formattedTime }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import TaskInfo from './TaskInfo.vue'

const props = defineProps({
  agent: {
    type: Object,
    required: true
  }
})

const avatarUrl = computed(() => {
  return props.agent.avatar_url || 
    `https://api.dicebear.com/7.x/avataaars/svg?seed=${props.agent.agentId}`
})

const formattedTime = computed(() => {
  if (!props.agent.updated_at) return '-'
  const date = new Date(props.agent.updated_at)
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const handleImageError = (e) => {
  e.target.src = 'https://via.placeholder.com/50?text=?'
}
</script>

<style scoped>
.agent-card {
  background: var(--bg-card);
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  transition: transform 0.3s, box-shadow 0.3s;
}

.agent-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 12px rgba(0,0,0,0.4);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.agent-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 3px solid var(--accent);
}

.agent-info h3 {
  color: var(--text-primary);
  margin-bottom: 5px;
}

.agent-role {
  color: var(--text-secondary);
  font-size: 0.9em;
}

.agent-state {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: bold;
  margin-bottom: 10px;
}

.updated-time {
  color: var(--text-secondary);
  font-size: 0.8em;
  margin-top: 10px;
  text-align: right;
}
</style>
