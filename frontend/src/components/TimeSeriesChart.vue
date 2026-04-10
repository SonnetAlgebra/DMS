<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { DataPoint } from '@/types'

const props = defineProps<{
  data: DataPoint[]
  title?: string
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChart()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

const updateChart = () => {
  if (!chart) return

  // 分离正常数据和异常数据
  const normalData = props.data.map((d, index) => ({
    name: d.timestamp,
    value: [d.timestamp, d.value],
    itemStyle: { color: '#5470c6' },
    dataIndex: index // 用于 tooltip 查找
  }))

  const anomalyData = props.data
    .filter(d => d.is_anomaly)
    .map((d, index) => ({
      name: d.timestamp,
      value: [d.timestamp, d.value],
      itemStyle: {
        color: '#ee6666', // 红色标记异常
        borderWidth: 2,
        borderColor: '#ff0000'
      },
      symbolSize: 10, // 异常点放大
      dataIndex: props.data.indexOf(d) // 用于 tooltip 查找
    }))

  const option: echarts.EChartsOption = {
    title: {
      text: props.title || '时序数据',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        if (!params || params.length === 0) return ''

        // 找到对应的数据点
        const dataIndex = (params[0] as any).dataIndex
        const data = props.data[dataIndex]

        if (!data) return ''

        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${data.timestamp}</div>
            <div>数值: ${data.value ?? 'N/A'}</div>
            <div>Z-Score: ${data.z_score.toFixed(2)}</div>
            ${data.is_anomaly ? '<div style="color: #ef4444; margin-top: 4px;">⚠️ 异常</div>' : ''}
          </div>
        `
      }
    },
    xAxis: {
      type: 'time',
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      scale: true // 不从0开始，自适应数据范围
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100 }
    ],
    series: [
      {
        name: '数值',
        type: 'line',
        data: normalData,
        connectNulls: false, // 关键：NULL值显示为断点
        smooth: false,
        symbol: 'circle',
        symbolSize: 6,
        showSymbol: false
      },
      {
        name: '异常点',
        type: 'scatter',
        data: anomalyData,
        symbol: 'circle',
        itemStyle: {
          color: '#ee6666',
          borderWidth: 2,
          borderColor: '#ff0000'
        },
        symbolSize: 10
      }
    ]
  }

  chart.setOption(option)
}

const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}

// 监听数据变化
watch(() => props.data, updateChart, { deep: true })

onMounted(initChart)

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
