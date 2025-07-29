<template>
  <div class="space-y-6">
    <!-- 顶部统计卡片 -->
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-blue-50">
            <DocumentTextIcon class="h-6 w-6 text-blue-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">主机数量</p>
            <p class="text-xl font-semibold">{{ dashboardStats.hosts_count || 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-green-50">
            <UserGroupIcon class="h-6 w-6 text-green-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">用户数量</p>
            <p class="text-xl font-semibold">{{ dashboardStats.users_count || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-purple-50">
            <ShieldCheckIcon class="h-6 w-6 text-purple-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">告警数量</p>
            <p class="text-xl font-semibold">{{ dashboardStats.alerts_count || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-orange-50">
            <ServerStackIcon class="h-6 w-6 text-orange-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">资产数量</p>
            <p class="text-xl font-semibold">{{ dashboardStats.assets_count || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 第二行统计 -->
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-cyan-50">
            <ChatBubbleLeftIcon class="h-6 w-6 text-cyan-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">在线会话</p>
            <p class="text-xl font-semibold">{{ dashboardStats.sessions_count || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-red-50">
            <ExclamationTriangleIcon class="h-6 w-6 text-red-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">失败登录</p>
            <p class="text-xl font-semibold">{{ dashboardStats.failed_logins || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-indigo-50">
            <ShieldExclamationIcon class="h-6 w-6 text-indigo-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">网站监控</p>
            <p class="text-xl font-semibold">{{ dashboardStats.sites_count || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 shadow-sm">
        <div class="flex items-center">
          <div class="p-2 rounded-lg bg-emerald-50">
            <CircleStackIcon class="h-6 w-6 text-emerald-500" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-gray-500">资产数据</p>
            <p class="text-xl font-semibold">{{ dashboardStats.asset_data_count || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-2 gap-4">
      <!-- 主机类型分布 -->
      <div class="bg-white rounded-lg p-6 shadow-sm">
        <h3 class="text-lg font-medium mb-4">主机类型分布</h3>
        <div class="h-64">
          <PieChart :data="hostTypeData" />
        </div>
      </div>

      <!-- 网站连通性占比 -->
      <div class="bg-white rounded-lg p-6 shadow-sm">
        <h3 class="text-lg font-medium mb-4">网站连通性占比</h3>
        <div class="h-64">
          <PieChart :data="connectivityData" />
        </div>
      </div>
    </div>

    <!-- 用户登录统计图 -->
    <div class="bg-white rounded-lg p-6 shadow-sm">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium">用户登录统计</h3>
        <div class="flex space-x-2">
          <button class="px-3 py-1 text-sm rounded-md" :class="{'bg-blue-50 text-blue-600': timeRange === '7'}" @click="timeRange = '7'">近7天</button>
          <button class="px-3 py-1 text-sm rounded-md" :class="{'bg-blue-50 text-blue-600': timeRange === '14'}" @click="timeRange = '14'">近14天</button>
          <button class="px-3 py-1 text-sm rounded-md" :class="{'bg-blue-50 text-blue-600': timeRange === '30'}" @click="timeRange = '30'">近30天</button>
        </div>
      </div>
      <div class="h-64">
        <LineChart :data="loginStatsData" />
      </div>
    </div>

    <!-- 最近登录失败记录 -->
    <div class="bg-white rounded-lg p-6 shadow-sm">
      <h3 class="text-lg font-medium mb-4">最近登录失败记录</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP地址</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">失败原因</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(record, index) in failedLoginRecords" :key="index">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ record.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ record.ip }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ record.reason }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ record.time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import {
  DocumentTextIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ServerStackIcon,
  ChatBubbleLeftIcon,
  ExclamationTriangleIcon,
  ShieldExclamationIcon,
  CircleStackIcon
} from '@heroicons/vue/24/outline'
import PieChart from './components/PieChart.vue'
import LineChart from './components/LineChart.vue'
import { fetchApi } from '@/utils/api'

const timeRange = ref('7')

// 响应式数据
const dashboardStats = ref({
  hosts_count: 0,
  users_count: 0,
  alerts_count: 0,
  assets_count: 0,
  sessions_count: 0,
  failed_logins: 0,
  sites_count: 0,
  asset_data_count: 0
})

const hostTypeData = ref([
  { name: 'Linux', value: 0 },
  { name: 'Windows', value: 0 }
])

const connectivityData = ref([
  { name: '正常', value: 0 },
  { name: '异常', value: 0 }
])

const loginStatsData = ref({
  labels: [],
  datasets: [{
    label: '登录次数',
    data: [],
    borderColor: '#3B82F6',
    tension: 0.4
  }]
})

const failedLoginRecords = ref([])

// 获取仪表板统计数据
const getDashboardStats = async () => {
  try {
    const response = await fetchApi('/dashboard/stats')
    if (response.success) {
      dashboardStats.value = response.data
    }
  } catch (error) {
    console.error('获取仪表板统计数据失败:', error)
    // 保持默认值，不显示错误弹窗
  }
}

// 获取主机类型分布
const getHostTypes = async () => {
  try {
    const response = await fetchApi('/dashboard/host-types')
    if (response.success) {
      hostTypeData.value = response.data
    }
  } catch (error) {
    console.error('获取主机类型分布失败:', error)
    // 保持默认值，不显示错误弹窗
  }
}

// 获取网站连通性统计
const getConnectivityStats = async () => {
  try {
    const response = await fetchApi('/dashboard/connectivity')
    if (response.success) {
      connectivityData.value = response.data
    }
  } catch (error) {
    console.error('获取网站连通性统计失败:', error)
    // 保持默认值，不显示错误弹窗
  }
}

// 获取登录统计数据
const getLoginStats = async () => {
  try {
    const response = await fetchApi(`/dashboard/login-stats?range=${timeRange.value}`)
    if (response.success) {
      loginStatsData.value = response.data
    }
  } catch (error) {
    console.error('获取登录统计数据失败:', error)
    // 保持默认值，不显示错误弹窗
  }
}

// 获取失败登录记录
const getFailedLogins = async () => {
  try {
    const response = await fetchApi('/dashboard/failed-logins')
    if (response.success) {
      failedLoginRecords.value = response.data
    }
  } catch (error) {
    console.error('获取失败登录记录失败:', error)
    // 保持默认值，不显示错误弹窗
  }
}

// 加载所有数据
const loadDashboardData = async () => {
  await Promise.all([
    getDashboardStats(),
    getHostTypes(),
    getConnectivityStats(),
    getLoginStats(),
    getFailedLogins()
  ])
}

// 监听时间范围变化
watch(timeRange, () => {
  getLoginStats()
})

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardData()
})
</script>

<script>
export default {
  name: 'Dashboard'
}
</script>