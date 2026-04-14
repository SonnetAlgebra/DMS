<template>
  <div class="dashboard">
    <aside class="sidebar">
      <DataUpload @uploadSuccess="refreshMetrics" />
      <MetricList
        @select="handleSelect"
        @toggle="handleToggle"
        :selectedId="selectedMetric"
        :selectedIds="selectedIds"
      />
    </aside>
    <main class="main-content">
      <div class="metric-cards">
        <MetricCard
          v-for="m in metrics"
          :key="m.id"
          :metric="m"
          :data="getMetricData(m.id)"
        />
      </div>
      <div class="chart-section">
        <div class="chart-controls" v-if="selectedMetric">
          <ThresholdSlider v-model="threshold" />
          <DetectButton
            :metricId="selectedMetric"
            :threshold="threshold"
            @detectComplete="handleDetectComplete"
          />
        </div>
        <div class="chart-container">
          <p v-if="!selectedMetric" class="placeholder">选择指标查看详情</p>
          <TimeSeriesChart
            v-else
            :data="getMetricData(selectedMetric)"
            :title="selectedMetricName"
          />
        </div>
      </div>
      <div class="heatmap-section" v-if="selectedIds.length >= 2">
        <h3>指标关联分析</h3>
        <HeatmapChart
          :metricIds="selectedIds"
          :metricNames="selectedNames"
        />
      </div>
      <AnomalyPanel
        v-if="selectedMetric"
        :metricId="selectedMetric"
        @anomalyDetected="handleAnomalyDetected"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import DataUpload from './DataUpload.vue'
import MetricList from './MetricList.vue'
import MetricCard from './MetricCard.vue'
import TimeSeriesChart from './TimeSeriesChart.vue'
import AnomalyPanel from './AnomalyPanel.vue'
import DetectButton from './DetectButton.vue'
import ThresholdSlider from './ThresholdSlider.vue'
import HeatmapChart from './HeatmapChart.vue'
import type { Metric, DataPoint, AnomalyPoint } from '@/types'
import client from '@/api/client'

const metrics = ref<Metric[]>([])
const selectedMetric = ref<number | null>(null)
const selectedIds = ref<number[]>([])
const metricsData = ref<Map<number, DataPoint[]>>(new Map())
const threshold = ref(3.0)

const selectedMetricName = computed(() => {
  const m = metrics.value.find(m => m.id === selectedMetric.value)
  return m?.name || ''
})

const selectedNames = computed(() => {
  return selectedIds.value.map(id => {
    const m = metrics.value.find(m => m.id === id)
    return m?.name || ''
  })
})

const getMetricData = (metricId: number): DataPoint[] => {
  return metricsData.value.get(metricId) || []
}

onMounted(async () => {
  try {
    const res = await client.get<MetricsListResponse>('/metrics')
    metrics.value = res.data.metrics
  } catch (error) {
    console.error('加载指标列表失败:', error)
  }
})

const handleSelect = async (id: number) => {
  selectedMetric.value = id

  // 如果没有加载过该指标的数据，则加载
  if (!metricsData.value.has(id)) {
    try {
      const res = await client.get<DataResponse>(`/metrics/${id}/data?limit=100`)
      metricsData.value.set(id, res.data.data)
    } catch (error) {
      console.error('加载指标数据失败:', error)
    }
  }
}

const handleToggle = (id: number) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const refreshMetrics = async () => {
  try {
    const res = await client.get<MetricsListResponse>('/metrics')
    metrics.value = res.data.metrics
  } catch (error) {
    console.error('刷新指标列表失败:', error)
  }
}

const handleAnomalyDetected = (anomalies: AnomalyPoint[]) => {
  console.log('检测到异常:', anomalies)
  // 可以在这里添加其他处理逻辑，比如发送通知
}

const handleDetectComplete = async (result: any) => {
  console.log('检测完成:', result)
  // 检测完成后重新加载当前指标的数据，以更新异常标记
  if (selectedMetric.value) {
    await handleSelect(selectedMetric.value)
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  gap: 1rem;
  min-height: calc(100vh - 60px);
}

.sidebar {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-cards {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.chart-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-controls .threshold-slider {
  flex: 1;
  min-width: 200px;
  max-width: 400px;
}

.chart-container {
  flex: 1;
  min-height: 400px;
}

.placeholder {
  color: #999;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.heatmap-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem;
}

.heatmap-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #333;
}
</style>
