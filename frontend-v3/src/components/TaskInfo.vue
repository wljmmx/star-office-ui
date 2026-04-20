<template>
  <div class="task-info">
    <div class="task-title">{{ title }}</div>
    <div class="progress-bar">
      <div 
        class="progress-fill" 
        :style="{ width: progress + '%' }"
      ></div>
    </div>
    <div class="progress-text">
      {{ progress }}%
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  progress: {
    type: Number,
    default: 0
  }
})
</script>

<style scoped>
.task-info {
  background: var(--bg-secondary);
  padding: 10px;
  border-radius: 6px;
  margin-top: 10px;
}

.task-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.progress-bar {
  height: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--success));
  transition: width 0.5s ease;
}

.progress-text {
  text-align: right;
  margin-top: 5px;
  font-size: 0.9em;
  color: var(--text-secondary);
}
</style>
