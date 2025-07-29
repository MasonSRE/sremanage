<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页头 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">软件管理中心</h1>
            <p class="mt-1 text-sm text-gray-500">一站式软件安装、管理和监控平台</p>
          </div>
          <div class="flex items-center space-x-4">
            <select 
              v-if="activeTab === 'store'" 
              v-model="selectedCategory" 
              class="rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">所有分类</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
            <button @click="refreshCurrentTab" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              刷新
            </button>
          </div>
        </div>
        
        <!-- 标签页导航 -->
        <div class="border-t border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button
              @click="activeTab = 'store'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'store'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <svg class="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
              </svg>
              应用商店
            </button>
            <button
              @click="activeTab = 'installed'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'installed'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <svg class="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              已安装 ({{ installedApps.length }})
            </button>
            <button
              @click="activeTab = 'manage'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'manage'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <svg class="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              应用管理
            </button>
          </nav>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      <!-- 应用商店标签页 -->
      <div v-if="activeTab === 'store'">
        <!-- 统计信息 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div class="flex items-center">
              <div class="p-3 rounded-lg bg-blue-50">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">可用应用</p>
                <p class="text-2xl font-semibold text-gray-900">{{ filteredApps.length }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div class="flex items-center">
              <div class="p-3 rounded-lg bg-green-50">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">已安装</p>
                <p class="text-2xl font-semibold text-gray-900">{{ installedApps.length }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div class="flex items-center">
              <div class="p-3 rounded-lg bg-purple-50">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">分类数量</p>
                <p class="text-2xl font-semibold text-gray-900">{{ categories.length }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div class="flex items-center">
              <div class="p-3 rounded-lg bg-orange-50">
                <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">快速部署</p>
                <p class="text-2xl font-semibold text-gray-900">Docker</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 应用网格 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="app in filteredApps"
          :key="app.id"
          class="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100 overflow-hidden group"
        >
          <!-- 应用图标和基本信息 -->
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center">
                <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  {{ app.name.charAt(0) }}
                </div>
                <div class="ml-3">
                  <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    {{ app.name }}
                  </h3>
                  <p class="text-sm text-gray-500">{{ app.version }}</p>
                </div>
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {{ app.category }}
              </span>
            </div>
            
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ app.description }}</p>
            
            <!-- 标签 -->
            <div class="flex flex-wrap gap-2 mb-4">
              <span
                v-for="tag in app.tags.slice(0, 3)"
                :key="tag"
                class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
              >
                #{{ tag }}
              </span>
            </div>
            
            <!-- 端口信息 -->
            <div class="mb-4">
              <div class="flex items-center text-sm text-gray-500 mb-2">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"></path>
                </svg>
                默认端口
              </div>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="port in app.ports.slice(0, 2)"
                  :key="port.name"
                  class="inline-flex items-center px-2 py-1 rounded text-xs bg-green-50 text-green-700 font-mono"
                >
                  {{ port.host }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="px-6 py-4 bg-gray-50 border-t border-gray-100">
            <button
              @click="showInstallModal(app)"
              class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              立即安装
            </button>
          </div>
        </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="filteredApps.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">暂无应用</h3>
          <p class="mt-1 text-sm text-gray-500">该分类下没有找到应用</p>
        </div>
      </div>

      <!-- 应用管理标签页 -->
      <div v-if="activeTab === 'manage'">
        <!-- 管理工具栏 -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">应用模板管理</h2>
            <p class="text-gray-600">管理和配置应用模板，支持添加自定义应用</p>
          </div>
          <button
            @click="showCreateTemplateModal = true"
            class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            添加应用模板
          </button>
          <button
            v-if="legacyApps.length > 0"
            @click="showMigrationModal = true"
            class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
            </svg>
            迁移旧应用 ({{ legacyApps.length }})
          </button>
        </div>

        <!-- 迁移提示 -->
        <div v-if="legacyApps.length > 0" class="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
          <div class="flex">
            <svg class="w-5 h-5 text-orange-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.764 0L3.05 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <div>
              <h4 class="text-sm font-medium text-orange-800 mb-1">发现旧版本应用</h4>
              <div class="text-sm text-orange-700">
                <p class="mb-2">检测到 {{ legacyApps.length }} 个使用旧系统部署的应用，建议迁移到新系统以获得更好的管理体验。</p>
                <p>迁移后你可以在"已安装"页面统一管理这些应用。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作说明 -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div class="flex">
            <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <h4 class="text-sm font-medium text-blue-800 mb-1">操作说明</h4>
              <div class="text-sm text-blue-700">
                <p class="mb-2">• <strong>所有应用</strong>：都可以直接编辑配置，包括端口、存储卷、环境变量等</p>
                <p class="mb-2">• <strong>系统预设应用</strong>（带"系统预设"标签）：不可删除，但可以编辑和复制</p>
                <p>• <strong>修改端口/存储卷</strong>：直接点击编辑按钮修改配置即可</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 模板列表 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">应用模板列表</h3>
          </div>
          
          <div class="divide-y divide-gray-200">
            <div 
              v-for="template in templates" 
              :key="template.id"
              class="px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-green-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    {{ template.name.charAt(0) }}
                  </div>
                  <div class="ml-4">
                    <h4 class="text-lg font-semibold text-gray-900">{{ template.name }}</h4>
                    <p class="text-sm text-gray-500">{{ template.description }}</p>
                    <div class="flex items-center mt-1 space-x-3">
                      <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                        {{ template.category }}
                      </span>
                      <span class="text-xs text-gray-400">版本: {{ template.version }}</span>
                      <span v-if="template.is_system" class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                        系统预设
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="flex items-center space-x-2">
                  <!-- 编辑按钮 - 现在所有应用都可以编辑 -->
                  <button 
                    @click="editTemplate(template)"
                    class="text-blue-600 hover:text-blue-700 p-2 rounded-lg hover:bg-blue-50"
                    title="编辑"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  
                  <button 
                    @click="duplicateTemplate(template)"
                    class="text-green-600 hover:text-green-700 p-2 rounded-lg hover:bg-green-50"
                    title="复制"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                  </button>
                  
                  <button 
                    v-if="!template.is_system"
                    @click="deleteTemplate(template)"
                    class="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50"
                    title="删除"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 已安装标签页 -->
      <div v-if="activeTab === 'installed'">
        <!-- 统计信息 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div class="flex items-center">
              <div class="p-3 rounded-lg bg-green-50">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">已安装应用</p>
                <p class="text-2xl font-semibold text-gray-900">{{ installedApps.length }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div class="flex items-center">
              <div class="p-3 rounded-lg bg-blue-50">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">运行中</p>
                <p class="text-2xl font-semibold text-gray-900">{{ runningApps }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div class="flex items-center">
              <div class="p-3 rounded-lg bg-red-50">
                <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">已停止</p>
                <p class="text-2xl font-semibold text-gray-900">{{ stoppedApps }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 已安装应用列表 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">已安装应用</h3>
          </div>
          
          <div v-if="installedApps.length === 0" class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">暂无已安装应用</h3>
            <p class="mt-1 text-sm text-gray-500">
              前往 
              <button @click="activeTab = 'store'" class="text-blue-600 hover:text-blue-700">应用商店</button>
              安装您的第一个应用
            </p>
          </div>

          <div v-else class="divide-y divide-gray-200">
            <div 
              v-for="app in installedApps" 
              :key="app.id"
              class="px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    {{ app.name.charAt(0) }}
                  </div>
                  <div class="ml-4">
                    <h4 class="text-lg font-semibold text-gray-900">{{ app.name }}</h4>
                    <p class="text-sm text-gray-500">实例ID: {{ app.instance_id }}</p>
                    <p class="text-sm text-gray-500">主机: {{ app.host }}</p>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    app.status === 'running' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  ]">
                    {{ app.status === 'running' ? '运行中' : '已停止' }}
                  </span>
                  
                  <div class="flex space-x-2">
                    <button 
                      v-if="app.status === 'running'"
                      @click="stopAppInstance(app)"
                      class="text-red-600 hover:text-red-700 p-1 rounded"
                      title="停止"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10h6v4H9z"></path>
                      </svg>
                    </button>
                    
                    <button 
                      v-else
                      @click="startAppInstance(app)"
                      class="text-green-600 hover:text-green-700 p-1 rounded"
                      title="启动"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.5a1.5 1.5 0 011.5 1.5v4a1.5 1.5 0 01-1.5 1.5H9m4.5-7H15a1.5 1.5 0 011.5 1.5v4a1.5 1.5 0 01-1.5 1.5h-1.5m-3-5V9a1.5 1.5 0 011.5-1.5h1.5"></path>
                      </svg>
                    </button>
                    
                    <button 
                      @click="viewAppLogs(app)"
                      class="text-blue-600 hover:text-blue-700 p-1 rounded"
                      title="查看日志"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                    </button>
                    
                    <button 
                      @click="uninstallAppInstance(app)"
                      class="text-red-600 hover:text-red-700 p-1 rounded"
                      title="卸载"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 安装模态框 -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click="closeModal"
    >
      <div
        class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
        @click.stop
      >
        <!-- 模态框头部 -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                {{ selectedApp?.name?.charAt(0) }}
              </div>
              <div class="ml-3">
                <h3 class="text-lg font-semibold text-gray-900">安装 {{ selectedApp?.name }}</h3>
                <p class="text-sm text-gray-500">{{ selectedApp?.description }}</p>
              </div>
            </div>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- 模态框内容 -->
        <div class="px-6 py-4">
          <!-- 主机选择 -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">选择目标主机</label>
            <select v-model="installForm.host_id" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option value="">请选择主机</option>
              <option v-for="host in hosts" :key="host.id" :value="host.id">
                {{ host.hostname }} ({{ host.ip }}) - {{ host.source_type === 'aliyun' ? '阿里云ECS' : '手动添加' }}
              </option>
            </select>
          </div>

          <!-- 配置参数 -->
          <div class="mb-6">
            <h4 class="text-sm font-medium text-gray-700 mb-3">配置参数</h4>
            <div class="space-y-4">
              <div v-for="(envVar, key) in selectedApp?.env_vars" :key="key">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ envVar.description }}
                </label>
                <input
                  v-model="installForm.config[key]"
                  :placeholder="envVar.default"
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- 端口配置 -->
          <div class="mb-6">
            <h4 class="text-sm font-medium text-gray-700 mb-3">端口映射</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <div v-for="port in selectedApp?.ports" :key="port.name" class="flex items-center justify-between py-2">
                <span class="text-sm text-gray-600">{{ port.name }}</span>
                <span class="text-sm font-mono bg-white px-2 py-1 rounded border">
                  {{ port.host }} → {{ port.container }}
                </span>
              </div>
            </div>
          </div>

          <!-- 存储卷 -->
          <div class="mb-6">
            <h4 class="text-sm font-medium text-gray-700 mb-3">数据存储</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <div v-for="volume in selectedApp?.volumes" :key="volume.name" class="flex items-center justify-between py-2">
                <span class="text-sm text-gray-600">{{ volume.name }}</span>
                <span class="text-sm font-mono bg-white px-2 py-1 rounded border">
                  ./{{ volume.host }} → {{ volume.container }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 模态框底部 -->
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
          <button
            @click="closeModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="installApp"
            :disabled="!installForm.host_id || installing"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <svg v-if="installing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ installing ? '安装中...' : '确认安装' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 创建/编辑模板模态框 -->
    <div
      v-if="showCreateTemplateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click="closeCreateTemplateModal"
    >
      <div
        class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <!-- 模态框头部 -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingTemplate ? '编辑' : '创建' }}应用模板
            </h3>
            <button @click="closeCreateTemplateModal" class="text-gray-400 hover:text-gray-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- 模态框内容 -->
        <div class="px-6 py-4">
          <form @submit.prevent="saveTemplate">
            <!-- 基本信息 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">应用ID</label>
                <input
                  v-model="templateForm.id"
                  :disabled="editingTemplate"
                  type="text"
                  placeholder="例如: kafka"
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100"
                  required
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">应用名称</label>
                <input
                  v-model="templateForm.name"
                  type="text"
                  placeholder="例如: Apache Kafka"
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">分类</label>
                <select
                  v-model="templateForm.category"
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                >
                  <option value="">选择分类</option>
                  <option v-for="cat in appCategories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">版本</label>
                <input
                  v-model="templateForm.version"
                  type="text"
                  placeholder="例如: latest"
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
            </div>

            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">描述</label>
              <textarea
                v-model="templateForm.description"
                rows="3"
                placeholder="描述该应用的功能和特点"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
              ></textarea>
            </div>

            <!-- Docker Compose模板 -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Docker Compose 模板
                <span class="text-gray-500 text-xs">(支持变量: ${VARIABLE_NAME})</span>
              </label>
              <textarea
                v-model="templateForm.compose_template"
                rows="12"
                placeholder="version: '3.8'&#10;services:&#10;  kafka:&#10;    image: confluentinc/cp-kafka:${KAFKA_VERSION}&#10;    container_name: ${CONTAINER_NAME}&#10;    ports:&#10;      - '${KAFKA_PORT}:9092'"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 font-mono text-sm"
                required
              ></textarea>
            </div>

            <!-- 环境变量配置 -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-gray-700">环境变量配置</label>
                <button
                  type="button"
                  @click="addEnvVar"
                  class="text-blue-600 hover:text-blue-700 text-sm"
                >
                  + 添加变量
                </button>
              </div>
              <div class="space-y-3">
                <div 
                  v-for="(envVar, index) in templateForm.env_vars_list" 
                  :key="index"
                  class="grid grid-cols-12 gap-3 items-center"
                >
                  <div class="col-span-3">
                    <input
                      v-model="envVar.key"
                      type="text"
                      placeholder="变量名"
                      class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                    />
                  </div>
                  <div class="col-span-3">
                    <input
                      v-model="envVar.default"
                      type="text"
                      placeholder="默认值"
                      class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                    />
                  </div>
                  <div class="col-span-5">
                    <input
                      v-model="envVar.description"
                      type="text"
                      placeholder="描述"
                      class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                    />
                  </div>
                  <div class="col-span-1">
                    <button
                      type="button"
                      @click="removeEnvVar(index)"
                      class="text-red-600 hover:text-red-700 p-1"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 端口配置 -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-gray-700">端口配置</label>
                <button
                  type="button"
                  @click="addPort"
                  class="text-blue-600 hover:text-blue-700 text-sm"
                >
                  + 添加端口
                </button>
              </div>
              <div class="space-y-3">
                <div 
                  v-for="(port, index) in templateForm.ports_list" 
                  :key="index"
                  class="grid grid-cols-12 gap-3 items-center"
                >
                  <div class="col-span-3">
                    <input
                      v-model="port.name"
                      type="text"
                      placeholder="端口名称"
                      class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                    />
                  </div>
                  <div class="col-span-3">
                    <input
                      v-model.number="port.host"
                      type="number"
                      placeholder="主机端口"
                      class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                    />
                  </div>
                  <div class="col-span-3">
                    <input
                      v-model.number="port.container"
                      type="number"
                      placeholder="容器端口"
                      class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                    />
                  </div>
                  <div class="col-span-2">
                    <select
                      v-model="port.protocol"
                      class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                    >
                      <option value="tcp">TCP</option>
                      <option value="udp">UDP</option>
                    </select>
                  </div>
                  <div class="col-span-1">
                    <button
                      type="button"
                      @click="removePort(index)"
                      class="text-red-600 hover:text-red-700 p-1"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 标签 -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">标签</label>
              <input
                v-model="templateForm.tags_string"
                type="text"
                placeholder="用逗号分隔，例如: web,proxy,server"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <!-- 提交按钮 -->
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="closeCreateTemplateModal"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ saving ? '保存中...' : (editingTemplate ? '更新' : '创建') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 迁移模态框 -->
    <div
      v-if="showMigrationModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click="closeMigrationModal"
    >
      <div
        class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <!-- 模态框头部 -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">迁移旧版本应用</h3>
            <button @click="closeMigrationModal" class="text-gray-400 hover:text-gray-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- 模态框内容 -->
        <div class="px-6 py-4">
          <div class="mb-4">
            <p class="text-sm text-gray-600 mb-4">
              以下是检测到的旧版本应用实例。迁移后，这些应用将在新系统中进行统一管理。
            </p>
            
            <!-- 全选控制 -->
            <div class="flex items-center mb-4">
              <input
                type="checkbox"
                id="selectAll"
                v-model="selectAllLegacyApps"
                @change="toggleSelectAllLegacyApps"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <label for="selectAll" class="ml-2 text-sm font-medium text-gray-700">
                全选 ({{ selectedLegacyApps.length }}/{{ legacyApps.length }})
              </label>
            </div>
          </div>

          <!-- 应用列表 -->
          <div class="space-y-3 max-h-96 overflow-y-auto">
            <div 
              v-for="app in legacyApps" 
              :key="app.container_name"
              class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <input
                type="checkbox"
                :id="app.container_name"
                v-model="selectedLegacyApps"
                :value="app"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              
              <div class="ml-3 flex-1">
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">{{ app.container_name }}</h4>
                    <p class="text-xs text-gray-500">
                      类型: {{ app.app_type }} | 主机: {{ app.hostname }} | 状态: 
                      <span :class="app.status === 'running' ? 'text-green-600' : 'text-red-600'">
                        {{ app.status === 'running' ? '运行中' : '已停止' }}
                      </span>
                    </p>
                    <p class="text-xs text-gray-400">镜像: {{ app.image }}</p>
                  </div>
                  
                  <div class="text-right">
                    <p class="text-xs text-gray-500">端口映射</p>
                    <p class="text-xs font-mono text-gray-700">{{ app.ports || '无' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 迁移状态 -->
          <div v-if="migrating" class="mt-6 p-4 bg-blue-50 rounded-lg">
            <div class="flex items-center mb-2">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="text-sm font-medium text-blue-900">正在迁移应用...</span>
            </div>
            <div class="text-sm text-blue-700">
              <p>进度: {{ migrationProgress.completed }}/{{ migrationProgress.total }}</p>
            </div>
          </div>

          <!-- 迁移结果 -->
          <div v-if="migrationResults.length > 0" class="mt-6">
            <h4 class="text-sm font-medium text-gray-900 mb-3">迁移结果</h4>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <div 
                v-for="result in migrationResults" 
                :key="result.container_name"
                class="flex items-center justify-between p-2 rounded"
                :class="result.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
              >
                <span class="text-sm">{{ result.container_name }}</span>
                <span class="text-xs">{{ result.message }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 模态框底部 -->
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
          <button
            @click="closeMigrationModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="startMigration"
            :disabled="selectedLegacyApps.length === 0 || migrating"
            class="px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ migrating ? '迁移中...' : `迁移选中的应用 (${selectedLegacyApps.length})` }}
          </button>
        </div>
      </div>
    </div>

    <!-- 安装日志模态框 -->
    <div
      v-if="showLogModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click="closeLogModal"
    >
      <div
        class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[80vh] overflow-y-auto"
        @click.stop
      >
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">安装日志</h3>
            <button @click="closeLogModal" class="text-gray-400 hover:text-gray-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        <div class="px-6 py-4">
          <div class="bg-black rounded-lg p-4 font-mono text-sm text-green-400 min-h-[300px] whitespace-pre-wrap">{{ installLog }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchApi } from '@/utils/api'

// 响应式数据
const apps = ref([])
const categories = ref([])
const hosts = ref([])
const installedApps = ref([])
const templates = ref([])
const appCategories = ref([])
const selectedCategory = ref('')
const showModal = ref(false)
const showLogModal = ref(false)
const showCreateTemplateModal = ref(false)
const selectedApp = ref(null)
const installing = ref(false)
const installLog = ref('')
const activeTab = ref('store')
const editingTemplate = ref(null)
const saving = ref(false)

// 迁移相关
const legacyApps = ref([])
const showMigrationModal = ref(false)
const selectedLegacyApps = ref([])
const selectAllLegacyApps = ref(false)
const migrating = ref(false)
const migrationProgress = ref({ completed: 0, total: 0 })
const migrationResults = ref([])

// 安装表单
const installForm = ref({
  host_id: '',
  config: {}
})

// 模板表单
const templateForm = ref({
  id: '',
  name: '',
  description: '',
  category: '',
  version: 'latest',
  compose_template: '',
  tags_string: '',
  env_vars_list: [],
  ports_list: []
})

// 计算属性
const filteredApps = computed(() => {
  if (!selectedCategory.value) {
    return apps.value
  }
  return apps.value.filter(app => app.category === selectedCategory.value)
})

const runningApps = computed(() => {
  return installedApps.value.filter(app => app.status === 'running').length
})

const stoppedApps = computed(() => {
  return installedApps.value.filter(app => app.status === 'stopped').length
})

// 加载应用列表
const loadApps = async () => {
  try {
    const response = await fetchApi('/docker-apps-test')
    if (response.success) {
      apps.value = response.data.apps
      categories.value = response.data.categories
    }
  } catch (error) {
    console.error('获取应用列表失败:', error)
  }
}

// 加载主机列表
const loadHosts = async () => {
  try {
    const response = await fetchApi('/hosts-all-test')
    if (response.success) {
      hosts.value = response.data
    }
  } catch (error) {
    console.error('获取主机列表失败:', error)
  }
}

// 加载已安装应用
const loadInstalledApps = async () => {
  try {
    const response = await fetchApi('/docker-apps/installed')
    if (response.success) {
      installedApps.value = response.data
    } else {
      // API返回失败，显示空列表
      installedApps.value = []
    }
  } catch (error) {
    console.error('获取已安装应用失败:', error)
    // 网络错误等情况，显示空列表
    installedApps.value = []
  }
}

// 显示安装模态框
const showInstallModal = (app) => {
  selectedApp.value = app
  installForm.value = {
    host_id: '',
    config: {}
  }
  
  // 初始化配置参数默认值
  if (app.env_vars) {
    Object.keys(app.env_vars).forEach(key => {
      installForm.value.config[key] = app.env_vars[key].default
    })
  }
  
  showModal.value = true
}

// 关闭安装模态框
const closeModal = () => {
  showModal.value = false
  selectedApp.value = null
  installForm.value = {
    host_id: '',
    config: {}
  }
}

// 关闭日志模态框
const closeLogModal = () => {
  showLogModal.value = false
  installLog.value = ''
}

// 刷新当前标签页
const refreshCurrentTab = () => {
  if (activeTab.value === 'store') {
    loadApps()
  } else if (activeTab.value === 'installed') {
    loadInstalledApps()
  } else if (activeTab.value === 'manage') {
    loadTemplates()
  }
}

// 加载应用模板
const loadTemplates = async () => {
  try {
    const response = await fetchApi('/app-store/templates')
    if (response.success) {
      templates.value = response.data.templates
      appCategories.value = response.data.categories
    }
  } catch (error) {
    console.error('获取应用模板失败:', error)
  }
}

// 显示创建模板模态框
const showCreateTemplateModal_func = () => {
  editingTemplate.value = null
  resetTemplateForm()
  showCreateTemplateModal.value = true
}

// 编辑模板
const editTemplate = (template) => {
  editingTemplate.value = template
  templateForm.value = {
    id: template.id,
    name: template.name,
    description: template.description,
    category: template.category,
    version: template.version,
    compose_template: template.compose_template || '',
    tags_string: template.tags ? template.tags.join(',') : '',
    env_vars_list: Object.entries(template.env_vars || {}).map(([key, value]) => ({
      key,
      default: value.default || '',
      description: value.description || ''
    })),
    ports_list: template.ports || []
  }
  showCreateTemplateModal.value = true
}

// 复制模板
const duplicateTemplate = (template) => {
  editingTemplate.value = null
  templateForm.value = {
    id: template.id + '_copy',
    name: template.name + ' (副本)',
    description: template.description,
    category: template.category,
    version: template.version,
    compose_template: template.compose_template || '',
    tags_string: template.tags ? template.tags.join(',') : '',
    env_vars_list: Object.entries(template.env_vars || {}).map(([key, value]) => ({
      key,
      default: value.default || '',
      description: value.description || ''
    })),
    ports_list: template.ports || []
  }
  showCreateTemplateModal.value = true
}

// 删除模板
const deleteTemplate = async (template) => {
  if (!confirm(`确定要删除 "${template.name}" 吗？`)) {
    return
  }
  
  try {
    const response = await fetchApi(`/app-store/templates/${template.id}`, {
      method: 'DELETE'
    })
    
    if (response.success) {
      alert('模板删除成功')
      loadTemplates()
    } else {
      alert('删除失败: ' + response.message)
    }
  } catch (error) {
    alert('删除失败: ' + error.message)
  }
}

// 重置模板表单
const resetTemplateForm = () => {
  templateForm.value = {
    id: '',
    name: '',
    description: '',
    category: '',
    version: 'latest',
    compose_template: '',
    tags_string: '',
    env_vars_list: [],
    ports_list: []
  }
}

// 关闭创建模板模态框
const closeCreateTemplateModal = () => {
  showCreateTemplateModal.value = false
  editingTemplate.value = null
  resetTemplateForm()
}

// 添加环境变量
const addEnvVar = () => {
  templateForm.value.env_vars_list.push({
    key: '',
    default: '',
    description: ''
  })
}

// 删除环境变量
const removeEnvVar = (index) => {
  templateForm.value.env_vars_list.splice(index, 1)
}

// 添加端口
const addPort = () => {
  templateForm.value.ports_list.push({
    name: '',
    host: '',
    container: '',
    protocol: 'tcp'
  })
}

// 删除端口
const removePort = (index) => {
  templateForm.value.ports_list.splice(index, 1)
}

// 保存模板
const saveTemplate = async () => {
  if (!templateForm.value.id || !templateForm.value.name || !templateForm.value.description) {
    alert('请填写必要的字段')
    return
  }
  
  saving.value = true
  
  try {
    // 准备提交数据
    const data = {
      id: templateForm.value.id,
      name: templateForm.value.name,
      description: templateForm.value.description,
      category: templateForm.value.category,
      version: templateForm.value.version,
      compose_template: templateForm.value.compose_template,
      tags: templateForm.value.tags_string.split(',').map(tag => tag.trim()).filter(Boolean),
      env_vars: {},
      ports: templateForm.value.ports_list
    }
    
    // 处理环境变量
    templateForm.value.env_vars_list.forEach(envVar => {
      if (envVar.key) {
        data.env_vars[envVar.key] = {
          default: envVar.default,
          description: envVar.description,
          required: true
        }
      }
    })
    
    let response
    if (editingTemplate.value) {
      response = await fetchApi(`/app-store/templates/${templateForm.value.id}`, {
        method: 'PUT',
        body: data
      })
    } else {
      response = await fetchApi('/app-store/templates', {
        method: 'POST',
        body: data
      })
    }
    
    if (response.success) {
      alert(editingTemplate.value ? '模板更新成功' : '模板创建成功')
      closeCreateTemplateModal()
      loadTemplates()
    } else {
      alert('保存失败: ' + response.message)
    }
  } catch (error) {
    alert('保存失败: ' + error.message)
  }
  
  saving.value = false
}

// 迁移相关函数

// 检测旧应用
const detectLegacyApps = async () => {
  try {
    const response = await fetchApi('/migration/detect-legacy-apps')
    if (response.success) {
      legacyApps.value = response.data
    }
  } catch (error) {
    console.error('检测旧应用失败:', error)
  }
}

// 关闭迁移模态框
const closeMigrationModal = () => {
  showMigrationModal.value = false
  selectedLegacyApps.value = []
  selectAllLegacyApps.value = false
  migrationResults.value = []
}

// 切换全选
const toggleSelectAllLegacyApps = () => {
  if (selectAllLegacyApps.value) {
    selectedLegacyApps.value = [...legacyApps.value]
  } else {
    selectedLegacyApps.value = []
  }
}

// 开始迁移
const startMigration = async () => {
  if (selectedLegacyApps.value.length === 0) {
    alert('请选择要迁移的应用')
    return
  }
  
  migrating.value = true
  migrationProgress.value = { completed: 0, total: selectedLegacyApps.value.length }
  migrationResults.value = []
  
  try {
    const response = await fetchApi('/migration/batch-migrate', {
      method: 'POST',
      body: {
        apps: selectedLegacyApps.value
      }
    })
    
    if (response.success) {
      migrationResults.value = response.data.results
      migrationProgress.value.completed = response.data.success
      
      // 刷新相关数据
      await Promise.all([
        loadInstalledApps(),
        detectLegacyApps()
      ])
      
      alert(`迁移完成! 成功: ${response.data.success}/${response.data.total}`)
    } else {
      alert('迁移失败: ' + response.message)
    }
  } catch (error) {
    alert('迁移失败: ' + error.message)
  }
  
  migrating.value = false
}

// 安装应用
const installApp = async () => {
  if (!installForm.value.host_id) {
    alert('请选择目标主机')
    return
  }
  
  installing.value = true
  installLog.value = `开始安装 ${selectedApp.value.name}...\n`
  
  try {
    const response = await fetchApi(`/docker-apps/${selectedApp.value.id}/install-test`, {
      method: 'POST',
      body: {
        host_id: installForm.value.host_id,
        config: installForm.value.config
      }
    })
    
    if (response.success) {
      installLog.value += `✅ ${response.message}\n`
      installLog.value += `📋 实例ID: ${response.data.instance_id}\n`
      installLog.value += `🖥️  主机: ${response.data.host}\n`
      if (response.data.output) {
        installLog.value += `\n📋 Docker输出:\n${response.data.output}\n`
      }
      
      // 刷新已安装应用列表
      await loadInstalledApps()
    } else {
      installLog.value += `❌ 安装失败: ${response.message}\n`
    }
  } catch (error) {
    installLog.value += `❌ 安装出错: ${error.message}\n`
  }
  
  installing.value = false
  closeModal()
  showLogModal.value = true
}

// 启动应用实例
const startAppInstance = async (app) => {
  try {
    const response = await fetchApi(`/docker-apps/instances/${app.instance_id}/start`, {
      method: 'POST'
    })
    
    if (response.success) {
      alert(`${app.name} 启动成功`)
      await loadInstalledApps()
    } else {
      alert(`启动失败: ${response.message}`)
    }
  } catch (error) {
    alert(`启动失败: ${error.message}`)
  }
}

// 停止应用实例
const stopAppInstance = async (app) => {
  if (!confirm(`确定要停止 "${app.name}" 吗？`)) {
    return
  }
  
  try {
    const response = await fetchApi(`/docker-apps/instances/${app.instance_id}/stop`, {
      method: 'POST'
    })
    
    if (response.success) {
      alert(`${app.name} 停止成功`)
      await loadInstalledApps()
    } else {
      alert(`停止失败: ${response.message}`)
    }
  } catch (error) {
    alert(`停止失败: ${error.message}`)
  }
}

// 查看应用日志
const viewAppLogs = async (app) => {
  try {
    const response = await fetchApi(`/docker-apps/instances/${app.instance_id}/logs`)
    
    if (response.success) {
      let logs = response.data.logs || '暂无日志'
      if (response.data.error_logs) {
        logs += '\n\n=== 错误日志 ===\n' + response.data.error_logs
      }
      
      installLog.value = `=== ${app.name} (${app.instance_id}) 运行日志 ===\n\n${logs}`
      showLogModal.value = true
    } else {
      alert(`获取日志失败: ${response.message}`)
    }
  } catch (error) {
    console.error('日志API调用失败:', error)
    alert(`获取日志失败: ${error.message}`)
  }
}


// 卸载应用实例
const uninstallAppInstance = async (app) => {
  if (!confirm(`确定要卸载 "${app.name}" 吗？\n\n⚠️ 这将删除应用的所有数据，包括配置文件和存储卷。此操作不可恢复！`)) {
    return
  }
  
  try {
    const response = await fetchApi(`/docker-apps/instances/${app.instance_id}/uninstall`, {
      method: 'DELETE'
    })
    
    if (response.success) {
      alert(`${app.name} 卸载成功`)
      await loadInstalledApps()
    } else {
      alert(`卸载失败: ${response.message}`)
    }
  } catch (error) {
    alert(`卸载失败: ${error.message}`)
  }
}

// 监听分类变化
watch(selectedCategory, () => {
  // 分类变化时可以重新加载应用
})

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadApps(),
    loadHosts(),
    loadInstalledApps(),
    loadTemplates(),
    detectLegacyApps()
  ])
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>