import { ref, onMounted, onUnmounted } from 'vue'
import io from 'socket.io-client'

// Reconnection configuration
const RECONNECT_CONFIG = {
  INITIAL_DELAY: 1000,
  MAX_DELAY: 30000,
  BACKOFF_MULTIPLIER: 2,
  MAX_ATTEMPTS: -1,
  RANDOMIZATION_FACTOR: 0.5
}

export function useSocket() {
  const agents = ref([])
  const loading = ref(true)
  const isConnected = ref(false)
  const error = ref(null)
  const reconnectAttempts = ref(0)
  
  let socket = null
  let reconnectTimeout = null

  // Calculate reconnection delay with exponential backoff
  const calculateReconnectDelay = (attempt) => {
    const exponentialDelay = RECONNECT_CONFIG.INITIAL_DELAY * 
      Math.pow(RECONNECT_CONFIG.BACKOFF_MULTIPLIER, attempt)
    const randomizedDelay = exponentialDelay * 
      (1 + Math.random() * RECONNECT_CONFIG.RANDOMIZATION_FACTOR)
    return Math.min(randomizedDelay, RECONNECT_CONFIG.MAX_DELAY)
  }

  // Update connection status
  const updateStatus = (status) => {
    const statusTexts = {
      connected: '● 在线',
      disconnected: '○ 离线',
      reconnecting: '⟳ 重连中',
      error: '⚠ 错误'
    }
    return statusTexts[status] || '○ 离线'
  }

  // Clear error state
  const clearError = () => {
    error.value = null
  }

  // Initialize socket connection
  const connect = () => {
    if (socket) return

    socket = io({
      transports: ['websocket', 'polling'],
      upgrade: false,
      reconnection: true,
      reconnectionAttempts: RECONNECT_CONFIG.MAX_ATTEMPTS,
      reconnectionDelay: RECONNECT_CONFIG.INITIAL_DELAY,
      reconnectionDelayMax: RECONNECT_CONFIG.MAX_DELAY,
      randomizeReconnectionDelay: true
    })

    // Connection established
    socket.on('connect', () => {
      console.log('✅ Socket connected')
      isConnected.value = true
      reconnectAttempts.value = 0
      error.value = null
      
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
        reconnectTimeout = null
      }
      
      // Subscribe to agent updates
      socket.emit('subscribe_agents')
    })

    // Disconnection
    socket.on('disconnect', (reason) => {
      console.log('❌ Socket disconnected:', reason)
      isConnected.value = false
    })

    // Connection error
    socket.on('connect_error', (err) => {
      console.error('Socket error:', err)
      error.value = {
        message: '连接失败：' + err.message,
        attempt: reconnectAttempts.value
      }
    })

    // Reconnection attempt
    socket.on('reconnect_attempt', (attemptNumber) => {
      reconnectAttempts.value = attemptNumber
      const delay = calculateReconnectDelay(attemptNumber)
      console.log(`⟳ Reconnection attempt ${attemptNumber}, next in ${Math.round(delay)}ms`)
    })

    // Reconnection success
    socket.on('reconnect', (attemptNumber) => {
      console.log(`✅ Reconnected after ${attemptNumber} attempts`)
      reconnectAttempts.value = 0
      isConnected.value = true
      error.value = null
      
      // Resubscribe
      socket.emit('subscribe_agents')
    })

    // Reconnection failed
    socket.on('reconnect_failed', () => {
      console.error('❌ Reconnection failed after max attempts')
      error.value = {
        message: '重连失败，请刷新页面',
        attempt: reconnectAttempts.value
      }
    })

    // Agent updates
    socket.on('agents_update', (data) => {
      console.log(`🔄 Received ${data.agents?.length || 0} agents`)
      agents.value = data.agents || []
      loading.value = false
    })
  }

  // Fallback to REST API
  const fetchAgents = async () => {
    try {
      const response = await fetch('/v1/agents')
      const data = await response.json()
      if (data.ok && data.agents) {
        agents.value = data.agents
      }
      loading.value = false
    } catch (err) {
      console.error('Fetch agents failed:', err)
      error.value = {
        message: '获取 Agent 失败：' + err.message,
        attempt: 0
      }
      loading.value = false
    }
  }

  // Cleanup on unmount
  onUnmounted(() => {
    if (socket) {
      socket.disconnect()
      socket = null
    }
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
    }
  })

  return {
    agents,
    loading,
    isConnected,
    error,
    reconnectAttempts,
    connect,
    clearError,
    fetchAgents,
    updateStatus
  }
}
