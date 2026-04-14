<template>
  <div ref="chartRef" class="heatmap-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import client from '@/api/client'

const props = defineProps<{
  metricIds: number[]
  metricNames: string[]
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const loadData = async () => {
  if (!props.metricIds || props.metricIds.length < 2) {
    if (chart) {
      chart.clear()
    }
    return
  }

  try {
    const res = await client.post('/correlation', {
      metric_ids: props.metricIds
    })

    const matrix = res.data.matrix
    const data: [number, number, number][] = []

    for (let i = 0; i < matrix.length; i++) {
      for (let j = 0; j < matrix[i].length; j++) {
        data.push([j, i, matrix[i][j]])
      }
    }

    chart?.setOption({
      tooltip: { position: 'top' },
      grid: {
        height: '70%',
        top: '10%'
      },
      xAxis: { type: 'category', data: props.metricNames, axisLabel: { rotate: 30 } },
      yAxis: { type: 'category', data: props.metricNames },
      visualMap: {
        min: -1, max: 1,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: { color: ['#313695', '#4575b4', '#74add1', '#fee090', '#f46d43', '#d73027'] }
      },
      series: [{
        type: 'heatmap',
        data: data,
        label: { show: true, formatter: (p: any) => p.data[2].toFixed(2) }
      }]
    })
  } catch (error) {
    console.error('加载相关系数数据失败:', error)
  }
}

onMounted(() => {
  chart = echarts.init(chartRef.value!)
  loadData()

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

watch(() => props.metricIds, () => {
  loadData()
}, { deep: true })
</script>

<style scoped>
.heatmap-container {
  width: 100%;
  height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
