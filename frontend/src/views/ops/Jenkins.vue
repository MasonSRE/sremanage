<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面标题栏 -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-900 flex items-center">
            🏗️ Jenkins管理 - 运维控制中心
          </h1>
          <div class="ml-8">
            <JenkinsInstanceSelector
              v-model="selectedInstance"
              @change="onInstanceChange"
              @add="addNewInstance"
              show-status
              show-stats
              class="max-w-lg"
            />
          </div>
        </div>
        
        <!-- 快捷操作区 -->
        <div class="flex items-center space-x-3">
          <button 
            @click="refreshData"
            :disabled="!selectedInstance || isLoading('refresh')"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <svg v-if="isLoading('refresh')" class="animate-spin -ml-1 mr-1 h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            🔄 刷新
          </button>
          <button 
            @click="toggleAutoRefresh"
            :disabled="!selectedInstance"
            :class="[
              'inline-flex items-center px-3 py-2 border shadow-sm text-sm leading-4 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50',
              autoRefresh 
                ? 'border-green-300 text-green-700 bg-green-50 hover:bg-green-100' 
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
            ]"
          >
            {{ autoRefresh ? '⚡ 自动刷新(开)' : '⚡ 自动刷新(关)' }}
          </button>
          <button 
            @click="addNewInstance"
            class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            ➕ 添加实例
          </button>
        </div>
      </div>
    </div>

    <div class="px-6 py-6 space-y-6">

      <!-- 统计卡片区 & 快捷操作区 & 状态监控区 -->
      <div v-if="selectedInstance" class="space-y-6">
        <!-- 状态统计卡片 -->
        <JenkinsStatusCards
          :stats="statusSummary"
          :loading="statusLoading"
          :show-extended="true"
          :show-trends="true"
          :auto-refresh="autoRefresh"
          @refresh="refreshData"
          @card-click="handleCardClick"
        />

        <!-- 快捷操作栏 -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-3 sm:px-6">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
              <div class="flex items-center space-x-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">快捷操作</h3>
                <div class="flex items-center space-x-2">
                  <button 
                    @click="batchHealthCheck"
                    :disabled="!selectedInstance || isLoading('health-check')"
                    class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    <svg v-if="isLoading('health-check')" class="animate-spin -ml-1 mr-1 h-3 w-3 text-gray-600" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    🏥 健康检查
                  </button>
                  <button 
                    @click="openBatchBuildDialog"
                    :disabled="!selectedInstance || jobs.length === 0 || isLoading('batch-build')"
                    class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    <svg v-if="isLoading('batch-build')" class="animate-spin -ml-1 mr-1 h-3 w-3 text-gray-600" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    🚀 批量构建
                  </button>
                  <button 
                    @click="openLogViewerDialog"
                    :disabled="!selectedInstance"
                    class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    📜 日志查看
                  </button>
                  <button 
                    @click="openViewManagementDialog"
                    :disabled="!selectedInstance"
                    class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    📁 视图管理
                  </button>
                </div>
              </div>
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <!-- 连接状态指示器 -->
                <div class="flex items-center space-x-1">
                  <div :class="[
                    'w-2 h-2 rounded-full',
                    connectionStatus === 'connected' ? 'bg-green-400' : 
                    connectionStatus === 'connecting' ? 'bg-yellow-400 animate-pulse' : 'bg-red-400'
                  ]"></div>
                  <span>{{ 
                    connectionStatus === 'connected' ? '已连接' : 
                    connectionStatus === 'connecting' ? '连接中' : '连接断开'
                  }}</span>
                </div>
                
                <span>最后更新: {{ lastUpdateTime || '未更新' }}</span>
                
                <div v-if="autoRefresh" class="flex items-center space-x-1">
                  <span>更新: {{ updateCounter }}</span>
                </div>
                
                <div class="hidden xl:flex items-center space-x-1">
                  <span>快捷键:</span>
                  <span class="inline-flex items-center px-1 py-0.5 rounded text-xs bg-gray-200 text-gray-700" title="刷新数据">F5</span>
                  <span class="inline-flex items-center px-1 py-0.5 rounded text-xs bg-gray-200 text-gray-700" title="批量构建">Ctrl+B</span>
                  <span class="inline-flex items-center px-1 py-0.5 rounded text-xs bg-gray-200 text-gray-700" title="快速搜索">Ctrl+K</span>
                  <span class="inline-flex items-center px-1 py-0.5 rounded text-xs bg-gray-200 text-gray-700" title="健康检查">Ctrl+T</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Phase 3 分析面板 -->
        <div v-if="selectedInstance" class="space-y-6">
          <!-- 分析功能选项卡 -->
          <div class="bg-white shadow rounded-lg">
            <div class="border-b border-gray-200">
              <nav class="flex space-x-8 px-6" aria-label="Tabs">
                <button
                  @click="activeAnalyticsTab = 'performance'"
                  :class="[
                    'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                    activeAnalyticsTab === 'performance'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  📊 性能监控
                </button>
                <button
                  @click="activeAnalyticsTab = 'trends'"
                  :class="[
                    'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                    activeAnalyticsTab === 'trends'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  📈 趋势分析
                </button>
                <button
                  @click="activeAnalyticsTab = 'history'"
                  :class="[
                    'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                    activeAnalyticsTab === 'history'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  📋 构建分析
                </button>
                <button
                  @click="activeAnalyticsTab = 'prediction'"
                  :class="[
                    'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                    activeAnalyticsTab === 'prediction'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  🔮 智能预测
                </button>
                <button
                  @click="activeAnalyticsTab = 'failure'"
                  :class="[
                    'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                    activeAnalyticsTab === 'failure'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  🔍 失败分析
                </button>
                <button
                  @click="activeAnalyticsTab = 'optimization'"
                  :class="[
                    'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                    activeAnalyticsTab === 'optimization'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  ⚡ 优化建议
                </button>
              </nav>
            </div>
            
            <!-- 分析面板内容 -->
            <div class="p-6">
              <!-- 性能监控面板 -->
              <div v-show="activeAnalyticsTab === 'performance'">
                <PerformanceMetrics :instance-id="selectedInstance" />
              </div>
              
              <!-- 趋势分析面板 -->
              <div v-show="activeAnalyticsTab === 'trends'">
                <BuildTrendsChart :instance-id="selectedInstance" />
              </div>
              
              <!-- 构建历史分析面板 -->
              <div v-show="activeAnalyticsTab === 'history'">
                <BuildHistoryAnalytics :instance-id="selectedInstance" />
              </div>
              
              <!-- Phase 4: 智能预测面板 -->
              <div v-show="activeAnalyticsTab === 'prediction'">
                <BuildPredictionAnalysis 
                  :instance-id="selectedInstance" 
                  :available-jobs="jobs.map(job => job.name)"
                />
              </div>
              
              <!-- Phase 4: 失败分析面板 -->
              <div v-show="activeAnalyticsTab === 'failure'">
                <FailureAnalysis 
                  :instance-id="selectedInstance" 
                  :available-jobs="jobs.map(job => job.name)"
                />
              </div>
              
              <!-- Phase 4: 优化建议面板 -->
              <div v-show="activeAnalyticsTab === 'optimization'">
                <OptimizationRecommendations :instance-id="selectedInstance" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 任务列表区域 -->
      <div v-if="filteredJobs.length > 0 || selectedInstance" class="bg-white shadow rounded-lg">
        <!-- 列表头部 -->
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div class="flex items-center space-x-4">
              <h2 class="text-xl font-semibold text-gray-900">🗂️ 任务列表</h2>
              <div v-if="selectedJobs.length > 0" class="flex items-center space-x-3 bg-blue-50 px-3 py-1 rounded-full">
                <span class="text-sm font-medium text-blue-700">已选择 {{ selectedJobs.length }} 个任务</span>
                <button 
                  @click="batchBuild"
                  :disabled="isLoading('batch-build')"
                  class="inline-flex items-center px-2 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg v-if="isLoading('batch-build')" class="animate-spin -ml-1 mr-1 h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  🚀 批量构建
                </button>
                <button 
                  @click="clearSelection"
                  class="inline-flex items-center px-2 py-1 bg-gray-500 text-white text-xs font-medium rounded hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  清除
                </button>
              </div>
            </div>
            
            <!-- 搜索和筛选 -->
            <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                  </svg>
                </div>
                <input 
                  type="text"
                  v-model="searchQuery"
                  placeholder="🔍 搜索任务..."
                  class="block w-full sm:w-64 pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                >
              </div>
              
              <select 
                v-model="statusFilter"
                class="block w-full sm:w-32 px-3 py-2 border border-gray-300 bg-white rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">🏷️ 全部状态</option>
                <option value="success">✅ 成功</option>
                <option value="failure">❌ 失败</option>
                <option value="building">🟡 构建中</option>
                <option value="unknown">❓ 未知</option>
              </select>
              
              <select 
                v-model="selectedView"
                class="block w-full sm:w-32 px-3 py-2 border border-gray-300 bg-white rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">📁 全部视图</option>
                <option v-for="view in jenkinsViews" :key="view.name" :value="view.name">{{ view.name }}</option>
              </select>
              
              <select 
                v-model="viewMode"
                class="block w-full sm:w-28 px-3 py-2 border border-gray-300 bg-white rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="table">👁️ 表格</option>
                <option value="card">📋 卡片</option>
              </select>
            </div>
          </div>
        </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">任务名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后构建</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">持续时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="job in filteredJobs" :key="job.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  :value="job.name"
                  v-model="selectedJobs"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <component 
                      :is="getJobIcon(job.type)"
                      class="h-5 w-5 text-gray-500"
                    />
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ job.name }}</div>
                    <div class="text-sm text-gray-500">{{ job.description }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">#{{ job.lastBuildNumber }}</div>
                <div class="text-sm text-gray-500">{{ job.lastBuildTime }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  getStatusClass(job.status)
                ]">
                  {{ getStatusText(job.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ job.duration }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button 
                  @click="triggerBuild(job)"
                  :disabled="isLoading(`build-${job.name}`)"
                  class="text-blue-600 hover:text-blue-900 mr-3 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center"
                >
                  <svg v-if="isLoading(`build-${job.name}`)" class="animate-spin -ml-1 mr-1 h-3 w-3 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  构建
                </button>
                <button 
                  @click="viewLogs(job)"
                  class="text-purple-600 hover:text-purple-900 mr-3"
                >
                  日志
                </button>
                <button 
                  @click="viewDetails(job)"
                  class="text-green-600 hover:text-green-900 mr-3"
                >
                  详情
                </button>
                <button 
                  @click="showConfig(job)"
                  class="text-gray-600 hover:text-gray-900"
                >
                  配置
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
        
        <!-- 构建历史 -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 class="text-lg leading-6 font-medium text-gray-900">📈 最近构建历史</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">最新50条构建记录</p>
          </div>
          <div class="px-4 py-5 sm:p-6">
            <div v-if="buildHistory.length === 0" class="text-center py-8 text-gray-500">
              暂无构建历史记录
            </div>
            <div v-else class="space-y-3">
              <div v-for="build in buildHistory.slice(0, 10)" :key="build.id" 
                   class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div class="flex items-center space-x-3">
                  <div :class="[
                    'status-indicator',
                    build.status === 'success' ? 'status-success' : 
                    build.status === 'failure' ? 'status-failure' : 
                    build.status === 'building' ? 'status-building' : 'status-unknown'
                  ]"></div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ build.jobName }} #{{ build.number }}
                    </div>
                    <div class="text-xs text-gray-500">
                      by {{ build.triggeredBy }} • {{ build.startTime }}
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-xs text-gray-500">{{ build.duration }}</span>
                  <span :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    build.status === 'success' ? 'bg-green-100 text-green-800' : 
                    build.status === 'failure' ? 'bg-red-100 text-red-800' : 
                    build.status === 'building' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
                  ]">
                    {{ getStatusText(build.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态提示 -->
      <div v-else class="text-center py-12">
        <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">选择Jenkins实例</h3>
        <p class="text-gray-500 mb-4">请先选择一个Jenkins实例来查看任务和状态信息</p>
        <button 
          @click="addNewInstance"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          ➕ 添加第一个Jenkins实例
        </button>
      </div>
    </div>

  <!-- 添加Jenkins实例对话框 -->
  <TransitionRoot appear :show="showAddDialog" as="template">
    <Dialog as="div" @close="showAddDialog = false" class="relative z-10">
      <TransitionChild
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                添加Jenkins实例
              </DialogTitle>

              <div class="mt-4 space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">实例名称</label>
                  <input 
                    type="text"
                    v-model="newInstance.name"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Jenkins URL</label>
                  <input 
                    type="text"
                    v-model="newInstance.url"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">用户名</label>
                  <input 
                    type="text"
                    v-model="newInstance.username"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">API Token</label>
                  <input 
                    type="password"
                    v-model="newInstance.token"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
              </div>

              <div class="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  @click="showAddDialog = false"
                >
                  取消
                </button>
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-transparent bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  @click="saveNewInstance"
                >
                  保存
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- 日志查看对话框 -->
  <TransitionRoot appear :show="showLogDialog" as="template">
    <Dialog as="div" @close="showLogDialog = false" class="relative z-10">
      <TransitionChild
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
              <div class="p-6">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                  构建日志 - {{ currentLogJob?.name }} #{{ currentLogJob?.lastBuildNumber }}
                </DialogTitle>

                <!-- 日志控制栏 -->
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center space-x-4">
                    <button 
                      @click="refreshLog"
                      class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                    >
                      刷新日志
                    </button>
                    <button 
                      @click="downloadLog"
                      class="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                    >
                      下载日志
                    </button>
                  </div>
                  <div class="flex items-center space-x-2">
                    <input 
                      type="text"
                      v-model="logSearchQuery"
                      placeholder="搜索日志..."
                      class="block w-64 text-sm rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                    <select 
                      v-model="logLevelFilter"
                      class="block text-sm rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">全部级别</option>
                      <option value="ERROR">错误</option>
                      <option value="WARN">警告</option>
                      <option value="INFO">信息</option>
                      <option value="DEBUG">调试</option>
                    </select>
                  </div>
                </div>

                <!-- 日志内容 -->
                <div class="bg-black text-green-400 p-4 rounded-lg h-96 overflow-y-auto font-mono text-sm">
                  <div v-if="isLoading('fetch-log')" class="text-center text-gray-500 flex items-center justify-center h-full">
                    <div class="flex items-center space-x-2">
                      <svg class="animate-spin h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>加载日志中...</span>
                    </div>
                  </div>
                  <div v-else-if="!logContent" class="text-center text-gray-500">
                    暂无日志内容
                  </div>
                  <pre v-else class="whitespace-pre-wrap">{{ filteredLogContent }}</pre>
                </div>

                <div class="mt-6 flex justify-end">
                  <button
                    type="button"
                    class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    @click="showLogDialog = false"
                  >
                    关闭
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
  </div>

  <!-- 视图管理对话框 -->
  <TransitionRoot appear :show="showViewDialog" as="template">
    <Dialog as="div" @close="showViewDialog = false" class="relative z-10">
      <TransitionChild
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
              <div class="p-6">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                  Jenkins视图管理
                </DialogTitle>

                <!-- 创建新视图表单 -->
                <div class="mb-6 bg-gray-50 p-4 rounded-lg">
                  <h4 class="text-sm font-medium text-gray-900 mb-3">创建新视图</h4>
                  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">视图名称</label>
                      <input 
                        type="text"
                        v-model="viewForm.name"
                        placeholder="输入视图名称"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">视图描述</label>
                      <input 
                        type="text"
                        v-model="viewForm.description"
                        placeholder="输入视图描述"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                    </div>
                  </div>
                  <div class="mt-4">
                    <label class="block text-sm font-medium text-gray-700">选择任务</label>
                    <div class="mt-1 max-h-32 overflow-y-auto border border-gray-300 rounded-md p-2">
                      <div v-for="job in jobs" :key="job.name" class="flex items-center">
                        <input 
                          type="checkbox"
                          :id="`job-${job.name}`"
                          :value="job.name"
                          v-model="viewForm.jobNames"
                          class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        >
                        <label :for="`job-${job.name}`" class="ml-2 text-sm text-gray-700">{{ job.name }}</label>
                      </div>
                    </div>
                  </div>
                  <div class="mt-4 flex justify-end">
                    <button
                      @click="createJenkinsView"
                      :disabled="isLoading('create-view')"
                      class="inline-flex justify-center rounded-md border border-transparent bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                    >
                      <svg v-if="isLoading('create-view')" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      创建视图
                    </button>
                  </div>
                </div>

                <!-- 现有视图列表 -->
                <div>
                  <h4 class="text-sm font-medium text-gray-900 mb-3">现有视图</h4>
                  <div v-if="jenkinsViews.length === 0" class="text-center py-8 text-gray-500">
                    暂无视图，请创建新视图
                  </div>
                  <div v-else class="space-y-3">
                    <div v-for="view in jenkinsViews" :key="view.name" 
                         class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                      <div>
                        <div class="font-medium text-gray-900">{{ view.name }}</div>
                        <div class="text-sm text-gray-500">{{ view.description || '无描述' }} - {{ view.jobs?.length || 0 }} 个任务</div>
                      </div>
                      <div class="flex space-x-2">
                        <button
                          @click="deleteJenkinsView(view.name)"
                          :disabled="isLoading('delete-view')"
                          class="text-red-600 hover:text-red-900 text-sm disabled:opacity-50"
                        >
                          删除
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mt-6 flex justify-end">
                  <button
                    type="button"
                    class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    @click="showViewDialog = false"
                  >
                    关闭
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- 配置编辑对话框 -->
  <TransitionRoot appear :show="showConfigDialog" as="template">
    <Dialog as="div" @close="showConfigDialog = false" class="relative z-10">
      <TransitionChild
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-6xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
              <div class="p-6">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                  编辑任务配置 - {{ currentConfigJob?.name }}
                </DialogTitle>

                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-2">任务显示名称</label>
                  <input 
                    type="text"
                    v-model="jobConfig.displayName"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>

                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-2">任务描述</label>
                  <textarea 
                    v-model="jobConfig.description"
                    rows="3"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  ></textarea>
                </div>

                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-2">XML配置</label>
                  <textarea 
                    ref="configEditor"
                    v-model="jobConfig.xml"
                    rows="20"
                    class="block w-full font-mono text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    spellcheck="false"
                  ></textarea>
                </div>

                <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
                  <div class="flex">
                    <div class="flex-shrink-0">
                      <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                      </svg>
                    </div>
                    <div class="ml-3">
                      <p class="text-sm text-yellow-700">
                        警告：直接编辑XML配置可能导致任务无法正常运行。请确保您了解配置格式后再进行修改。
                      </p>
                    </div>
                  </div>
                </div>

                <div class="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    @click="showConfigDialog = false"
                  >
                    取消
                  </button>
                  <button
                    @click="updateJobConfig"
                    :disabled="isLoading('update-config')"
                    class="inline-flex justify-center rounded-md border border-transparent bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                  >
                    <svg v-if="isLoading('update-config')" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    保存配置
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { 
  FolderIcon, 
  PlayIcon, 
  CogIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'
import { fetchApi } from '@/utils/api'
import TimerManager from '@/utils/timer-manager'
import { notify } from '@/utils/notification'
import { useLoading } from '@/utils/loading-manager'
import { 
  performanceMonitor, 
  debounce, 
  throttle,
  cacheManager,
  useErrorBoundary 
} from '@/utils/performance-optimizer'
import JenkinsInstanceSelector from '@/components/jenkins/JenkinsInstanceSelector.vue'
import JenkinsStatusCards from '@/components/jenkins/JenkinsStatusCards.vue'
import BuildHistoryAnalytics from '@/components/jenkins/BuildHistoryAnalytics.vue'
import BuildTrendsChart from '@/components/jenkins/BuildTrendsChart.vue'
import PerformanceMetrics from '@/components/jenkins/PerformanceMetrics.vue'
import BuildPredictionAnalysis from '@/components/jenkins/BuildPredictionAnalysis.vue'  
import FailureAnalysis from '@/components/jenkins/FailureAnalysis.vue'
import OptimizationRecommendations from '@/components/jenkins/OptimizationRecommendations.vue'

// 状态管理
const selectedInstance = ref('')
const searchQuery = ref('')
const statusFilter = ref('')
const selectedView = ref('')
const showAddDialog = ref(false)
const showViewDialog = ref(false)
const showConfigDialog = ref(false)
const autoRefresh = ref(false)
const refreshInterval = ref(null)
const timerManager = new TimerManager()

// 性能优化和错误处理
const { error, errorInfo, catchError, clearError } = useErrorBoundary()
const debouncedSearch = debounce((value) => {
  searchQuery.value = value
}, 300)

// Loading状态管理
const {
  setLoading,
  isLoading,
  withLoading,
  withBatchLoading,
  debounce: loadingDebounce,
  throttle: loadingThrottle
} = useLoading('jenkins')
const newInstance = ref({
  name: '',
  url: '',
  username: '',
  token: ''
})

// 日志相关状态
const showLogDialog = ref(false)
const currentLogJob = ref(null)
const logContent = ref('')
const logSearchQuery = ref('')
const logLevelFilter = ref('')

// 视图管理相关状态
const jenkinsViews = ref([])
const currentView = ref(null)
const viewForm = ref({
  name: '',
  description: '',
  jobNames: []
})

// 配置编辑相关状态
const currentConfigJob = ref(null)
const jobConfig = ref({
  xml: '',
  displayName: '',
  description: ''
})
const configEditor = ref(null)

// 批量操作相关状态
const selectedJobs = ref([])
const batchOperationInProgress = ref(false)

// UI状态
const viewMode = ref('table') // 'table' 或 'card'
const lastUpdateTime = ref('')
const connectionStatus = ref('connected') // 'connected', 'disconnected', 'connecting'
const updateCounter = ref(0)
const statusLoading = ref(false)
const activeAnalyticsTab = ref('performance') // Phase 3 分析面板的激活标签页

// 状态统计数据
const statusSummary = ref({
  totalJobs: 0,
  buildingJobs: 0,
  queueCount: 0,
  successRate: 0,
  failedJobs: 0,
  successJobs: 0,
  averageDuration: 0,
  todayBuilds: 0
})

// Jenkins数据
const jobs = ref([])
const buildHistory = ref([])

// 计算属性
const filteredJobs = computed(() => {
  return jobs.value.filter(job => {
    const matchesSearch = job.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = !statusFilter.value || job.status === statusFilter.value
    const matchesView = !selectedView.value || 
                       (currentView.value && currentView.value.jobs.some(viewJob => viewJob.name === job.name))
    return matchesSearch && matchesStatus && matchesView
  })
})

// 过滤后的日志内容
const filteredLogContent = computed(() => {
  if (!logContent.value) return ''
  
  let lines = logContent.value.split('\n')
  
  // 按搜索关键字过滤
  if (logSearchQuery.value.trim()) {
    const query = logSearchQuery.value.toLowerCase()
    lines = lines.filter(line => 
      line.toLowerCase().includes(query)
    )
  }
  
  // 按日志级别过滤
  if (logLevelFilter.value) {
    lines = lines.filter(line => 
      line.includes(logLevelFilter.value)
    )
  }
  
  return lines.join('\n')
})

// 是否全选
const isAllSelected = computed(() => {
  return filteredJobs.value.length > 0 && selectedJobs.value.length === filteredJobs.value.length
})

// 方法
const getJobIcon = (type) => {
  switch (type) {
    case 'pipeline':
      return DocumentTextIcon
    case 'freestyle':
      return FolderIcon
    default:
      return CogIcon
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'success':
      return 'bg-green-100 text-green-800'
    case 'failure':
      return 'bg-red-100 text-red-800'
    case 'building':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'success':
      return '成功'
    case 'failure':
      return '失败'
    case 'building':
      return '构建中'
    default:
      return '未知'
  }
}

const addNewInstance = () => {
  showAddDialog.value = true
}

const handleCardClick = (cardData) => {
  console.log('状态卡片被点击:', cardData)
  // 可以根据卡片类型执行不同操作
  // 例如：跳转到相关页面、显示详细信息等
}

const saveNewInstance = async () => {
  try {
    const response = await fetchApi('/settings/jenkins', {
      method: 'POST',
      body: newInstance.value
    })
    
    if (response.success) {
      notify.success('Jenkins实例添加成功')
      showAddDialog.value = false
      newInstance.value = { name: '', url: '', username: '', token: '' }
      await fetchInstances()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('保存Jenkins实例失败:', error)
    notify.error(error.message || '保存失败')
  }
}

const triggerBuild = async (job) => {
  if (!selectedInstance.value) {
    notify.warning('请先选择Jenkins实例')
    return
  }
  
  return withLoading(`build-${job.name}`, async () => {
    const response = await fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${job.name}`, {
      method: 'POST'
    })
    
    if (response.success) {
      // 刷新任务列表
      await fetchJobs()
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: `触发构建: ${job.name}`,
    successMessage: `任务 ${job.name} 构建已触发`,
    errorMessage: `触发构建失败: ${job.name}`
  })
}

const viewDetails = (job) => {
  if (!selectedInstance.value) {
    notify.warning('请先选择Jenkins实例')
    return
  }
  
  // 显示任务详细信息，包括：
  // 1. 任务基本信息（描述、创建时间、最后构建等）
  // 2. 构建历史统计
  // 3. 当前状态详情
  // 4. 配置摘要
  
  const jobDetails = {
    name: job.name,
    description: job.description,
    status: job.status,
    lastBuildNumber: job.lastBuildNumber,
    lastBuildTime: job.lastBuildTime,
    duration: job.duration,
    type: job.type,
    buildable: job.buildable
  }
  
  // 创建一个简单的详情展示
  const detailHtml = `
    <div class="text-left">
      <h3 class="text-lg font-semibold mb-3">任务详情: ${job.name}</h3>
      <div class="space-y-2 text-sm">
        <div><strong>描述:</strong> ${job.description || '无描述'}</div>
        <div><strong>状态:</strong> ${getStatusText(job.status)}</div>
        <div><strong>最后构建:</strong> #${job.lastBuildNumber || '无构建记录'}</div>
        <div><strong>构建时间:</strong> ${job.lastBuildTime || '-'}</div>
        <div><strong>持续时间:</strong> ${job.duration || '-'}</div>
        <div><strong>类型:</strong> ${job.type}</div>
        <div><strong>是否可构建:</strong> ${job.buildable ? '是' : '否'}</div>
      </div>
    </div>
  `
  
  notify.info(detailHtml, { 
    title: '任务详情',
    timeout: 0, // 不自动关闭
    type: 'info'
  })
}

const showConfig = async (job) => {
  if (!selectedInstance.value) {
    notify.warning('请先选择Jenkins实例')
    return
  }
  
  currentConfigJob.value = job
  await fetchJobConfig(job.name)
  showConfigDialog.value = true
}

// 获取任务配置
const fetchJobConfig = async (jobName) => {
  return withLoading('fetch-config', async () => {
    const response = await fetchApi(`/ops/jenkins/config/${selectedInstance.value}/${jobName}`, {
      method: 'GET'
    })
    
    if (response.success) {
      jobConfig.value = response.data
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '加载任务配置...',
    errorMessage: '获取任务配置失败'
  })
}

// 更新任务配置
const updateJobConfig = async () => {
  if (!selectedInstance.value || !currentConfigJob.value) {
    notify.warning('请先选择Jenkins实例和任务')
    return
  }
  
  return withLoading('update-config', async () => {
    const response = await fetchApi(`/ops/jenkins/config/${selectedInstance.value}/${currentConfigJob.value.name}`, {
      method: 'POST',
      body: {
        config: jobConfig.value.xml
      }
    })
    
    if (response.success) {
      notify.success('任务配置更新成功')
      showConfigDialog.value = false
      await refreshData()
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '更新任务配置中...',
    successMessage: '配置更新成功',
    errorMessage: '配置更新失败'
  })
}

// 打开视图管理对话框
const openViewManagementDialog = () => {
  fetchJenkinsViews()
  showViewDialog.value = true
}

// 获取Jenkins视图列表
const fetchJenkinsViews = async () => {
  if (!selectedInstance.value) return
  
  return withLoading('fetch-views', async () => {
    const response = await fetchApi(`/ops/jenkins/views/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      jenkinsViews.value = response.data.views || []
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '加载视图列表...',
    errorMessage: '获取视图列表失败'
  })
}

// 创建新视图
const createJenkinsView = async () => {
  if (!selectedInstance.value) return
  
  if (!viewForm.value.name.trim()) {
    notify.warning('请输入视图名称')
    return
  }
  
  return withLoading('create-view', async () => {
    const response = await fetchApi(`/ops/jenkins/views/${selectedInstance.value}`, {
      method: 'POST',
      body: {
        name: viewForm.value.name,
        description: viewForm.value.description,
        jobNames: viewForm.value.jobNames
      }
    })
    
    if (response.success) {
      notify.success('视图创建成功')
      await fetchJenkinsViews()
      viewForm.value = { name: '', description: '', jobNames: [] }
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '创建视图中...',
    successMessage: '视图创建成功',
    errorMessage: '视图创建失败'
  })
}

// 删除视图
const deleteJenkinsView = async (viewName) => {
  if (!selectedInstance.value || !viewName) return
  
  if (!(await notify.confirm(`确定要删除视图 "${viewName}" 吗？此操作不可恢复。`))) {
    return
  }
  
  return withLoading('delete-view', async () => {
    const response = await fetchApi(`/ops/jenkins/views/${selectedInstance.value}/${viewName}`, {
      method: 'DELETE'
    })
    
    if (response.success) {
      notify.success('视图删除成功')
      await fetchJenkinsViews()
      if (selectedView.value === viewName) {
        selectedView.value = ''
      }
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '删除视图中...',
    successMessage: '视图删除成功',
    errorMessage: '视图删除失败'
  })
}

// 更新视图
const updateJenkinsView = async (viewName, viewData) => {
  if (!selectedInstance.value || !viewName) return
  
  return withLoading('update-view', async () => {
    const response = await fetchApi(`/ops/jenkins/views/${selectedInstance.value}/${viewName}`, {
      method: 'PUT',
      body: viewData
    })
    
    if (response.success) {
      notify.success('视图更新成功')
      await fetchJenkinsViews()
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '更新视图中...',
    successMessage: '视图更新成功',
    errorMessage: '视图更新失败'
  })
}

// 获取视图中的任务
const fetchViewJobs = async (viewName) => {
  if (!selectedInstance.value || !viewName) return
  
  return withLoading('fetch-view-jobs', async () => {
    const response = await fetchApi(`/ops/jenkins/views/${selectedInstance.value}/${viewName}/jobs`, {
      method: 'GET'
    })
    
    if (response.success) {
      currentView.value = response.data
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '加载视图任务...',
    errorMessage: '获取视图任务失败'
  })
}

// 监听视图选择变化
const handleViewChange = async () => {
  if (selectedView.value) {
    await fetchViewJobs(selectedView.value)
  } else {
    currentView.value = null
  }
}

// 查看日志
const viewLogs = async (job) => {
  if (!selectedInstance.value || !job.lastBuildNumber) {
    notify.warning('请先选择Jenkins实例，且任务需要有构建记录')
    return
  }
  
  currentLogJob.value = job
  showLogDialog.value = true
  await fetchBuildLog(job.name, job.lastBuildNumber)
}

// 获取构建日志
const fetchBuildLog = async (jobName, buildNumber) => {
  logContent.value = ''
  
  return withLoading('fetch-log', async () => {
    const response = await fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${jobName}/${buildNumber}/log`, {
      method: 'GET'
    })
    
    if (response.success) {
      logContent.value = response.data.log
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '获取构建日志...',
    errorMessage: '获取日志失败',
    showNotification: false
  }).catch(error => {
    logContent.value = `获取日志失败: ${error.message}`
    throw error
  })
}

// 刷新日志
const refreshLog = async () => {
  if (currentLogJob.value) {
    await fetchBuildLog(currentLogJob.value.name, currentLogJob.value.lastBuildNumber)
  }
}

// 下载日志
const downloadLog = () => {
  if (!logContent.value || !currentLogJob.value) return
  
  const blob = new Blob([logContent.value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${currentLogJob.value.name}-${currentLogJob.value.lastBuildNumber}.log`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// 切换全选
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedJobs.value = []
  } else {
    selectedJobs.value = filteredJobs.value.map(job => job.name)
  }
}

// 清除选择
const clearSelection = () => {
  selectedJobs.value = []
}

// 批量构建
const batchBuild = async () => {
  if (!selectedInstance.value || selectedJobs.value.length === 0) {
    notify.warning('请先选择Jenkins实例和任务')
    return
  }
  
  if (!(await notify.confirm(`确定要批量构建选中的 ${selectedJobs.value.length} 个任务吗？`))) {
    return
  }
  
  return withBatchLoading('batch-build', 
    selectedJobs.value.map(jobName => () => 
      fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${jobName}`, {
        method: 'POST'
      })
    ), {
      message: '批量构建进行中',
      concurrent: 3, // 限制并发数
      showProgress: true,
      showNotification: true
    }
  ).then(async (batchResult) => {
    // 处理批量结果
    const { successCount, errorCount, results } = batchResult
    
    // 显示详细结果
    if (errorCount > 0) {
      const failures = results
        .filter(r => r.value && !r.value.success)
        .map((r, index) => `- ${selectedJobs.value[r.value.index]}: ${r.value.error?.message || '未知错误'}`)
        .join('\n')
      
      notify.warning(`批量构建完成: 成功 ${successCount} 个，失败 ${errorCount} 个\n\n失败任务:\n${failures}`)
    }
    
    // 清除选择并刷新数据
    clearSelection()
    await refreshData()
    
    return batchResult
  })
}

// 批量健康检查
const batchHealthCheck = async () => {
  if (!selectedInstance.value) {
    notify.warning('请先选择Jenkins实例')
    return
  }
  
  return withLoading('health-check', async () => {
    const response = await fetchApi(`/ops/jenkins/test/${selectedInstance.value}`, {
      method: 'POST'
    })
    
    if (response.success) {
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '执行健康检查...',
    successMessage: '健康检查完成',
    errorMessage: '健康检查失败'
  })
}

// 打开批量构建对话框
const openBatchBuildDialog = async () => {
  // 可以扩展为更复杂的批量构建参数配置对话框
  const jobCount = jobs.value.filter(job => job.buildable).length
  if (jobCount === 0) {
    notify.warning('没有可构建的任务')
    return
  }
  
  if (await notify.confirm(`确定要对所有 ${jobCount} 个可构建任务执行批量构建吗？`)) {
    const buildableJobs = jobs.value.filter(job => job.buildable).map(job => job.name)
    selectedJobs.value = buildableJobs
    batchBuild()
  }
}

// 打开日志查看对话框
const openLogViewerDialog = () => {
  const jobsWithBuilds = jobs.value.filter(job => job.lastBuildNumber > 0)
  if (jobsWithBuilds.length === 0) {
    notify.warning('没有找到有构建记录的任务')
    return
  }
  
  // 选择第一个有构建记录的任务查看日志
  const firstJob = jobsWithBuilds[0]
  viewLogs(firstJob)
}

// Jenkins实例相关方法现在由JenkinsInstanceSelector组件处理

// 获取Jenkins任务列表
const fetchJobs = async () => {
  if (!selectedInstance.value) return
  
  const measureName = performanceMonitor.startMeasure('fetch-jobs')
  
  try {
    return await withLoading('fetch-jobs', async () => {
      // 检查缓存
      const cacheKey = `jobs-${selectedInstance.value}`
      const cachedJobs = cacheManager.get(cacheKey)
      if (cachedJobs) {
        jobs.value = cachedJobs
        calculateStatusSummary()
        return cachedJobs
      }
      
      const response = await performanceMonitor.measureApiCall(
        'jenkins-jobs-api',
        fetchApi(`/ops/jenkins/jobs/${selectedInstance.value}`, {
          method: 'GET'
        })
      )
      
      if (response.success) {
        const processedJobs = response.data.map(job => ({
          ...job,
          id: job.name,
          description: job.description || `Jenkins任务: ${job.name}`,
          type: job.buildable ? 'freestyle' : 'disabled',
          lastBuildTime: job.lastBuildTime ? new Date(job.lastBuildTime).toLocaleString() : '-',
          duration: job.duration ? `${Math.round(job.duration / 1000)}秒` : '-',
          lastBuildNumber: job.lastBuildNumber || 0
        }))
        
        jobs.value = processedJobs
        
        // 缓存结果
        cacheManager.set(cacheKey, processedJobs, 120000) // 缓存2分钟
        
        // 计算状态统计
        calculateStatusSummary()
        return response.data
      } else {
        throw new Error(response.message)
      }
    }, {
      message: '加载任务列表...',
      errorMessage: '获取Jenkins任务失败',
      showNotification: false
    })
  } catch (error) {
    catchError(error, { component: 'Jenkins', method: 'fetchJobs' })
    throw error
  } finally {
    performanceMonitor.endMeasure(measureName)
  }
}

// 刷新所有数据
const refreshData = async () => {
  if (!selectedInstance.value) return
  
  return withLoading('refresh', async () => {
    await Promise.all([
      fetchJobs(),
      fetchJenkinsStatus(),
      fetchQueue(),
      fetchBuildHistory(),
      fetchJenkinsViews()
    ])
    
    // 如果选择了视图，刷新视图任务
    if (selectedView.value) {
      await fetchViewJobs(selectedView.value)
    }
    
    // 更新最后更新时间
    lastUpdateTime.value = new Date().toLocaleString()
  }, {
    message: '刷新数据中...',
    successMessage: '数据刷新成功',
    errorMessage: '数据刷新失败'
  })
}

// 获取Jenkins状态概览
const fetchJenkinsStatus = async () => {
  if (!selectedInstance.value) return
  
  return withLoading('fetch-status', async () => {
    const response = await fetchApi(`/ops/jenkins/status/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      const data = response.data
      statusSummary.value.totalJobs = data.totalJobs
      statusSummary.value.queueCount = data.queueCount
      return data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '获取Jenkins状态...',
    errorMessage: '获取Jenkins状态失败',
    showNotification: false
  })
}

// 获取构建队列
const fetchQueue = async () => {
  if (!selectedInstance.value) return
  
  return withLoading('fetch-queue', async () => {
    const response = await fetchApi(`/ops/jenkins/queue/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      statusSummary.value.queueCount = response.data.length
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '获取构建队列...',
    errorMessage: '获取构建队列失败',
    showNotification: false
  })
}

// 计算状态统计
const calculateStatusSummary = () => {
  const totalJobs = jobs.value.length
  let buildingJobs = 0
  let successJobs = 0
  let failedJobs = 0
  
  jobs.value.forEach(job => {
    if (job.status === 'building') {
      buildingJobs++
    } else if (job.status === 'success') {
      successJobs++
    } else if (job.status === 'failure') {
      failedJobs++
    }
  })
  
  statusSummary.value.totalJobs = totalJobs
  statusSummary.value.buildingJobs = buildingJobs
  statusSummary.value.successJobs = successJobs
  statusSummary.value.failedJobs = failedJobs
  statusSummary.value.successRate = totalJobs > 0 ? Math.round((successJobs / totalJobs) * 100) : 0
}

// 自动刷新控制器
let autoRefreshController = null

// 切换自动刷新
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  // 首先清理所有现有的定时器，防止内存泄露
  timerManager.clearAll()
  if (autoRefreshController) {
    autoRefreshController.stop()
    autoRefreshController = null
  }
  
  if (autoRefresh.value) {
    // 使用带重试机制的定时器，每30秒刷新一次
    autoRefreshController = timerManager.setRetryInterval(
      async () => {
        connectionStatus.value = 'connecting'
        await refreshData()
        connectionStatus.value = 'connected'
        updateCounter.value++
      },
      30000, // 30秒间隔
      -1, // 无限重试
      (error, retryCount) => {
        console.error(`自动刷新失败 (第${retryCount}次重试):`, error)
        connectionStatus.value = 'disconnected'
        
        // 如果连续失败3次，延长重试间隔
        if (retryCount >= 3) {
          console.warn('连续刷新失败，将延长重试间隔至60秒')
          // 这里可以动态调整重试间隔，但目前TimerManager还不支持
          // 作为替代方案，我们在错误处理中记录状态
        }
      }
    )
    
    // 立即刷新一次
    refreshData().catch(error => {
      console.error('初始刷新失败:', error)
      connectionStatus.value = 'disconnected'
    })
  } else {
    // 停止自动刷新
    connectionStatus.value = 'connected'
  }
}

// 监听实例选择变化
const onInstanceChange = async (instanceId, instanceData) => {
  console.log('Jenkins实例已切换:', instanceId, instanceData)
  selectedView.value = '' // 重置视图选择
  currentView.value = null
  await refreshData()
}

// 监听视图选择变化
watch(selectedView, handleViewChange)

// 获取构建历史
const fetchBuildHistory = async () => {
  if (!selectedInstance.value) return
  
  return withLoading('fetch-history', async () => {
    const response = await fetchApi(`/ops/jenkins/history/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      buildHistory.value = response.data.map(build => ({
        ...build,
        startTime: build.startTime ? new Date(build.startTime).toLocaleString() : '-',
        duration: build.duration ? `${Math.round(build.duration / 1000)}秒` : '-'
      }))
      return response.data
    } else {
      throw new Error(response.message)
    }
  }, {
    message: '获取构建历史...',
    errorMessage: '获取构建历史失败',
    showNotification: false
  })
}

// 快捷键处理
const handleKeydown = (event) => {
  // F5 - 刷新页面 (避免与浏览器Ctrl+R冲突)
  if (event.key === 'F5') {
    event.preventDefault()
    if (selectedInstance.value) {
      refreshData()
    }
  }
  
  // Ctrl + Shift + R - 刷新页面 (备用快捷键)
  if (event.ctrlKey && event.shiftKey && event.key === 'R') {
    event.preventDefault()
    if (selectedInstance.value) {
      refreshData()
    }
  }
  
  // Ctrl + B - 批量构建
  if (event.ctrlKey && event.key === 'b') {
    event.preventDefault()
    if (selectedInstance.value && jobs.value.length > 0) {
      openBatchBuildDialog()
    }
  }
  
  // Ctrl + K - 快速搜索 (聚焦搜索框，避免与浏览器Ctrl+F冲突)
  if (event.ctrlKey && event.key === 'k') {
    event.preventDefault()
    const searchInput = document.querySelector('input[placeholder*="搜索任务"]')
    if (searchInput) {
      searchInput.focus()
      searchInput.select()
    }
  }
  
  // Ctrl + L - 查看日志
  if (event.ctrlKey && event.key === 'l') {
    event.preventDefault()
    if (selectedInstance.value) {
      openLogViewerDialog()
    }
  }
  
  // Ctrl + T - 健康检查 (Test的首字母，避免与浏览器Ctrl+H冲突)
  if (event.ctrlKey && event.key === 't') {
    event.preventDefault()
    if (selectedInstance.value) {
      batchHealthCheck()
    }
  }
  
  // Ctrl + Shift + A - 自动刷新切换
  if (event.ctrlKey && event.shiftKey && event.key === 'A') {
    event.preventDefault()
    if (selectedInstance.value) {
      toggleAutoRefresh()
    }
  }
  
  // Escape - 关闭对话框
  if (event.key === 'Escape') {
    showAddDialog.value = false
    showLogDialog.value = false
    clearSelection()
  }
  
  // Ctrl + A - 全选任务 (在任务列表区域，避免在输入框中触发)
  if (event.ctrlKey && event.key === 'a') {
    const activeElement = document.activeElement
    const isInInputField = activeElement?.tagName.match(/INPUT|TEXTAREA/) || 
                          activeElement?.contentEditable === 'true'
    
    if (!isInInputField) {
      event.preventDefault()
      if (filteredJobs.value.length > 0) {
        toggleSelectAll()
      }
    }
  }
  
  // Delete - 清除选择
  if (event.key === 'Delete' || event.key === 'Backspace') {
    const activeElement = document.activeElement
    const isInInputField = activeElement?.tagName.match(/INPUT|TEXTAREA/) || 
                          activeElement?.contentEditable === 'true'
    
    if (!isInInputField && selectedJobs.value.length > 0) {
      event.preventDefault()
      clearSelection()
    }
  }
}

// 组件挂载时添加事件监听
onMounted(() => {
  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeydown)
})

// 组件卸载时清理定时器和事件监听
onBeforeUnmount(() => {
  // 停止自动刷新
  autoRefresh.value = false
  
  // 停止自动刷新控制器
  if (autoRefreshController) {
    autoRefreshController.stop()
    autoRefreshController = null
  }
  
  // 清理所有定时器
  timerManager.clearAll()
  
  // 移除键盘事件监听
  document.removeEventListener('keydown', handleKeydown)
  
  // 重置连接状态
  connectionStatus.value = 'disconnected'
  
  console.log('Jenkins组件已卸载，所有资源已清理')
  console.log('定时器统计:', timerManager.getStats())
})
</script>

<script>
export default {
  name: 'Jenkins',
  components: {
    JenkinsInstanceSelector,
    JenkinsStatusCards,
    BuildHistoryAnalytics,
    BuildTrendsChart,
    PerformanceMetrics,
    BuildPredictionAnalysis,
    FailureAnalysis,
    OptimizationRecommendations
  }
}
</script>

<style scoped>
/* 响应式设计样式 */
@media (max-width: 768px) {
  .jenkins-dashboard {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 640px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .task-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.25rem;
  }
  
  .task-actions button {
    justify-content: center;
  }
}

/* 大屏展示优化 */
@media (min-width: 1920px) {
  .jenkins-dashboard {
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
  }
  
  .stats-cards {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 构建进度动画 */
.build-progress {
  background: linear-gradient(90deg, #10B981 0%, #3B82F6 100%);
  height: 4px;
  border-radius: 2px;
  animation: progress-pulse 2s infinite;
}

@keyframes progress-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 状态指示灯 */
.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
}

.status-success {
  background-color: #10B981;
  box-shadow: 0 0 4px rgba(16, 185, 129, 0.4);
}

.status-failure {
  background-color: #EF4444;
  box-shadow: 0 0 4px rgba(239, 68, 68, 0.4);
}

.status-building {
  background-color: #F59E0B;
  animation: building-pulse 1.5s infinite;
}

@keyframes building-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

.status-unknown {
  background-color: #6B7280;
}

/* 表格行悬停效果 */
.table-row:hover {
  background-color: #F9FAFB;
  transition: background-color 0.15s ease-in-out;
}

/* 选中状态 */
.table-row.selected {
  background-color: #EBF4FF;
  border-left: 4px solid #3B82F6;
}

/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #F1F5F9;
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}
</style>