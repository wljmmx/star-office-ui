<template>
  <div 
    class="socket-status" 
    :class="'status-' + statusClass"
  >
    <span class="status-indicator" :class="{ pulse: isReconnecting }">
      {{ statusIcon }}
    </span>
    <span>{{ statusText }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSocket } from '../composables/useSocket'

const { isConnected, reconnectAttempts } = useSocket()

const statusClass = computed(() => {
  if (isConnected.value) return 'connected'
  if (reconnectAttempts.value > 0) return 'reconnecting'
  return 'disconnected'
})

const statusIcon = computed(() => {
  if (isConnected.value) return '●'
  if (reconnectAttempts.value > 0) return '⟳'
  return '○'
})

const statusText = computed(() => {
  if (isConnected.value) return '在线'
  if (reconnectAttempts.value > 0) return '重连中'
  return '离线'
})

const isReconnecting = computed(() => {
  return reconnectAttempts.value > 0
})
</script>

<style scoped>
.socket-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-card);
  border-radius: 20px;
  font-size: 0.9em;
}

.socket-status.status-connected { color: var(--success); }
.socket-status.status-disconnected { color: var(--danger); }
.socket-status.status-reconnecting { color: var(--warning); }
.socket-status.status-error { color: var(--danger); }

.status-indicator {
  font-size: 1.2em;
}

.status-indicator.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
