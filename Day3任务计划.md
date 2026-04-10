# Day 3 任务计划

---

## 任务概览

| 任务ID | 任务名称 | 交付物 | 验收标准 |
|--------|----------|--------|----------|
| **FE-01** | Vue3项目搭建 | 可运行的前端框架 | `npm run dev` 启动成功，页面可访问 |
| **FE-02** | 布局组件开发 | Dashboard.vue、MetricCard.vue | 基础布局渲染，指标卡片展示 |
| **FE-03** | 时序图表组件 | TimeSeriesChart.vue | ECharts渲染折线图，支持断点展示 |

---

## FE-01: Vue3项目搭建

**交付物**
- `frontend/package.json` - 项目配置
- `frontend/vite.config.ts` - Vite配置
- `frontend/src/main.ts` - 入口文件
- `frontend/src/App.vue` - 根组件
- `frontend/src/types/index.ts` - TypeScript类型定义

**技术栈确认**
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.3+ | 前端框架 |
| TypeScript | 5.0+ | 类型安全 |
| Vite | 5.0+ | 构建工具 |
| Bun | 1.0+ | 包管理器 |
| Axios | 1.6+ | HTTP请求 |
| ECharts | 5.4+ | 图表渲染（FE-03使用） |

**实施步骤**

**步骤1：初始化项目**
```bash
cd DMS/frontend
bun create vue@latest . --template typescript
# 选择：Vue 3 + TypeScript + Vite
```

**步骤2：安装依赖**
```bash
bun install
bun add axios echarts
bun add -D @types/node
```

**步骤3：配置Vite代理（vite.config.ts）**
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
```

**步骤4：创建类型定义（src/types/index.ts）**
```typescript
// 数据点类型
export interface DataPoint {
  timestamp: string
  value: number | null
  is_anomaly: boolean
  z_score: number
}

// 指标类型
export interface Metric {
  id: number
  name: string
  description?: string
  unit?: string
}

// API响应类型
export interface DataResponse {
  data: DataPoint[]
  mean: number
  std: number
  limit: number
  offset: number
  total: number
}
```

**步骤5：创建API客户端（src/api/client.ts）**
```typescript
import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

export default client
```

**验收标准**
- [ ] `bun run dev` 启动成功，无报错
- [ ] 浏览器访问 `http://localhost:5173` 显示Vue默认页面
- [ ] 网络面板确认代理配置生效（请求转发到8000端口）

---

## FE-02: 布局组件开发

**交付物**
- `frontend/src/App.vue` - 根布局（导航栏+主内容区）
- `frontend/src/components/Dashboard.vue` - Dashboard布局
- `frontend/src/components/MetricCard.vue` - 指标卡片组件
- `frontend/src/components/MetricList.vue` - 指标列表组件

**布局设计**
```
┌─────────────────────────────────────────┐
│  📊 DMS 数据监控系统          [设置]     │  ← Header
├─────────────────────────────────────────┤
│  ┌──────────┐  ┌─────────────────────┐ │
│  │ 指标列表  │  │    主内容区          │ │
│  │ - 日活跃  │  │  （时序图表/热力图）  │ │
│  │ - GMV    │  │                     │ │
│  │ ...      │  │                     │ │
│  └──────────┘  └─────────────────────┘ │
└─────────────────────────────────────────┘
```

**实施步骤**

**步骤1：实现指标列表组件（MetricList.vue）**
```vue
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
const emit = defineEmits(['select'])

onMounted(async () => {
  const res = await client.get('/metrics')
  metrics.value = res.data.metrics
})

const selectMetric = (id: number) => {
  selectedId.value = id
  emit('select', id)
}
</script>
```

**步骤2：实现指标卡片组件（MetricCard.vue）**
```vue
<template>
  <div class="metric-card">
    <div class="name">{{ metric.name }}</div>
    <div class="value">{{ latestValue }}</div>
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

const latestValue = computed(() => {
  const valid = props.data.filter(d => d.value !== null)
  return valid.length > 0 ? valid[valid.length - 1].value : '-'
})

const trend = computed(() => {
  // 简化：计算最近两个点的变化
  return '+0%'
})
</script>
```

**步骤3：实现Dashboard布局（Dashboard.vue）**
```vue
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
          :data="[]"
        />
      </div>
      <div class="chart-container">
        <!-- FE-03: 时序图表将放在这里 -->
        <p>选择指标查看详情</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MetricList from './MetricList.vue'
import MetricCard from './MetricCard.vue'
import type { Metric } from '@/types'

const metrics = ref<Metric[]>([])
const selectedMetric = ref<number | null>(null)

const handleSelect = (id: number) => {
  selectedMetric.value = id
}
</script>
```

**步骤4：更新App.vue**
```vue
<template>
  <header class="app-header">
    <h1>📊 DMS 数据监控系统</h1>
  </header>
  <main>
    <Dashboard />
  </main>
</template>

<script setup lang="ts">
import Dashboard from './components/Dashboard.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-header {
  background: #1a1a2e;
  color: white;
  padding: 1rem 2rem;
}

main {
  padding: 1rem;
}
</style>
```

