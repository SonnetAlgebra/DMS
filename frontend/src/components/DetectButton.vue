<template>
  <button
    @click="detect"
    :disabled="disabled || isDetecting"
    class="detect-button"
    :class="{ 'detecting': isDetecting }"
  >
    <span v-if="isDetecting" class="spinner"></span>
    <span class="text">{{ isDetecting ? '检测中...' : '检测异常' }}</span>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import client from '@/api/client'

const props = defineProps<{
  metricId: number | null
  threshold: number
  disabled?: boolean
}>()

const emit = defineEmits<{
  detectComplete: [result: DetectResult]
}>()

interface DetectResult {
  anomalies: Array<{
    timestamp: string
    value: number
    z_score: number
  }>
  count: number
  mean: number
  std: number
  threshold_used: number
}

const isDetecting = ref(false)

const detect = async () => {
  if (!props.metricId || props.disabled) return

  isDetecting.value = true

  try {
    const res = await client.post<DetectResult>('/metrics/detect', {
      metric_id: props.metricId,
      threshold: props.threshold
    })

    emit('detectComplete', res.data)
  } catch (error) {
    console.error('检测失败:', error)
    throw error
  } finally {
    isDetecting.value = false
  }
}
</script>

<style scoped>
.detect-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.detect-button:hover:not(:disabled) {
  background: #66b1ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.detect-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(64, 158, 255, 0.3);
}

.detect-button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
  opacity: 0.7;
}

.detect-button.detecting {
  background: #409eff;
  cursor: wait;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.text {
  white-space: nowrap;
}
</style>
