<template>
  <div ref="chartContainer" class="w-full h-full"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const chartContainer = ref(null)
let chart = null

const initChart = () => {
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(chartContainer.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.data.labels
    },
    yAxis: {
      type: 'value'
    },
    series: props.data.datasets.map(dataset => ({
      name: dataset.label,
      type: 'line',
      data: dataset.data,
      smooth: true,
      lineStyle: {
        color: dataset.borderColor
      },
      itemStyle: {
        color: dataset.borderColor
      }
    }))
  }
  
  chart.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

watch(() => props.data, () => {
  initChart()
}, { deep: true })
</script> 