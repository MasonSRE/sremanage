<template>
  <div class="stage-editor-container">
    <!-- 阶段编辑对话框 -->
    <TransitionRoot appear :show="show" as="template">
      <Dialog as="div" @close="closeEditor" class="relative z-50">
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
              <DialogPanel class="w-full max-w-3xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <div class="p-6">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                    {{ isEditMode ? '编辑阶段' : '添加阶段' }}
                  </DialogTitle>

                  <div class="space-y-6">
                    <!-- 基础配置 -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">阶段名称 *</label>
                      <input 
                        v-model="currentStage.name" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="例如：构建阶段"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">阶段描述</label>
                      <textarea 
                        v-model="currentStage.description" 
                        rows="2"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="描述这个阶段的作用..."
                      />
                    </div>

                    <!-- 执行条件 -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-3">执行条件</label>
                      <div class="space-y-2">
                        <label class="flex items-center">
                          <input type="radio" v-model="currentStage.when.type" value="always" class="rounded" />
                          <span class="ml-2 text-sm">总是执行</span>
                        </label>
                        <label class="flex items-center">
                          <input type="radio" v-model="currentStage.when.type" value="branch" class="rounded" />
                          <span class="ml-2 text-sm">特定分支</span>
                          <input 
                            v-if="currentStage.when.type === 'branch'"
                            v-model="currentStage.when.branch" 
                            type="text"
                            placeholder="master"
                            class="ml-2 block w-32 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                          />
                        </label>
                        <label class="flex items-center">
                          <input type="radio" v-model="currentStage.when.type" value="expression" class="rounded" />
                          <span class="ml-2 text-sm">表达式</span>
                          <input 
                            v-if="currentStage.when.type === 'expression'"
                            v-model="currentStage.when.expression" 
                            type="text"
                            placeholder="env.DEPLOY == 'true'"
                            class="ml-2 block w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                          />
                        </label>
                      </div>
                    </div>

                    <!-- 并行执行 -->
                    <div>
                      <div class="flex items-center justify-between mb-3">
                        <label class="text-sm font-medium text-gray-700">并行执行</label>
                        <button
                          @click="toggleParallel"
                          :class="[
                            'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                            currentStage.isParallel ? 'bg-blue-600' : 'bg-gray-200'
                          ]"
                        >
                          <span
                            :class="[
                              'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                              currentStage.isParallel ? 'translate-x-5' : 'translate-x-0'
                            ]"
                          />
                        </button>
                      </div>
                      
                      <div v-if="currentStage.isParallel" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div class="mb-4">
                          <div class="flex items-center justify-between mb-2">
                            <h4 class="text-sm font-medium text-gray-900">并行分支</h4>
                            <button
                              @click="addParallelBranch"
                              class="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              + 添加分支
                            </button>
                          </div>
                          
                          <div class="space-y-3">
                            <div 
                              v-for="(branch, index) in currentStage.parallel" 
                              :key="branch.id"
                              class="bg-white border rounded p-3"
                            >
                              <div class="flex items-center justify-between mb-2">
                                <input 
                                  v-model="branch.name" 
                                  type="text"
                                  placeholder="分支名称"
                                  class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                                />
                                <button
                                  @click="removeParallelBranch(index)"
                                  class="ml-2 text-red-600 hover:text-red-800 text-sm"
                                >
                                  删除
                                </button>
                              </div>
                              
                              <div class="space-y-1">
                                <div v-for="step in branch.steps" :key="step.id" class="text-xs text-gray-600 pl-2">
                                  • {{ step.name }}
                                </div>
                                <button
                                  @click="addBranchStep(index)"
                                  class="text-blue-600 hover:text-blue-800 text-xs"
                                >
                                  + 添加步骤
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 普通步骤 -->
                    <div v-if="!currentStage.isParallel">
                      <div class="flex items-center justify-between mb-3">
                        <label class="text-sm font-medium text-gray-700">执行步骤</label>
                        <button
                          @click="addStep"
                          class="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          + 添加步骤
                        </button>
                      </div>
                      
                      <div class="space-y-3">
                        <div 
                          v-for="(step, index) in currentStage.steps" 
                          :key="step.id"
                          class="border rounded p-3 bg-gray-50"
                        >
                          <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center space-x-2">
                              <select 
                                v-model="step.type"
                                class="text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              >
                                <option value="echo">Echo</option>
                                <option value="sh">Shell命令</option>
                                <option value="script">Groovy脚本</option>
                                <option value="checkout">检出代码</option>
                                <option value="build">构建</option>
                                <option value="test">测试</option>
                                <option value="deploy">部署</option>
                              </select>
                              <input 
                                v-model="step.name" 
                                type="text"
                                placeholder="步骤名称"
                                class="flex-1 text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              />
                            </div>
                            <button
                              @click="removeStep(index)"
                              class="text-red-600 hover:text-red-800 text-sm"
                            >
                              删除
                            </button>
                          </div>
                          
                          <!-- 步骤配置 -->
                          <div v-if="step.type === 'echo'">
                            <input 
                              v-model="step.message" 
                              type="text"
                              placeholder="输出消息"
                              class="w-full text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                          </div>
                          
                          <div v-else-if="step.type === 'sh'">
                            <textarea 
                              v-model="step.script" 
                              rows="3"
                              placeholder="#!/bin/bash
