<template>
  <div class="pipeline-wizard">
    <!-- 模板选择 -->
    <div v-if="!selectedTemplate" class="template-selection">
      <h3 class="text-lg font-semibold text-gray-900 mb-6">选择Pipeline模板</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div 
          v-for="template in pipelineTemplates" 
          :key="template.id"
          @click="selectTemplate(template)"
          class="template-card cursor-pointer border-2 border-gray-200 rounded-lg p-6 hover:border-blue-500 hover:bg-blue-50 transition-all"
        >
          <div class="flex items-center mb-4">
            <div class="text-3xl mr-4">{{ template.icon }}</div>
            <div>
              <h4 class="text-lg font-semibold text-gray-900">{{ template.name }}</h4>
              <p class="text-gray-600">{{ template.description }}</p>
            </div>
          </div>
          
          <!-- 模板流程预览 -->
          <div class="template-preview bg-gray-50 rounded p-3 mb-4">
            <div class="flex items-center text-sm text-gray-600 space-x-2">
              <span v-for="(stage, index) in template.preview" :key="index" class="flex items-center">
                <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">{{ stage }}</span>
                <svg v-if="index < template.preview.length - 1" class="w-4 h-4 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </span>
            </div>
          </div>
          
          <!-- 模板标签 -->
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="tag in template.tags" 
              :key="tag"
              class="px-2 py-1 bg-gray-200 text-gray-700 rounded-full text-xs"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="mt-6 text-center">
        <button
          @click="selectTemplate({ id: 'custom', name: '自定义Pipeline', script: '' })"
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          🛠️ 从空白开始创建
        </button>
      </div>
    </div>

    <!-- Pipeline编辑器 -->
    <div v-else class="pipeline-editor">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold text-gray-900">
          Pipeline配置 - {{ selectedTemplate.name }}
        </h3>
        <button
          @click="backToTemplates"
          class="text-blue-600 hover:text-blue-800 text-sm"
        >
          ← 返回模板选择
        </button>
      </div>

      <!-- 编辑器标签 -->
      <div class="border-b border-gray-200 mb-6">
        <nav class="flex space-x-8" aria-label="Tabs">
          <button
            @click="activeTab = 'visual'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'visual'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🎨 可视化编辑
          </button>
          <button
            @click="activeTab = 'code'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'code'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            📝 代码编辑
          </button>
        </nav>
      </div>

      <!-- 可视化编辑器 -->
      <div v-if="activeTab === 'visual'" class="visual-editor">
        <div class="bg-white border rounded-lg p-6">
          <div class="pipeline-canvas">
            <div class="stages-container space-y-4">
              <div 
                v-for="(stage, index) in pipeline.stages" 
                :key="stage.id"
                class="stage-node border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                @click="editStage(index)"
              >
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600 mr-3">
                      {{ index + 1 }}
                    </div>
                    <h4 class="font-medium text-gray-900">{{ stage.name }}</h4>
                  </div>
                  <div class="flex space-x-2">
                    <button @click.stop="editStage(index)" class="text-blue-600 hover:text-blue-800 text-sm">
                      ✏️
                    </button>
                    <button @click.stop="deleteStage(index)" class="text-red-600 hover:text-red-800 text-sm">
                      🗑️
                    </button>
                  </div>
                </div>
                
                <!-- 阶段步骤 -->
                <div class="stage-steps">
                  <div v-if="stage.steps.length === 0" class="text-gray-500 text-sm italic">
                    点击添加步骤
                  </div>
                  <div v-else class="space-y-2">
                    <div 
                      v-for="step in stage.steps" 
                      :key="step.id"
                      class="flex items-center text-sm bg-gray-50 rounded px-3 py-2"
                    >
                      <span class="mr-2">{{ getStepIcon(step.type) }}</span>
                      <span class="flex-1">{{ step.name }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- 并行分支 -->
                <div v-if="stage.parallel" class="parallel-branches mt-4 border-t pt-4">
                  <div class="text-sm text-gray-600 mb-2">并行执行:</div>
                  <div class="grid grid-cols-2 gap-4">
                    <div 
                      v-for="branch in stage.parallel" 
                      :key="branch.id"
                      class="border rounded p-3 bg-yellow-50"
                    >
                      <h5 class="font-medium text-sm text-gray-900 mb-2">{{ branch.name }}</h5>
                      <div class="space-y-1">
                        <div v-for="step in branch.steps" :key="step.id" class="text-xs text-gray-600">
                          {{ step.name }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 添加阶段按钮 -->
            <div class="text-center mt-6">
              <button 
                @click="addStage"
                class="inline-flex items-center px-4 py-2 border border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-300 hover:text-blue-600 transition-colors"
              >
                ➕ 添加阶段
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 代码编辑器 -->
      <div v-else class="code-editor">
        <div class="bg-white border rounded-lg">
          <!-- 编辑器工具栏 -->
          <div class="border-b border-gray-200 px-4 py-3 flex items-center justify-between">
            <div class="flex space-x-3">
              <button @click="formatCode" class="text-sm text-gray-600 hover:text-gray-900">
                格式化
              </button>
              <button @click="validateSyntax" class="text-sm text-gray-600 hover:text-gray-900">
                语法检查
              </button>
              <button @click="syncFromVisual" class="text-sm text-gray-600 hover:text-gray-900">
                从可视化同步
              </button>
            </div>
            <div class="text-sm text-gray-500">
              Jenkinsfile (Groovy)
            </div>
          </div>
          
          <!-- 代码编辑区域 -->
          <div class="relative">
            <textarea
              v-model="pipelineCode"
              @input="onCodeChange"
              class="w-full h-96 p-4 font-mono text-sm border-0 resize-none focus:ring-0 focus:outline-none"
              placeholder="pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
    }
}"
              spellcheck="false"
            />
          </div>
          
          <!-- 语法错误显示 -->
          <div v-if="syntaxErrors.length > 0" class="border-t border-red-200 bg-red-50 p-4">
            <h4 class="text-sm font-medium text-red-800">语法错误:</h4>
            <div class="mt-2 space-y-1">
              <div v-for="error in syntaxErrors" :key="error.line" class="text-sm text-red-700">
                <span class="font-medium">第{{ error.line }}行:</span>
                <span class="ml-2">{{ error.message }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="mt-6 flex justify-between">
        <button
          @click="backToTemplates"
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          ← 返回模板选择
        </button>
        <div class="flex space-x-3">
          <button
            @click="previewPipeline"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            👁️ 预览
          </button>
          <button
            @click="savePipeline"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            💾 保存Pipeline
          </button>
        </div>
      </div>
    </div>

    <!-- 阶段编辑对话框 -->
    <StageEditor
      :show="showStageEditor"
      :stage="editingStage"
      :is-edit-mode="editingStageIndex >= 0"
      @close="closeStageEditor"
      @save="saveStageEdit"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import StageEditor from './StageEditor.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'save'])

// State
const selectedTemplate = ref(null)
const activeTab = ref('visual')
const pipelineCode = ref('')
const syntaxErrors = ref([])
const showStageEditor = ref(false)
const editingStage = ref({})
const editingStageIndex = ref(-1)

// Pipeline数据
const pipeline = ref({
  stages: []
})

// 模板数据
const pipelineTemplates = ref([
  {
    id: 'basic',
    name: '基础Pipeline',
    description: '检出 → 构建 → 测试 → 部署',
    icon: '🔄',
    preview: ['检出代码', '构建', '测试', '部署'],
    tags: ['基础', '通用'],
    script: `pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building...'
                // 添加你的构建命令
            }
        }
        
        stage('Test') {
            steps {
                echo 'Testing...'
                // 添加你的测试命令
            }
            post {
                always {
                    // 发布测试结果
                    echo 'Publishing test results...'
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'master'
            }
            steps {
                echo 'Deploying...'
                // 添加你的部署命令
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}`
  },
  {
    id: 'nodejs',
    name: 'Node.js项目',
    description: 'npm install → lint → test → build → deploy',
    icon: '📦',
    preview: ['安装依赖', '代码检查', '运行测试', '构建', '部署'],
    tags: ['npm', 'docker', 'k8s'],
    script: `pipeline {
    agent any
    
    tools {
        nodejs '16'
    }
    
    environment {
        NPM_CONFIG_CACHE = "${WORKSPACE}/.npm"
        NODE_ENV = 'production'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Node.js dependencies...'
                sh '''
                    node --version
                    npm --version
                    npm ci --prefer-offline --no-audit
                '''
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('ESLint') {
                    steps {
                        sh 'npm run lint'
                    }
                }
                
                stage('Type Check') {
                    when {
                        expression { fileExists('tsconfig.json') }
                    }
                    steps {
                        sh 'npm run type-check'
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'test-results.xml'
                }
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                sh 'npm run build'
            }
            post {
                success {
                    archiveArtifacts artifacts: 'dist/**/*', fingerprint: true
                }
            }
        }
        
        stage('Docker Build & Push') {
            when {
                anyOf {
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def imageTag = env.BRANCH_NAME == 'master' ? 'latest' : env.BRANCH_NAME
                    def image = docker.build("myapp:${BUILD_NUMBER}")
                    
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-credentials') {
                        image.push("${BUILD_NUMBER}")
                        image.push(imageTag)
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'master'
            }
            steps {
                echo 'Deploying to production...'
                sh '''
                    kubectl set image deployment/myapp myapp=myapp:${BUILD_NUMBER} -n production
                    kubectl rollout status deployment/myapp -n production
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed!'
        }
    }
}`
  },
  {
    id: 'java',
    name: 'Java项目',
    description: 'maven compile → test → package → docker → deploy',
    icon: '☕',
    preview: ['编译', '测试', '打包', 'Docker构建', '部署'],
    tags: ['maven', 'junit', 'spring'],
    script: `pipeline {
    agent any
    
    tools {
        maven 'Maven-3.8'
        jdk 'JDK-11'
    }
    
    environment {
        MAVEN_OPTS = '-Xmx1024m'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Compile') {
            steps {
                echo 'Compiling...'
                sh 'mvn clean compile'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'mvn test'
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'target/surefire-reports/*.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'target/site/jacoco',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('Package') {
            steps {
                echo 'Packaging...'
                sh 'mvn package -DskipTests'
            }
            post {
                success {
                    archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
                }
            }
        }
        
        stage('Docker Build') {
            when {
                anyOf {
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def image = docker.build("myapp:${BUILD_NUMBER}")
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-credentials') {
                        image.push("${BUILD_NUMBER}")
                        image.push("latest")
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'master'
            }
            steps {
                echo 'Deploying to production...'
                // 添加部署脚本
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}`
  },
  {
    id: 'python',
    name: 'Python项目',
    description: 'pip install → lint → test → package → deploy',
    icon: '🐍',
    preview: ['安装依赖', '代码检查', '运行测试', '打包', '部署'],
    tags: ['pytest', 'flake8', 'requirements'],
    script: `pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                echo 'Setting up Python environment...'
                sh '''
                    python3 --version
                    pip --version
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Lint') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    flake8 .
                    black --check .
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    pytest --cov=. --cov-report=xml --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'test-results.xml'
                    publishCoverageGlobally([
                        coberturaReportFile: 'coverage.xml'
                    ])
                }
            }
        }
        
        stage('Package') {
            steps {
                echo 'Building package...'
                sh '''
                    python setup.py sdist bdist_wheel
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'dist/*', fingerprint: true
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'master'
            }
            steps {
                echo 'Deploying...'
                // 添加部署脚本
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}`
  }
])

// 方法
const selectTemplate = (template) => {
  selectedTemplate.value = template
  pipelineCode.value = template.script || ''
  
  // 如果有预定义的阶段，初始化可视化编辑器
  if (template.preview) {
    pipeline.value.stages = template.preview.map((stageName, index) => ({
      id: Date.now() + index,
      name: stageName,
      steps: []
    }))
  }
}

const backToTemplates = () => {
  selectedTemplate.value = null
  pipelineCode.value = ''
  pipeline.value.stages = []
  syntaxErrors.value = []
}

const addStage = () => {
  editingStageIndex.value = -1
  editingStage.value = {
    id: Date.now(),
    name: '新阶段',
    steps: []
  }
  showStageEditor.value = true
}

const editStage = (index) => {
  editingStageIndex.value = index
  editingStage.value = { ...pipeline.value.stages[index] }
  showStageEditor.value = true
}

const deleteStage = (index) => {
  pipeline.value.stages.splice(index, 1)
  syncToCode()
}

const closeStageEditor = () => {
  showStageEditor.value = false
  editingStage.value = {}
  editingStageIndex.value = -1
}

const saveStageEdit = (stageData) => {
  if (editingStageIndex.value >= 0) {
    pipeline.value.stages[editingStageIndex.value] = stageData
  } else {
    pipeline.value.stages.push(stageData)
  }
  closeStageEditor()
  syncToCode()
}

const getStepIcon = (type) => {
  const icons = {
    shell: '🖥️',
    docker: '🐳',
    test: '🧪',
    deploy: '🚀',
    build: '🔨'
  }
  return icons[type] || '📋'
}

const formatCode = () => {
  // 简单的格式化逻辑
  const lines = pipelineCode.value.split('\n')
  let formatted = ''
  let indent = 0
  
  lines.forEach(line => {
    const trimmed = line.trim()
    if (trimmed.includes('}')) indent = Math.max(0, indent - 1)
    
    formatted += '    '.repeat(indent) + trimmed + '\n'
    
    if (trimmed.includes('{')) indent++
  })
  
  pipelineCode.value = formatted
}

const validateSyntax = () => {
  syntaxErrors.value = []
  
  // 基础语法检查
  const lines = pipelineCode.value.split('\n')
  lines.forEach((line, index) => {
    if (line.includes('pipeline') && !line.includes('{')) {
      syntaxErrors.value.push({
        line: index + 1,
        message: 'pipeline块必须包含开放大括号'
      })
    }
  })
  
  // 检查大括号匹配
  let braceCount = 0
  lines.forEach((line, index) => {
    braceCount += (line.match(/\{/g) || []).length
    braceCount -= (line.match(/\}/g) || []).length
    
    if (braceCount < 0) {
      syntaxErrors.value.push({
        line: index + 1,
        message: '多余的闭合大括号'
      })
    }
  })
  
  if (braceCount > 0) {
    syntaxErrors.value.push({
      line: lines.length,
      message: '缺少闭合大括号'
    })
  }
}

const syncFromVisual = () => {
  // 从可视化编辑器同步到代码编辑器
  let script = `pipeline {
    agent any
    
    stages {`
  
  pipeline.value.stages.forEach(stage => {
    script += `
        stage('${stage.name}') {
            steps {`
    
    if (stage.steps.length === 0) {
      script += `
                echo 'Running ${stage.name}...'`
    } else {
      stage.steps.forEach(step => {
        script += `
                echo '${step.name}'`
      })
    }
    
    script += `
            }
        }`
  })
  
  script += `
    }
    
    post {
        always {
            cleanWs()
        }
    }
}`
  
  pipelineCode.value = script
}

const syncToCode = () => {
  // 简化版本的可视化到代码同步
  syncFromVisual()
}

const onCodeChange = () => {
  // 当代码改变时，可以选择实时验证
  // validateSyntax()
}

const previewPipeline = () => {
  validateSyntax()
  // 可以在这里添加更详细的预览逻辑
}

const savePipeline = () => {
  const pipelineData = {
    template: selectedTemplate.value?.id || 'custom',
    script: pipelineCode.value,
    visualStages: pipeline.value.stages
  }
  
  emit('save', pipelineData)
}

// 监听激活标签变化
watch(activeTab, (newTab) => {
  if (newTab === 'code' && pipeline.value.stages.length > 0) {
    syncFromVisual()
  }
})
</script>

<style scoped>
/* 模板卡片样式 */
.template-card {
  transition: all 0.2s ease-in-out;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 阶段节点样式 */
.stage-node {
  transition: all 0.2s ease-in-out;
}

.stage-node:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 代码编辑器样式 */
textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.5;
}

/* 滚动条样式 */
textarea::-webkit-scrollbar {
  width: 8px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  
  .parallel-branches .grid {
    grid-template-columns: 1fr;
  }
}
</style>