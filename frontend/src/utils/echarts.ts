import * as echarts from 'echarts'

export const initChart = (dom: HTMLElement) => {
  return echarts.init(dom, undefined, {
    renderer: 'canvas'
  })
}

export const disposeChart = (chart: echarts.ECharts) => {
  chart.dispose()
}

export const resizeChart = (chart: echarts.ECharts) => {
  chart.resize()
}
