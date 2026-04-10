<template>
  <div class="metric-list">
    <h3>指标列表</h3>
    <ul>
      <li
        v-for="metric in metrics"
        :key="metric.id"
        :class="{ active: selectedId === metric.id }"
        @click="selectMetric(metric.id)"
      >
        {{ metric.name }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Metric } from '@/types'
import client from '@/api/client'

const metrics = ref<Metric[]>([])
const selectedId = ref<number | null>(null)
const emit = defineEmits<{ select: [id: number] }>()

onMounted(async () => {
  try {
    const res = await client.get<MetricsListResponse>('/metrics')
    metrics.value = res.data.metrics
  } catch (error) {
    console.error('加载指标列表失败:', error)
  }
})

const selectMetric = (id: number) => {
  selectedId.value = id
  emit('select', id)
}
</script>

<style scoped>
.metric-list {
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  min-width: 200px;
}

.metric-list h3 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #333;
}

.metric-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.metric-list li {
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.metric-list li:hover {
  background: #e0e7ff;
}

.metric-list li.active {
  background: #4f46e5;
  color: white;
}
</style>
