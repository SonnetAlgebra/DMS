<template>
  <div class="anomaly-panel">
    <div class="panel-header">
      <h4>🔔 异常面板</h4>
      <div class="header-actions">
        <button
          @click="detectAnomalies"
          :disabled="!metricId || isDetecting"
          class="detect-btn"
        >
          {{ isDetecting ? '检测中...' : '检测异常' }}
        </button>
        <button
          @click="refreshAnomalies"
          :disabled="!metricId || isDetecting"
          class="refresh-btn"
        >
          🔄
        </button>
      </div>
    </div>

    <div v-if="!metricId" class="placeholder">
      <p>选择指标后可检测异常</p>
    </div>

    <div v-else-if="isLoading" class="loading">
      <p>加载中...</p>
    </div>

    <div v-else-if="!hasAnomalies" class="no-anomalies">
      <p>📊 当前无异常点</p>
      <p class="hint">点击"检测异常"开始分析</p>
    </div>

    <div v-else class="anomaly-list">
      <div class="anomaly-stats">
        <span class="count">共 {{ anomalies.length }} 个异常</span>
        <span class="threshold">阈值: {{ threshold }}</span>
      </div>

      <div
        v-for="anomaly in anomalies"
        :key="anomaly.timestamp"
        class="anomaly-item"
      >
        <div class="anomaly-info">
          <span class="timestamp">{{ formatTimestamp(anomaly.timestamp) }}</span>
          <span class="value">值: {{ anomaly.value }}</span>
          <span class="z-score" :class="{ 'high': anomaly.z_score > 5 }">
            Z: {{ anomaly.z_score.toFixed(2) }}
          </span>
        </div>
        <div class="anomaly-actions">
          <button
            @click="handleAcknowledge(anomaly)"
            :disabled="anomaly.acknowledged"
            :class="{ 'disabled': anomaly.acknowledged }"
            class="action-btn acknowledge"
          >
            {{ anomaly.acknowledged ? '✓ 已处理' : '标记处理' }}
          </button>
          <button
            @click="handleIgnore(anomaly)"
            :disabled="anomaly.ignored"
            :class="{ 'disabled': anomaly.ignored }"
            class="action-btn ignore"
          >
            {{ anomaly.ignored ? '✕ 已忽略' : '忽略' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="error">
      <p>❌ {{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { AnomalyPoint } from '@/types'
import client from '@/api/client'

interface AnomalyWithStatus extends AnomalyPoint {
  acknowledged?: boolean
  ignored?: boolean
}

const props = defineProps<{
  metricId: number | null
}>()

const emit = defineEmits<{
  anomalyDetected: [anomalies: AnomalyPoint[]]
}>()

const anomalies = ref<AnomalyWithStatus[]>([])
const isLoading = ref(false)
const isDetecting = ref(false)
const threshold = ref(3.0)
const error = ref<string | null>(null)

const hasAnomalies = computed(() => anomalies.value.length > 0)

// 监听 metricId 变化，加载异常列表
watch(() => props.metricId, (newId) => {
  if (newId) {
    fetchAnomalies()
  } else {
    anomalies.value = []
  }
})

const fetchAnomalies = async () => {
  if (!props.metricId) return

  isLoading.value = true
  error.value = null

  try {
    // 查询 anomalies 表（需要后端支持）
    // 暂时使用 detect 接口获取异常
    const res = await client.post<{
      anomalies: AnomalyPoint[]
      count: number
      mean: number
      std: number
      threshold_used: number
    }>('/metrics/detect', {
      metric_id: props.metricId,
      threshold: 3.0
    })

    threshold.value = res.data.threshold_used
    anomalies.value = res.data.anomalies.map(a => ({
      ...a,
      acknowledged: false,
      ignored: false
    }))

    if (res.data.anomalies.length > 0) {
      emit('anomalyDetected', res.data.anomalies)
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '加载异常失败'
  } finally {
    isLoading.value = false
  }
}

const detectAnomalies = async () => {
  if (!props.metricId) return

  isDetecting.value = true
  error.value = null

  try {
    const res = await client.post<{
      anomalies: AnomalyPoint[]
      count: number
      mean: number
      std: number
      threshold_used: number
    }>('/metrics/detect', {
      metric_id: props.metricId,
      threshold: 3.0
    })

    threshold.value = res.data.threshold_used
    anomalies.value = res.data.anomalies.map(a => ({
      ...a,
      acknowledged: false,
      ignored: false
    }))

    if (res.data.anomalies.length > 0) {
      emit('anomalyDetected', res.data.anomalies)
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '检测失败'
  } finally {
    isDetecting.value = false
  }
}

const refreshAnomalies = () => {
  fetchAnomalies()
}

const handleAcknowledge = (anomaly: AnomalyWithStatus) => {
  anomaly.acknowledged = !anomaly.acknowledged
  if (anomaly.acknowledged) {
    anomaly.ignored = false
  }
}

const handleIgnore = (anomaly: AnomalyWithStatus) => {
  anomaly.ignored = !anomaly.ignored
  if (anomaly.ignored) {
    anomaly.acknowledged = false
  }
}

const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.anomaly-panel {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 300px;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-header h4 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.detect-btn {
  padding: 0.5rem 1rem;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.detect-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.detect-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.refresh-btn {
  padding: 0.5rem 0.75rem;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #e0e0e0;
}

.refresh-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.placeholder,
.loading,
.no-anomalies {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  text-align: center;
}

.placeholder p,
.loading p,
.no-anomalies p {
  margin: 0.25rem 0;
}

.hint {
  font-size: 0.85rem;
}

.anomaly-list {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.anomaly-stats {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.count {
  color: #f56c6c;
  font-weight: 500;
}

.threshold {
  color: #666;
}

.anomaly-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #fffbfb;
  border-left: 3px solid #f56c6c;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.anomaly-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex: 1;
}

.timestamp {
  color: #333;
  font-size: 0.9rem;
}

.value {
  color: #666;
  font-size: 0.9rem;
}

.z-score {
  padding: 0.2rem 0.5rem;
  background: #ffe6e6;
  color: #f56c6c;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.z-score.high {
  background: #ffcccc;
  font-weight: 600;
}

.anomaly-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.4rem 0.8rem;
  border: 1px solid;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.action-btn.acknowledge {
  background: white;
  border-color: #67c23a;
  color: #67c23a;
}

.action-btn.acknowledge:hover:not(.disabled) {
  background: #e1f3d8;
}

.action-btn.ignore {
  background: white;
  border-color: #909399;
  color: #909399;
}

.action-btn.ignore:hover:not(.disabled) {
  background: #f4f4f5;
}

.action-btn.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.error {
  padding: 1rem;
  background: #fff0f0;
  color: #f00;
  border-radius: 4px;
  text-align: center;
}

.error p {
  margin: 0;
}
</style>
