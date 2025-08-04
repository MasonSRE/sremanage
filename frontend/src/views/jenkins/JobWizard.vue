<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- 页面标题 -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">
            {{ isEditMode ? '编辑任务' : '创建Jenkins任务' }}
          </h1>
          <p class="mt-1 text-sm text-gray-600">
            {{ isEditMode ? '修改现有任务配置' : '使用向导创建新的Jenkins任务' }}
          </p>
          <!-- 无实例警告 -->
          <div v-if="!hasSelectedInstance" class="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-yellow-700">
                  请先选择Jenkins实例后再创建任务
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="text-sm text-gray-500">
          步骤 {{ currentStep }} / {{ totalSteps }}
        </div>
      </div>
    </div>

    <!-- 步骤进度条 -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <div class="flex items-center justify-between">
        <div 
          v-for="(step, index) in steps" 
          :key="step.id"
          class="flex items-center"
          :class="{ 'opacity-50': index + 1 > currentStep }"
        >
          <div :class="[
            'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium',
            index + 1 < currentStep ? 'bg-green-500 text-white' :
            index + 1 === currentStep ? 'bg-blue-500 text-white' :
            'bg-gray-200 text-gray-600'
          ]">
            <CheckIcon v-if="index + 1 < currentStep" class="w-5 h-5" />
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div v-if="index < steps.length - 1" :class="[
            'w-12 h-1 mx-2',
            index + 1 < currentStep ? 'bg-green-500' : 'bg-gray-200'
          ]"></div>
          <div class="ml-2 text-sm">
            <div :class="[
              'font-medium',
              index + 1 <= currentStep ? 'text-gray-900' : 'text-gray-500'
            ]">
              {{ step.title }}
            </div>
          </div>
          <div v-if="index < steps.length - 1" class="mx-4"></div>
        </div>
      </div>
    </div>

    <!-- 步骤内容 -->
    <div class="bg-white rounded-lg shadow-sm border">
      <!-- 步骤1: 项目类型选择 -->
      <div v-if="currentStep === 1" class="p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">选择项目类型</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div 
            @click="selectProjectType('freestyle')"
            :class="[
              'border-2 rounded-lg p-6 cursor-pointer transition-all',
              jobConfig.projectType === 'freestyle' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            ]"
          >
            <div class="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
              🔧
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Freestyle Project</h3>
            <p class="text-gray-600 mb-3">自由风格项目</p>
            <ul class="text-sm text-gray-500 space-y-1">
              <li>• 适合简单的构建任务</li>
              <li>• 支持Shell脚本和批处理</li>
              <li>• 配置直观，易于上手</li>
            </ul>
          </div>
          
          <div 
            @click="selectProjectType('pipeline')"
            :class="[
              'border-2 rounded-lg p-6 cursor-pointer transition-all',
              jobConfig.projectType === 'pipeline' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            ]"
          >
            <div class="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
              🔄
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Pipeline Project</h3>
            <p class="text-gray-600 mb-3">流水线项目</p>
            <ul class="text-sm text-gray-500 space-y-1">
              <li>• 适合复杂的CI/CD流程</li>
              <li>• 代码即配置(Jenkinsfile)</li>
              <li>• 支持并行执行和条件分支</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 步骤2: 基础配置 -->
      <div v-if="currentStep === 2" class="p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">基础配置</h2>
        
        <form class="space-y-6">
          <!-- 基本信息 -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="text-md font-medium text-gray-900 mb-4">📝 基本信息</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">任务名称 *</label>
                <input 
                  v-model="jobConfig.name" 
                  type="text"
                  :class="[
                    'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    !isValidName && jobConfig.name ? 'border-red-300' : ''
                  ]"
                  placeholder="输入任务名称（只能包含字母、数字、连字符）"
                />
                <p class="mt-1 text-xs text-gray-500">建议使用项目名-环境的格式，如：webapp-prod</p>
                <p v-if="!isValidName && jobConfig.name" class="mt-1 text-xs text-red-600">
                  任务名称只能包含字母、数字、连字符和下划线
                </p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">任务描述</label>
                <textarea 
                  v-model="jobConfig.description" 
                  rows="3"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="描述这个任务的用途和注意事项"
                />
              </div>
            </div>
          </div>
          
          <!-- 源码管理 -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="text-md font-medium text-gray-900 mb-4">📂 源码管理</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Git仓库地址</label>
                <input 
                  v-model="jobConfig.scm.url" 
                  type="url"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="https://github.com/username/repo.git"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">分支</label>
                <input 
                  v-model="jobConfig.scm.branch" 
                  type="text"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="*/master"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">认证凭据</label>
                <select 
                  v-model="jobConfig.scm.credentials"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="">选择认证凭据</option>
                  <option v-for="cred in credentials" :key="cred.id" :value="cred.id">
                    {{ cred.description }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- 构建触发器 -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="text-md font-medium text-gray-900 mb-4">⏰ 构建触发器</h3>
            <div class="space-y-3">
              <label class="flex items-center">
                <input 
                  type="checkbox" 
                  v-model="jobConfig.triggers.manual"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
                <span class="ml-2 text-sm text-gray-700">手动触发</span>
              </label>
              
              <div class="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  v-model="jobConfig.triggers.scm"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
                <span class="text-sm text-gray-700">代码变更触发</span>
                <input 
                  v-if="jobConfig.triggers.scm" 
                  v-model="jobConfig.triggers.scmSchedule"
                  type="text"
                  placeholder="H/5 * * * *"
                  class="ml-2 block w-32 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                />
              </div>
              
              <div class="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  v-model="jobConfig.triggers.cron"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
                <span class="text-sm text-gray-700">定时触发</span>
                <input 
                  v-if="jobConfig.triggers.cron" 
                  v-model="jobConfig.triggers.cronSchedule"
                  type="text"
                  placeholder="0 2 * * *"
                  class="ml-2 block w-32 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                />
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- 步骤3: 构建步骤 -->
      <div v-if="currentStep === 3" class="p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">构建步骤配置</h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 已添加的步骤 -->
          <div class="space-y-4">
            <h3 class="text-md font-medium text-gray-900">当前构建步骤</h3>
            
            <div v-if="jobConfig.buildSteps.length === 0" class="text-center py-8 text-gray-500 border-2 border-dashed border-gray-200 rounded-lg">
              <p>还没有添加构建步骤</p>
              <p class="text-xs">请从右侧选择需要的步骤类型</p>
            </div>
            
            <div v-else class="space-y-3">
              <div 
                v-for="(step, index) in jobConfig.buildSteps" 
                :key="step.id"
                class="border rounded-lg p-4 bg-white"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center space-x-2">
                    <span class="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs font-medium">
                      {{ index + 1 }}
                    </span>
                    <span class="font-medium text-gray-900">{{ step.title }}</span>
                  </div>
                  <div class="flex space-x-2">
                    <button 
                      @click="editBuildStep(index)"
                      class="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      编辑
                    </button>
                    <button 
                      @click="removeBuildStep(index)"
                      class="text-red-600 hover:text-red-800 text-sm"
                    >
                      删除
                    </button>
                  </div>
                </div>
                <div class="text-sm text-gray-600">
                  {{ getStepPreview(step) }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 步骤类型选择 -->
          <div class="space-y-4">
            <h3 class="text-md font-medium text-gray-900">添加构建步骤</h3>
            
            <div class="grid grid-cols-1 gap-3">
              <div 
                @click="addBuildStep('shell')"
                class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center space-x-3">
                  <div class="text-2xl">🖥️</div>
                  <div>
                    <h4 class="font-medium text-gray-900">执行Shell脚本</h4>
                    <p class="text-sm text-gray-600">运行bash/sh脚本命令</p>
                  </div>
                </div>
              </div>
              
              <div 
                @click="addBuildStep('docker')"
                class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center space-x-3">
                  <div class="text-2xl">🐳</div>
                  <div>
                    <h4 class="font-medium text-gray-900">Docker操作</h4>
                    <p class="text-sm text-gray-600">构建镜像、推送仓库、运行容器</p>
                  </div>
                </div>
              </div>
              
              <div 
                @click="addBuildStep('deploy')"
                class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center space-x-3">
                  <div class="text-2xl">🚀</div>
                  <div>
                    <h4 class="font-medium text-gray-900">部署操作</h4>
                    <p class="text-sm text-gray-600">SSH部署、K8s部署、文件传输</p>
                  </div>
                </div>
              </div>
              
              <div 
                @click="addBuildStep('test')"
                class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center space-x-3">
                  <div class="text-2xl">🧪</div>
                  <div>
                    <h4 class="font-medium text-gray-900">测试操作</h4>
                    <p class="text-sm text-gray-600">单元测试、集成测试、代码覆盖率</p>
                  </div>
                </div>
              </div>
              
              <div 
                @click="addBuildStep('notify')"
                class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center space-x-3">
                  <div class="text-2xl">📧</div>
                  <div>
                    <h4 class="font-medium text-gray-900">通知操作</h4>
                    <p class="text-sm text-gray-600">邮件通知、钉钉/企微通知</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤4: 预览和创建 -->
      <div v-if="currentStep === 4" class="p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">预览配置</h2>
        
        <div class="space-y-6">
          <!-- 配置预览 -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h3 class="text-md font-medium text-gray-900 mb-4">任务配置概览</h3>
            <dl class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt class="text-sm font-medium text-gray-500">任务名称</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ jobConfig.name }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">项目类型</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ jobConfig.projectType === 'freestyle' ? 'Freestyle Project' : 'Pipeline Project' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Git仓库</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ jobConfig.scm.url || '未配置' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">分支</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ jobConfig.scm.branch || '*/master' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">构建步骤</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ jobConfig.buildSteps.length }} 个步骤</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">触发器</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ getTriggersSummary() }}
                </dd>
              </div>
            </dl>
          </div>
          
          <!-- 构建步骤详情 -->
          <div v-if="jobConfig.buildSteps.length > 0" class="bg-gray-50 rounded-lg p-4">
            <h3 class="text-md font-medium text-gray-900 mb-4">构建步骤详情</h3>
            <div class="space-y-3">
              <div v-for="(step, index) in jobConfig.buildSteps" :key="step.id" class="bg-white rounded p-3">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs font-medium">
                    {{ index + 1 }}
                  </span>
                  <span class="font-medium text-gray-900">{{ step.title }}</span>
                </div>
                <div class="text-sm text-gray-600 ml-8">
                  {{ getStepPreview(step) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <div class="flex justify-between">
        <button 
          @click="prevStep"
          :disabled="currentStep === 1"
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← 上一步
        </button>
        
        <div class="flex space-x-3">
          <button 
            v-if="currentStep === 4"
            @click="previewConfig"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            📋 预览XML
          </button>
          
          <button 
            v-if="currentStep < totalSteps"
            @click="nextStep"
            :disabled="!canProceed"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一步 →
          </button>
          
          <button 
            v-if="currentStep === totalSteps"
            @click="createJob"
            :disabled="!canCreate || isLoading"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isEditMode ? '更新任务' : '创建任务' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 步骤编辑器 -->
    <StepEditor
      :show="showStepEditor"
      :step="editingStep"
      :is-edit-mode="editingStepIndex >= 0"
      @close="closeStepEditor"
      @save="saveStepEdit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CheckIcon } from '@heroicons/vue/24/solid'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'
import StepEditor from '@/components/jenkins/job-wizard/StepEditor.vue'

const route = useRoute()
const router = useRouter()

// 注入全局状态
const selectedInstance = inject('jenkinsInstance')

// 响应式状态
const currentStep = ref(1)
const isLoading = ref(false)
const isEditMode = ref(false)
const editingJobName = ref('')
const credentials = ref([])
const showStepEditor = ref(false)
const editingStep = ref({})
const editingStepIndex = ref(-1)

// 步骤配置
const steps = [
  { id: 1, title: '项目类型' },
  { id: 2, title: '基础配置' },  
  { id: 3, title: '构建步骤' },
  { id: 4, title: '预览创建' }
]

const totalSteps = steps.length

// 任务配置数据
const jobConfig = ref({
  projectType: '',
  name: '',
  description: '',
  scm: {
    url: '',
    branch: '*/master',
    credentials: ''
  },
  triggers: {
    manual: true,
    scm: false,
    scmSchedule: 'H/5 * * * *',
    cron: false,
    cronSchedule: '0 2 * * *'
  },
  buildSteps: []
})

// 计算属性
const isValidName = computed(() => {
  if (!jobConfig.value.name) return true
  return /^[a-zA-Z0-9_-]+$/.test(jobConfig.value.name)
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return jobConfig.value.projectType !== ''
    case 2:
      return jobConfig.value.name && isValidName.value
    case 3:
      return true // 构建步骤可以为空
    case 4:
      return true
    default:
      return false
  }
})

const canCreate = computed(() => {
  return jobConfig.value.name && 
         isValidName.value && 
         jobConfig.value.projectType &&
         selectedInstance.value
})

const hasSelectedInstance = computed(() => {
  return !!selectedInstance.value
})

// 方法
const selectProjectType = (type) => {
  jobConfig.value.projectType = type
}

const nextStep = () => {
  if (currentStep.value < totalSteps && canProceed.value) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const addBuildStep = (type) => {
  editingStepIndex.value = -1 // 新增模式
  editingStep.value = {
    id: Date.now(),
    type: type,
    title: getStepTitle(type),
    config: getDefaultStepConfig(type)
  }
  showStepEditor.value = true
}

const removeBuildStep = (index) => {
  jobConfig.value.buildSteps.splice(index, 1)
}

const editBuildStep = (index) => {
  editingStepIndex.value = index
  editingStep.value = { ...jobConfig.value.buildSteps[index] }
  showStepEditor.value = true
}

const getStepTitle = (type) => {
  const titles = {
    shell: 'Shell脚本执行',
    docker: 'Docker操作',
    deploy: '部署操作',
    test: '测试执行',
    notify: '通知发送'
  }
  return titles[type] || '未知步骤'
}

const getDefaultStepConfig = (type) => {
  const configs = {
    shell: { script: 'echo "Hello Jenkins"' },
    docker: { operation: 'build', imageName: '' },
    deploy: { type: 'ssh', target: '' },
    test: { framework: 'junit', path: 'test/' },
    notify: { type: 'email', recipients: '' }
  }
  return configs[type] || {}
}

const getStepPreview = (step) => {
  switch (step.type) {
    case 'shell':
      return `执行脚本: ${step.config.script || '未配置'}`
    case 'docker':
      return `Docker操作: ${step.config.operation || '未配置'}`
    case 'deploy':
      return `部署到: ${step.config.target || '未配置'}`
    case 'test':
      return `测试框架: ${step.config.framework || '未配置'}`
    case 'notify':
      return `通知方式: ${step.config.type || '未配置'}`
    default:
      return '未配置'
  }
}

const getTriggersSummary = () => {
  const triggers = []
  if (jobConfig.value.triggers.manual) triggers.push('手动')
  if (jobConfig.value.triggers.scm) triggers.push('代码变更')
  if (jobConfig.value.triggers.cron) triggers.push('定时')
  return triggers.length > 0 ? triggers.join(', ') : '无'
}

const previewConfig = () => {
  // 生成XML配置预览
  const xml = generateJobXML()
  notify.info(`
    <div class="text-left">
      <h3 class="text-lg font-semibold mb-3">生成的XML配置</h3>
      <pre class="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-64">${xml}</pre>
    </div>
  `, { 
    title: '配置预览',
    timeout: 0
  })
}

const generateJobXML = () => {
  // 简化的XML生成示例
  return `<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>${jobConfig.value.description || ''}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  ${jobConfig.value.scm.url ? `
  <scm class="hudson.plugins.git.GitSCM">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>${jobConfig.value.scm.url}</url>
        ${jobConfig.value.scm.credentials ? `<credentialsId>${jobConfig.value.scm.credentials}</credentialsId>` : ''}
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>${jobConfig.value.scm.branch}</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
  </scm>` : ''}
  <builders>
    ${jobConfig.value.buildSteps.map(step => {
      if (step.type === 'shell') {
        return `<hudson.tasks.Shell>
          <command>${step.config.script || ''}</command>
        </hudson.tasks.Shell>`
      }
      return `<!-- ${step.title} -->`
    }).join('\n    ')}
  </builders>
</project>`
}

const createJob = async () => {
  if (!selectedInstance.value) {
    notify.warning('请先选择Jenkins实例')
    return
  }
  
  isLoading.value = true
  try {
    const xml = generateJobXML()
    const url = isEditMode.value 
      ? `/ops/jenkins/jobs/${selectedInstance.value}/${editingJobName.value}`
      : `/ops/jenkins/jobs/${selectedInstance.value}`
    
    const response = await fetchApi(url, {
      method: isEditMode.value ? 'PUT' : 'POST',
      body: {
        name: jobConfig.value.name,
        xml: xml,
        description: jobConfig.value.description
      }
    })
    
    if (response.success) {
      notify.success(isEditMode.value ? '任务更新成功' : '任务创建成功')
      router.push({ name: 'jenkins-jobs' })
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('任务操作失败:', error)
    notify.error(`任务操作失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

// 初始化
onMounted(async () => {
  // 检查是否为编辑模式
  if (route.query.edit) {
    isEditMode.value = true
    editingJobName.value = route.query.edit
    // 加载现有任务配置
    await loadJobConfig(route.query.edit)
  }
  
  // 加载凭据列表
  await loadCredentials()
})

const loadJobConfig = async (jobName) => {
  // 加载现有任务配置的逻辑
  // 这里应该从Jenkins API获取任务配置
  notify.info('编辑模式将在后续版本中完善')
}

const loadCredentials = async () => {
  // 加载Jenkins凭据列表
  // 这里应该从Jenkins API获取凭据列表
  credentials.value = [
    { id: 'github-token', description: 'GitHub Token' },
    { id: 'gitlab-key', description: 'GitLab SSH Key' }
  ]
}

// 步骤编辑器处理方法
const closeStepEditor = () => {
  showStepEditor.value = false
  editingStep.value = {}
  editingStepIndex.value = -1
}

const saveStepEdit = (stepData) => {
  if (editingStepIndex.value >= 0) {
    // 编辑模式：更新现有步骤
    jobConfig.value.buildSteps[editingStepIndex.value] = stepData
  } else {
    // 新增模式：添加新步骤
    jobConfig.value.buildSteps.push(stepData)
  }
  closeStepEditor()
}
</script>

<style scoped>
/* 步骤动画 */
.step-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 项目类型选择卡片 */
.project-type-card {
  transition: all 0.2s ease-in-out;
}

.project-type-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 构建步骤卡片 */
.build-step-card {
  transition: all 0.2s ease-in-out;
}

.build-step-card:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>