**验收标准**
- [ ] 页面显示左侧指标列表，从后端 `/metrics` 接口加载
- [ ] 点击指标项，高亮显示并触发选择事件
- [ ] 顶部显示指标卡片区域（Mock数据或空状态）
- [ ] 布局响应式，适配不同屏幕宽度

---

## FE-03: 时序图表组件

**交付物**
- `frontend/src/components/TimeSeriesChart.vue` - 时序图表组件
- `frontend/src/utils/echarts.ts` - ECharts初始化工具

**核心功能**
| 功能 | 说明 |
|------|------|
| 折线图渲染 | 显示时序数据趋势 |
| 断点展示 | `value === null` 时断开连线（`connectNulls: false`） |
| 异常标记 | `is_anomaly === true` 时显示红色数据点 |
| 数据缩放 | 支持区域缩放（dataZoom） |
| 提示框 | 鼠标悬停显示详细数值 |

**实施步骤**

**步骤1：ECharts初始化工具（utils/echarts.ts）**
```typescript
import * as echarts from 'echarts'

export const initChart = (dom: HTMLElement) => {
  return echarts.init(dom, undefined, {
    renderer: 'canvas'
  })
}

export const disposeChart = (chart: echarts.ECharts) => {
  chart.dispose()
}
```

**步骤2：实现时序图表组件（TimeSeriesChart.vue）**
```vue
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
}

const updateChart = () => {
  if (!chart) return

  // 分离正常数据和异常数据
  const normalData = props.data.map(d => ({
    name: d.timestamp,
    value: [d.timestamp, d.value],
    itemStyle: { color: '#5470c6' }
  }))

  const anomalyData = props.data
    .filter(d => d.is_anomaly)
    .map(d => ({
      name: d.timestamp,
      value: [d.timestamp, d.value],
      itemStyle: { 
        color: '#ee6666',  // 红色标记异常
        borderWidth: 2,
        borderColor: '#ff0000'
      },
      symbolSize: 10  // 异常点放大
    }))

  const option: echarts.EChartsOption = {
    title: {
      text: props.title || '时序数据',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        const data = props.data[p.dataIndex]
        return `
          <div>时间: ${p.name}</div>
          <div>数值: ${data.value ?? 'N/A'}</div>
          <div>Z-Score: ${data.z_score.toFixed(2)}</div>
          ${data.is_anomaly ? '<div style="color:red">⚠️ 异常</div>' : ''}
        `
      }
    },
    xAxis: {
      type: 'time',
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      scale: true  // 不从0开始，自适应数据范围
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
        connectNulls: false,  // 关键：NULL值显示为断点
        smooth: false,
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: '异常点',
        type: 'scatter',
        data: anomalyData,
        symbol: 'circle'
      }
    ]
  }

  chart.setOption(option)
}

// 监听数据变化
watch(() => props.data, updateChart, { deep: true })

onMounted(initChart)
onUnmounted(() => {
  chart?.dispose()
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
```

**步骤3：Dashboard集成图表**
```vue
<!-- Dashboard.vue 更新 -->
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
          :data="chartData"
        />
      </div>
      <div class="chart-wrapper">
        <TimeSeriesChart 
          v-if="selectedMetric"
          :data="chartData"
          :title="selectedMetricName"
        />
        <p v-else class="placeholder">选择指标查看时序图</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import MetricList from './MetricList.vue'
import MetricCard from './MetricCard.vue'
import TimeSeriesChart from './TimeSeriesChart.vue'
import client from '@/api/client'
import type { Metric, DataPoint } from '@/types'

const metrics = ref<Metric[]>([])
const selectedMetric = ref<number | null>(null)
const chartData = ref<DataPoint[]>([])

const selectedMetricName = computed(() => {
  const m = metrics.value.find(m => m.id === selectedMetric.value)
  return m?.name || ''
})

const handleSelect = async (id: number) => {
  selectedMetric.value = id
  // 加载时序数据
  const res = await client.get(`/metrics/${id}/data?limit=1000`)
  chartData.value = res.data.data
}
</script>
```

**验收标准**
- [ ] 选择指标后，ECharts渲染折线图
- [ ] 数据中存在`null`时，图表显示断点（不连线）
- [ ] `is_anomaly=true`的数据点显示为红色大圆点
- [ ] 鼠标悬停显示tooltip，包含时间、数值、Z-Score、异常标记
- [ ] 支持滚轮缩放和底部滑块缩放

---

## Day 3 完成检查清单

| 检查项 | 标准 |
|--------|------|
| 项目启动 | `bun run dev` 启动成功，无报错 |
| 指标列表 | 从后端加载并显示所有指标 |
| 布局完整 | Header + Sidebar + MainContent 结构正确 |
| 图表渲染 | 选择指标后显示时序图，含断点和异常标记 |
| 数据流 | `/metrics/{id}/data` 接口数据正确渲染 |

**Day 3 完成后，准备进入 Day 4（E2E闭环交付）。**
