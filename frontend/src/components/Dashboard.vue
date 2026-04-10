<template>
  <div class="dashboard">
    <aside class="sidebar">
      <MetricList @select="handleSelect" />
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
      <div class="chart-container">
        <p v-if="!selectedMetric" class="placeholder">选择指标查看详情</p>
        <TimeSeriesChart
          v-else
          :data="getMetricData(selectedMetric)"
          :title="selectedMetricName"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import MetricList from './MetricList.vue'
import MetricCard from './MetricCard.vue'
import TimeSeriesChart from './TimeSeriesChart.vue'
import type { Metric, DataPoint } from '@/types'
import client from '@/api/client'

const metrics = ref<Metric[]>([])
const selectedMetric = ref<number | null>(null)
const metricsData = ref<Map<number, DataPoint[]>>(new Map())

const selectedMetricName = computed(() => {
  const m = metrics.value.find(m => m.id === selectedMetric.value)
  return m?.name || ''
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
</script>

<style scoped>
.dashboard {
  display: flex;
  gap: 1rem;
  min-height: calc(100vh - 60px);
}

.sidebar {
  flex-shrink: 0;
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
</style>
