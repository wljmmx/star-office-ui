<template>
  <div class="error-notification slide-in">
    <div class="notification-content">
      <span class="notification-icon">⚠️</span>
      <div class="notification-text">
        <strong>{{ message }}</strong>
        <p v-if="attempt !== undefined">正在重连... (第 {{ attempt + 1 }} 次尝试)</p>
      </div>
      <button class="notification-close" @click="close" aria-label="关闭">
        ×
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  message: {
    type: String,
    required: true
  },
  attempt: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}
</script>

<style scoped>
.error-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 400px;
  background: var(--bg-card);
  border-left: 4px solid var(--danger);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  border-radius: 8px;
  padding: 15px;
  z-index: 1000;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.notification-icon {
  font-size: 1.5em;
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
  color: var(--text-primary);
}

.notification-text strong {
  display: block;
  margin-bottom: 4px;
}

.notification-text p {
  margin: 0;
  font-size: 0.9em;
  color: var(--text-secondary);
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5em;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.notification-close:hover {
  color: var(--text-primary);
}

.slide-in {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
