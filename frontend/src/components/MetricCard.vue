<template>
  <div class="metric-card">
    <div class="name">{{ metric.name }}</div>
    <div class="value">{{ displayValue }}</div>
    <div class="change" :class="trendClass">{{ trend }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Metric } from '@/types'

const props = defineProps<{
  metric: Metric
  data: { value: number | null }[]
}>()

const displayValue = computed(() => {
  const valid = props.data.filter(d => d.value !== null)
  return valid.length > 0 ? valid[valid.length - 1].value?.toFixed(2) || '-' : '-'
})

const trend = computed(() => {
  const valid = props.data.filter(d => d.value !== null)
  if (valid.length < 2) return '0%'

  const latest = valid[valid.length - 1].value
  const previous = valid[valid.length - 2].value

  if (latest === null || previous === null || previous === 0) return '0%'

  const change = ((latest - previous) / previous) * 100
  return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`
})

const trendClass = computed(() => {
  const t = trend.value
  if (t === '0%') return ''
  return t.startsWith('+') ? 'positive' : 'negative'
})
</script>

<style scoped>
.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-width: 200px;
}

.name {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.value {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.change {
  font-size: 0.9rem;
  font-weight: 500;
}

.change.positive {
  color: #10b981;
}

.change.negative {
  color: #ef4444;
}
</style>
