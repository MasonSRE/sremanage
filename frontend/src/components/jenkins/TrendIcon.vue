<template>
  <span 
    v-if="trend && trend !== 'stable'" 
    class="inline-flex items-center"
    :class="getTrendColorClass()"
    :title="getTrendTooltip()"
  >
    <svg 
      :class="[
        size === 'xs' ? 'w-3 h-3' : 'w-4 h-4',
        trend === 'up' ? 'transform rotate-0' : 'transform rotate-180'
      ]"
      fill="currentColor" 
      viewBox="0 0 20 20"
    >
      <path 
        fill-rule="evenodd" 
        d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" 
        clip-rule="evenodd" 
      />
    </svg>
    <span 
      v-if="showChange && change !== null && change !== 0" 
      :class="[
        'ml-1 font-medium',
        size === 'xs' ? 'text-xs' : 'text-sm'
      ]"
    >
      {{ formatChange() }}
    </span>
  </span>
  
  <!-- 稳定状态指示器 -->
  <span 
    v-else-if="trend === 'stable'" 
    class="inline-flex items-center text-gray-400"
    :title="getTrendTooltip()"
  >
    <svg 
      :class="[
        size === 'xs' ? 'w-3 h-3' : 'w-4 h-4'
      ]"
      fill="currentColor" 
      viewBox="0 0 20 20"
    >
      <path 
        fill-rule="evenodd" 
        d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" 
        clip-rule="evenodd" 
      />
    </svg>
  </span>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  trend: {
    type: String,
    validator: (value) => !value || ['up', 'down', 'stable'].includes(value)
  },
  change: {
    type: Number,
    default: null
  },
  size: {
    type: String,
    default: 'sm',
    validator: (value) => ['xs', 'sm'].includes(value)
  },
  showChange: {
    type: Boolean,
    default: true
  },
  isPercentage: {
    type: Boolean,
    default: false
  }
})

// Methods
const getTrendColorClass = () => {
  switch (props.trend) {
    case 'up':
      return 'text-green-500'
    case 'down':
      return 'text-red-500'
    case 'stable':
      return 'text-gray-400'
    default:
      return 'text-gray-400'
  }
}

const getTrendTooltip = () => {
  if (!props.trend) return ''
  
  const trendText = {
    up: '上升',
    down: '下降',
    stable: '稳定'
  }[props.trend]
  
  if (props.change !== null && props.change !== 0) {
    const changeText = formatChange()
    return `${trendText} (${changeText})`
  }
  
  return trendText
}

const formatChange = () => {
  if (props.change === null || props.change === 0) return ''
  
  const absChange = Math.abs(props.change)
  const sign = props.change > 0 ? '+' : '-'
  
  if (props.isPercentage) {
    return `${sign}${absChange}%`
  }
  
  return `${sign}${absChange}`
}
</script>

<script>
export default {
  name: 'TrendIcon'
}
</script>

<style scoped>
/* 悬停效果 */
span:hover svg {
  transform: scale(1.1);
}

/* 动画过渡 */
svg {
  transition: transform 0.2s ease-in-out;
}
</style>