echo 'Running shell command...'"
                              class="w-full text-sm font-mono rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                          </div>
                          
                          <div v-else-if="step.type === 'script'">
                            <textarea 
                              v-model="step.script" 
                              rows="3"
                              placeholder="// Groovy script
def result = sh(script: 'echo hello', returnStdout: true)
echo result"
                              class="w-full text-sm font-mono rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                          </div>
                          
                          <div v-else-if="step.type === 'checkout'">
                            <div class="text-sm text-gray-600">检出SCM中的代码</div>
                          </div>
                        </div>
                        
                        <div v-if="currentStage.steps.length === 0" class="text-center py-4 text-gray-500 border-2 border-dashed border-gray-200 rounded">
                          点击上方"添加步骤"按钮来添加执行步骤
                        </div>
                      </div>
                    </div>

                    <!-- Post处理 -->
                    <div>
                      <div class="flex items-center justify-between mb-3">
                        <label class="text-sm font-medium text-gray-700">Post处理</label>
                        <button
                          @click="showPostActions = !showPostActions"
                          class="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          {{ showPostActions ? '隐藏' : '显示' }}
                        </button>
                      </div>
                      
                      <div v-show="showPostActions" class="bg-gray-50 rounded-lg p-4 space-y-3">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Always (总是执行)</label>
                          <textarea 
                            v-model="currentStage.post.always" 
                            rows="2"
                            placeholder="echo 'Stage completed'"
                            class="w-full text-sm font-mono rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          />
                        </div>
                        
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Success (成功时执行)</label>
                          <textarea 
                            v-model="currentStage.post.success" 
                            rows="2"
                            placeholder="echo 'Stage succeeded'"
                            class="w-full text-sm font-mono rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          />
                        </div>
                        
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Failure (失败时执行)</label>
                          <textarea 
                            v-model="currentStage.post.failure" 
                            rows="2"
                            placeholder="echo 'Stage failed'"
                            class="w-full text-sm font-mono rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
                      @click="closeEditor"
                    >
                      取消
                    </button>
                    <button
                      type="button"
                      class="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700"
                      @click="saveStage"
                      :disabled="!currentStage.name.trim()"
                    >
                      {{ isEditMode ? '更新阶段' : '添加阶段' }}
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
</template>

<script setup>
import { ref, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  stage: {
    type: Object,
    default: () => ({})
  },
  isEditMode: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// State
const showPostActions = ref(false)
const currentStage = ref({
  id: null,
  name: '',
  description: '',
  when: {
    type: 'always',
    branch: '',
    expression: ''
  },
  isParallel: false,
  steps: [],
  parallel: [],
  post: {
    always: '',
    success: '',
    failure: ''
  }
})

// 方法
const getDefaultStage = () => ({
  id: Date.now(),
  name: '',
  description: '',
  when: {
    type: 'always',
    branch: '',
    expression: ''
  },
  isParallel: false,
  steps: [],
  parallel: [],
  post: {
    always: '',
    success: '',
    failure: ''
  }
})

const getDefaultStep = (type = 'echo') => ({
  id: Date.now(),
  type: type,
  name: '',
  message: '',
  script: ''
})

const getDefaultParallelBranch = () => ({
  id: Date.now(),
  name: '',
  steps: []
})

const toggleParallel = () => {
  currentStage.value.isParallel = !currentStage.value.isParallel
  
  if (currentStage.value.isParallel && currentStage.value.parallel.length === 0) {
    // 初始化两个并行分支
    currentStage.value.parallel = [
      { ...getDefaultParallelBranch(), name: '分支A' },
      { ...getDefaultParallelBranch(), name: '分支B' }
    ]
  }
}

const addParallelBranch = () => {
  currentStage.value.parallel.push({
    ...getDefaultParallelBranch(),
    name: `分支${currentStage.value.parallel.length + 1}`
  })
}

const removeParallelBranch = (index) => {
  currentStage.value.parallel.splice(index, 1)
}

const addBranchStep = (branchIndex) => {
  const step = {
    ...getDefaultStep(),
    name: '新步骤'
  }
  currentStage.value.parallel[branchIndex].steps.push(step)
}

const addStep = () => {
  const step = {
    ...getDefaultStep(),
    name: '新步骤'
  }
  currentStage.value.steps.push(step)
}

const removeStep = (index) => {
  currentStage.value.steps.splice(index, 1)
}

const closeEditor = () => {
  emit('close')
}

const saveStage = () => {
  if (!currentStage.value.name.trim()) {
    return
  }
  
  emit('save', { ...currentStage.value })
}

// 监听props变化
watch(() => props.stage, (newStage) => {
  if (newStage && Object.keys(newStage).length > 0) {
    currentStage.value = {
      ...getDefaultStage(),
      ...newStage
    }
  } else {
    currentStage.value = getDefaultStage()
  }
}, { immediate: true, deep: true })

// 监听显示状态
watch(() => props.show, (show) => {
  if (show) {
    showPostActions.value = false
  }
})
</script>

<style scoped>
/* 代码编辑器样式 */
textarea[class*="font-mono"] {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .space-y-3 > div {
    margin-top: 0.5rem;
  }
}
</style>