<template>
  <div 
    class="status-card bg-white overflow-hidden shadow rounded-lg transition-all duration-200 hover:shadow-md cursor-pointer"
    :class="[
      size === 'sm' ? 'p-3' : 'p-5',
      animated ? 'animate-pulse-border' : ''
    ]"
    @click="$emit('click', { title, value })"
  >
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div :class="[
          'rounded-full flex items-center justify-center',
          size === 'sm' ? 'w-6 h-6' : 'w-8 h-8',
          getIconBackgroundClass()
        ]">
          <component 
            :is="getIconComponent()" 
            :class="[
              size === 'sm' ? 'w-3 h-3' : 'w-5 h-5',
              getIconColorClass()
            ]" 
          />
        </div>
      </div>
      
      <div class="ml-4 w-0 flex-1">
        <dl>
          <dt :class="[
            'font-medium text-gray-500 truncate',
            size === 'sm' ? 'text-xs' : 'text-sm'
          ]">
            {{ title }}
            <!-- 趋势指示器 -->
            <span v-if="trend && showTrend" class="ml-1">
              <TrendIcon 
                :trend="trend" 
                :change="change"
                :size="size === 'sm' ? 'xs' : 'sm'"
              />
            </span>
          </dt>
          <dd :class="[
            'font-medium',
            size === 'sm' ? 'text-base' : 'text-lg',
            getValueColorClass()
          ]">
            {{ value }}
          </dd>
        </dl>
        
        <!-- 进度条 -->
        <div v-if="showProgress" class="mt-2">
          <div class="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              class="h-1.5 rounded-full transition-all duration-500"
              :class="getProgressColorClass()"
              :style="{ width: `${Math.min(progressValue, 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CalendarIcon,
  ChartBarIcon
} from '@heroicons/vue/24/outline'
import TrendIcon from './TrendIcon.vue'

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    default: 'folder'
  },
  color: {
    type: String,
    default: 'blue',
    validator: (value) => ['blue', 'green', 'yellow', 'red', 'gray'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md'].includes(value)
  },
  animated: {
    type: Boolean,
    default: false
  },
  trend: {
    type: String,
    validator: (value) => !value || ['up', 'down', 'stable'].includes(value)
  },
  change: {
    type: Number
  },
  showTrend: {
    type: Boolean,
    default: true
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  progressValue: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['click'])

// Methods
const getIconComponent = () => {
  const iconMap = {
    folder: FolderIcon,
    clock: ClockIcon,
    check: CheckCircleIcon,
    exclamation: ExclamationTriangleIcon,
    calendar: CalendarIcon,
    chart: ChartBarIcon,
    building: ChartBarIcon, // 使用图表图标代表构建中
    time: ClockIcon
  }
  
  return iconMap[props.icon] || FolderIcon
}

const getIconBackgroundClass = () => {
  const colorMap = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    yellow: 'bg-yellow-100',
    red: 'bg-red-100',
    gray: 'bg-gray-100'
  }
  
  return colorMap[props.color] || colorMap.blue
}

const getIconColorClass = () => {
  const colorMap = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    red: 'text-red-600',
    gray: 'text-gray-600'
  }
  
  return colorMap[props.color] || colorMap.blue
}

const getValueColorClass = () => {
  if (props.color === 'red') return 'text-red-600'
  if (props.color === 'yellow') return 'text-yellow-600'
  if (props.color === 'green') return 'text-green-600'
  return 'text-gray-900'
}

const getProgressColorClass = () => {
  const colorMap = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    yellow: 'bg-yellow-600',
    red: 'bg-red-600',
    gray: 'bg-gray-600'
  }
  
  return colorMap[props.color] || colorMap.blue
}
</script>

<script>
export default {
  name: 'StatusCard'
}
</script>

<style scoped>
.status-card:hover {
  transform: translateY(-1px);
}

/* 构建中动画效果 */
@keyframes pulse-border {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  }
}

.animate-pulse-border {
  animation: pulse-border 2s infinite;
}

/* 响应式调整 */
@media (max-width: 640px) {
  .status-card {
    padding: 0.75rem;
  }
}
</style>