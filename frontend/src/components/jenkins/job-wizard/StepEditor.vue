<template>
  <div class="step-editor-container">
    <!-- 步骤编辑对话框 -->
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
              <DialogPanel class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <div class="p-6">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                    {{ isEditMode ? '编辑构建步骤' : '添加构建步骤' }} - {{ getStepTypeName(currentStep.type) }}
                  </DialogTitle>

                  <!-- Shell脚本步骤编辑器 -->
                  <div v-if="currentStep.type === 'shell'" class="space-y-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">步骤名称</label>
                      <input 
                        v-model="currentStep.title" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="例如：编译项目"
                      />
                    </div>

                    <!-- 常用模板选择 -->
                    <div class="bg-gray-50 rounded-lg p-4">
                      <h4 class="text-sm font-medium text-gray-900 mb-3">选择模板（可选）</h4>
                      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <button 
                          v-for="template in shellTemplates" 
                          :key="template.id"
                          @click="loadShellTemplate(template)"
                          class="p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm"
                        >
                          <div class="text-lg mb-1">{{ template.icon }}</div>
                          <div class="font-medium">{{ template.name }}</div>
                        </button>
                      </div>
                    </div>

                    <!-- 脚本编辑器 -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Shell脚本内容</label>
                      <div class="border border-gray-300 rounded-md">
                        <textarea
                          v-model="currentStep.config.script"
                          rows="12"
                          class="block w-full font-mono text-sm rounded-md border-0 focus:ring-2 focus:ring-blue-500 resize-none"
                          placeholder="#!/bin/bash
# 在这里输入你的Shell脚本
echo '开始构建...'

# 示例：Node.js项目构建
# npm install
# npm run test
# npm run build

echo '构建完成！'"
                          spellcheck="false"
                        />
                      </div>
                      <p class="mt-1 text-xs text-gray-500">支持所有标准的Shell命令和环境变量</p>
                    </div>

                    <!-- 高级选项 -->
                    <div class="border-t pt-4">
                      <button
                        @click="showAdvancedOptions = !showAdvancedOptions"
                        class="flex items-center text-sm text-gray-600 hover:text-gray-900"
                      >
                        <ChevronRightIcon 
                          :class="['w-4 h-4 mr-1 transition-transform', showAdvancedOptions ? 'rotate-90' : '']"
                        />
                        高级选项
                      </button>
                      
                      <div v-show="showAdvancedOptions" class="mt-4 space-y-4 bg-gray-50 rounded-lg p-4">
                        <div class="flex items-center">
                          <input 
                            type="checkbox" 
                            v-model="currentStep.config.continueOnError"
                            class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                          />
                          <label class="ml-2 text-sm text-gray-700">脚本失败时继续执行后续步骤</label>
                        </div>
                        
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">工作目录</label>
                          <input 
                            v-model="currentStep.config.workingDir" 
                            type="text"
                            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            placeholder="留空使用默认工作目录"
                          />
                        </div>
                        
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">环境变量</label>
                          <div class="space-y-2">
                            <div v-for="(env, index) in currentStep.config.envVars" :key="index" class="flex space-x-2">
                              <input 
                                v-model="env.name" 
                                type="text"
                                placeholder="变量名"
                                class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              />
                              <input 
                                v-model="env.value" 
                                type="text"
                                placeholder="变量值"
                                class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              />
                              <button 
                                @click="removeEnvVar(index)"
                                class="px-3 py-2 text-red-600 hover:text-red-800"
                              >
                                删除
                              </button>
                            </div>
                            <button 
                              @click="addEnvVar"
                              class="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              + 添加环境变量
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Docker操作步骤编辑器 -->
                  <div v-else-if="currentStep.type === 'docker'" class="space-y-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">步骤名称</label>
                      <input 
                        v-model="currentStep.title" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="例如：构建Docker镜像"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">操作类型</label>
                      <select 
                        v-model="currentStep.config.operation" 
                        @change="onDockerOperationChange"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="build">构建Docker镜像</option>
                        <option value="push">推送镜像到仓库</option>
                        <option value="run">运行Docker容器</option>
                        <option value="compose">Docker Compose操作</option>
                      </select>
                    </div>

                    <!-- 构建镜像配置 -->
                    <div v-if="currentStep.config.operation === 'build'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">镜像名称和标签</label>
                        <input 
                          v-model="currentStep.config.imageName" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="例如：myapp:${BUILD_NUMBER}"
                        />
                        <p class="mt-1 text-xs text-gray-500">支持Jenkins环境变量，如 ${BUILD_NUMBER}, ${GIT_COMMIT}</p>
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Dockerfile路径</label>
                        <input 
                          v-model="currentStep.config.dockerfilePath" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="./Dockerfile"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">构建上下文路径</label>
                        <input 
                          v-model="currentStep.config.contextPath" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="."
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">构建参数</label>
                        <div class="space-y-2">
                          <div v-for="(arg, index) in currentStep.config.buildArgs" :key="index" class="flex space-x-2">
                            <input 
                              v-model="arg.key" 
                              type="text"
                              placeholder="参数名"
                              class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                            <input 
                              v-model="arg.value" 
                              type="text"
                              placeholder="参数值"
                              class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                            <button 
                              @click="removeBuildArg(index)"
                              class="px-3 py-2 text-red-600 hover:text-red-800"
                            >
                              删除
                            </button>
                          </div>
                          <button 
                            @click="addBuildArg"
                            class="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            + 添加构建参数
                          </button>
                        </div>
                      </div>
                    </div>

                    <!-- 推送镜像配置 -->
                    <div v-else-if="currentStep.config.operation === 'push'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">镜像仓库地址</label>
                        <input 
                          v-model="currentStep.config.registryUrl" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="例如：registry.cn-hangzhou.aliyuncs.com"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">认证凭据</label>
                        <select 
                          v-model="currentStep.config.registryCredentials"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                          <option value="">选择Docker仓库凭据</option>
                          <option v-for="cred in dockerCredentials" :key="cred.id" :value="cred.id">
                            {{ cred.description }}
                          </option>
                        </select>
                      </div>
                    </div>

                    <!-- 运行容器配置 -->
                    <div v-else-if="currentStep.config.operation === 'run'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">容器名称</label>
                        <input 
                          v-model="currentStep.config.containerName" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="例如：myapp-test"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">端口映射</label>
                        <input 
                          v-model="currentStep.config.portMapping" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="例如：8080:80"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">挂载卷</label>
                        <textarea 
                          v-model="currentStep.config.volumes" 
                          rows="3"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="每行一个挂载配置，例如：
/host/path:/container/path
/var/log:/app/logs"
                        />
                      </div>
                    </div>
                  </div>

                  <!-- 部署操作步骤编辑器 -->
                  <div v-else-if="currentStep.type === 'deploy'" class="space-y-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">步骤名称</label>
                      <input 
                        v-model="currentStep.title" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="例如：部署到生产环境"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">部署类型</label>
                      <select 
                        v-model="currentStep.config.deployType" 
                        @change="onDeployTypeChange"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="ssh">SSH远程部署</option>
                        <option value="k8s">Kubernetes部署</option>
                        <option value="docker-swarm">Docker Swarm部署</option>
                        <option value="file-copy">文件传输</option>
                      </select>
                    </div>

                    <!-- SSH部署配置 -->
                    <div v-if="currentStep.config.deployType === 'ssh'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">目标服务器</label>
                        <input 
                          v-model="currentStep.config.sshHost" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="例如：192.168.1.100 或 server.example.com"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">SSH凭据</label>
                        <select 
                          v-model="currentStep.config.sshCredentials"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                          <option value="">选择SSH凭据</option>
                          <option v-for="cred in sshCredentials" :key="cred.id" :value="cred.id">
                            {{ cred.description }}
                          </option>
                        </select>
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">部署脚本</label>
                        <textarea 
                          v-model="currentStep.config.deployScript" 
                          rows="10"
                          class="block w-full font-mono text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="#!/bin/bash
# SSH部署脚本示例
echo '开始部署...'

# 停止旧服务
sudo systemctl stop myapp

# 备份当前版本
sudo cp -r /opt/myapp /opt/myapp.backup.$(date +%Y%m%d_%H%M%S)

# 启动新服务
sudo systemctl start myapp
sudo systemctl enable myapp

echo '部署完成！'"
                        />
                      </div>
                    </div>

                    <!-- K8s部署配置 -->
                    <div v-else-if="currentStep.config.deployType === 'k8s'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Kubernetes配置</label>
                        <select 
                          v-model="currentStep.config.k8sConfig"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                          <option value="">选择K8s集群配置</option>
                          <option v-for="config in k8sConfigs" :key="config.id" :value="config.id">
                            {{ config.name }} ({{ config.cluster }})
                          </option>
                        </select>
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">命名空间</label>
                        <input 
                          v-model="currentStep.config.namespace" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="default"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">部署方式</label>
                        <div class="space-y-2">
                          <label class="flex items-center">
                            <input type="radio" v-model="currentStep.config.k8sMethod" value="kubectl" class="rounded" />
                            <span class="ml-2">kubectl命令</span>
                          </label>
                          <label class="flex items-center">
                            <input type="radio" v-model="currentStep.config.k8sMethod" value="yaml" class="rounded" />
                            <span class="ml-2">YAML文件</span>
                          </label>
                          <label class="flex items-center">
                            <input type="radio" v-model="currentStep.config.k8sMethod" value="helm" class="rounded" />
                            <span class="ml-2">Helm Chart</span>
                          </label>
                        </div>
                      </div>

                      <!-- kubectl命令方式 -->
                      <div v-if="currentStep.config.k8sMethod === 'kubectl'">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Kubectl命令</label>
                        <textarea 
                          v-model="currentStep.config.kubectlCommands" 
                          rows="8"
                          class="block w-full font-mono text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="# Kubernetes部署命令示例
# 更新镜像
kubectl set image deployment/myapp myapp=${DOCKER_REGISTRY}/myapp:${BUILD_NUMBER} -n ${NAMESPACE}

# 等待部署完成
kubectl rollout status deployment/myapp -n ${NAMESPACE}

# 验证部署
kubectl get pods -n ${NAMESPACE} -l app=myapp"
                        />
                      </div>

                      <!-- YAML文件方式 -->
                      <div v-else-if="currentStep.config.k8sMethod === 'yaml'">
                        <label class="block text-sm font-medium text-gray-700 mb-1">YAML文件路径</label>
                        <input 
                          v-model="currentStep.config.yamlPath" 
                          type="text"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="k8s/deployment.yaml"
                        />
                      </div>

                      <!-- Helm方式 -->
                      <div v-else-if="currentStep.config.k8sMethod === 'helm'" class="space-y-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Chart路径</label>
                          <input 
                            v-model="currentStep.config.chartPath" 
                            type="text"
                            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            placeholder="./helm-chart"
                          />
                        </div>
                        
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">Release名称</label>
                          <input 
                            v-model="currentStep.config.releaseName" 
                            type="text"
                            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            placeholder="myapp-${BUILD_NUMBER}"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 测试操作步骤编辑器 -->
                  <div v-else-if="currentStep.type === 'test'" class="space-y-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">步骤名称</label>
                      <input 
                        v-model="currentStep.title" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="例如：运行单元测试"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">测试框架</label>
                      <select 
                        v-model="currentStep.config.framework"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="junit">JUnit (Java)</option>
                        <option value="pytest">PyTest (Python)</option>
                        <option value="jest">Jest (JavaScript)</option>
                        <option value="mocha">Mocha (JavaScript)</option>
                        <option value="phpunit">PHPUnit (PHP)</option>
                        <option value="custom">自定义</option>
                      </select>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">测试路径</label>
                      <input 
                        v-model="currentStep.config.testPath" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="test/"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">测试命令</label>
                      <input 
                        v-model="currentStep.config.testCommand" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="npm test"
                      />
                    </div>

                    <div class="flex items-center">
                      <input 
                        type="checkbox" 
                        v-model="currentStep.config.generateReports"
                        class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      />
                      <label class="ml-2 text-sm text-gray-700">生成测试报告</label>
                    </div>

                    <div v-if="currentStep.config.generateReports">
                      <label class="block text-sm font-medium text-gray-700 mb-1">报告输出路径</label>
                      <input 
                        v-model="currentStep.config.reportPath" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="reports/"
                      />
                    </div>
                  </div>

                  <!-- 通知操作步骤编辑器 -->
                  <div v-else-if="currentStep.type === 'notify'" class="space-y-6">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">步骤名称</label>
                      <input 
                        v-model="currentStep.title" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="例如：发送构建通知"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">通知类型</label>
                      <select 
                        v-model="currentStep.config.notifyType"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="email">邮件通知</option>
                        <option value="dingtalk">钉钉通知</option>
                        <option value="wechat">企业微信通知</option>
                        <option value="slack">Slack通知</option>
                        <option value="webhook">Webhook通知</option>
                      </select>
                    </div>

                    <div v-if="currentStep.config.notifyType === 'email'">
                      <label class="block text-sm font-medium text-gray-700 mb-1">收件人</label>
                      <input 
                        v-model="currentStep.config.recipients" 
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="user1@example.com,user2@example.com"
                      />
                    </div>

                    <div v-else-if="currentStep.config.notifyType === 'webhook'">
                      <label class="block text-sm font-medium text-gray-700 mb-1">Webhook URL</label>
                      <input 
                        v-model="currentStep.config.webhookUrl" 
                        type="url"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="https://hooks.example.com/webhook"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">通知条件</label>
                      <div class="space-y-2">
                        <label class="flex items-center">
                          <input type="checkbox" v-model="currentStep.config.notifyOnSuccess" class="rounded" />
                          <span class="ml-2">构建成功时通知</span>
                        </label>
                        <label class="flex items-center">
                          <input type="checkbox" v-model="currentStep.config.notifyOnFailure" class="rounded" />
                          <span class="ml-2">构建失败时通知</span>
                        </label>
                        <label class="flex items-center">
                          <input type="checkbox" v-model="currentStep.config.notifyOnStart" class="rounded" />
                          <span class="ml-2">构建开始时通知</span>
                        </label>
                      </div>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">通知消息模板</label>
                      <textarea 
                        v-model="currentStep.config.messageTemplate" 
                        rows="4"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        placeholder="构建 ${JOB_NAME} #${BUILD_NUMBER} ${BUILD_STATUS}

分支: ${GIT_BRANCH}
提交: ${GIT_COMMIT}
时间: ${BUILD_TIMESTAMP}

查看详情: ${BUILD_URL}"
                      />
                    </div>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      @click="closeEditor"
                    >
                      取消
                    </button>
                    <button
                      type="button"
                      class="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      @click="saveStep"
                    >
                      {{ isEditMode ? '更新步骤' : '添加步骤' }}
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
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  step: {
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
const showAdvancedOptions = ref(false)
const currentStep = ref({
  id: null,
  type: 'shell',
  title: '',
  config: {}
})

// Shell模板数据
const shellTemplates = ref([
  {
    id: 'nodejs',
    name: 'Node.js构建',
    icon: '📦',
    script: `#!/bin/bash
echo "开始Node.js项目构建..."

# 检查Node.js版本
node --version
npm --version

# 安装依赖
echo "安装依赖..."
npm ci

# 代码检查
echo "运行代码检查..."
npm run lint

# 运行测试
echo "运行测试..."
npm test

# 构建项目
echo "构建项目..."
npm run build

echo "构建完成！"`
  },
  {
    id: 'maven',
    name: 'Maven构建',
    icon: '☕',
    script: `#!/bin/bash
echo "开始Maven项目构建..."

# 检查Java版本
java -version
mvn -version

# 清理并编译
echo "清理并编译..."
mvn clean compile

# 运行测试
echo "运行测试..."
mvn test

# 打包
echo "打包..."
mvn package -DskipTests

echo "构建完成！"`
  },
  {
    id: 'python',
    name: 'Python构建',
    icon: '🐍',
    script: `#!/bin/bash
echo "开始Python项目构建..."

# 检查Python版本
python --version
pip --version

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 代码检查
echo "运行代码检查..."
flake8 .

# 运行测试
echo "运行测试..."
pytest

echo "构建完成！"`
  },
  {
    id: 'golang',
    name: 'Go构建',
    icon: '🔵',
    script: `#!/bin/bash
echo "开始Go项目构建..."

# 检查Go版本
go version

# 下载依赖
echo "下载依赖..."
go mod download

# 代码检查
echo "运行代码检查..."
go vet ./...

# 运行测试
echo "运行测试..."
go test ./...

# 构建
echo "构建..."
go build -o app .

echo "构建完成！"`
  }
])

// 凭据数据（模拟）
const dockerCredentials = ref([
  { id: 'dockerhub-creds', description: 'Docker Hub 凭据' },
  { id: 'aliyun-registry', description: '阿里云镜像仓库凭据' }
])

const sshCredentials = ref([
  { id: 'prod-server-key', description: '生产服务器SSH密钥' },
  { id: 'test-server-key', description: '测试服务器SSH密钥' }
])

const k8sConfigs = ref([
  { id: 'prod-k8s', name: '生产集群', cluster: 'prod-cluster' },
  { id: 'test-k8s', name: '测试集群', cluster: 'test-cluster' }
])

// 方法
const getStepTypeName = (type) => {
  const names = {
    shell: 'Shell脚本',
    docker: 'Docker操作',
    deploy: '部署操作',
    test: '测试操作',
    notify: '通知操作'
  }
  return names[type] || '未知步骤'
}

const getDefaultStepConfig = (type) => {
  const configs = {
    shell: {
      script: '',
      continueOnError: false,
      workingDir: '',
      envVars: []
    },
    docker: {
      operation: 'build',
      imageName: '',
      dockerfilePath: './Dockerfile',
      contextPath: '.',
      buildArgs: [],
      registryUrl: '',
      registryCredentials: '',
      containerName: '',
      portMapping: '',
      volumes: ''
    },
    deploy: {
      deployType: 'ssh',
      sshHost: '',
      sshCredentials: '',
      deployScript: '',
      k8sConfig: '',
      namespace: 'default',
      k8sMethod: 'kubectl',
      kubectlCommands: '',
      yamlPath: '',
      chartPath: '',
      releaseName: ''
    },
    test: {
      framework: 'junit',
      testPath: 'test/',
      testCommand: '',
      generateReports: false,
      reportPath: 'reports/'
    },
    notify: {
      notifyType: 'email',
      recipients: '',
      webhookUrl: '',
      notifyOnSuccess: true,
      notifyOnFailure: true,
      notifyOnStart: false,
      messageTemplate: ''
    }
  }
  return configs[type] || {}
}

const loadShellTemplate = (template) => {
  currentStep.value.config.script = template.script
  currentStep.value.title = template.name
}

const addEnvVar = () => {
  if (!currentStep.value.config.envVars) {
    currentStep.value.config.envVars = []
  }
  currentStep.value.config.envVars.push({ name: '', value: '' })
}

const removeEnvVar = (index) => {
  currentStep.value.config.envVars.splice(index, 1)
}

const addBuildArg = () => {
  if (!currentStep.value.config.buildArgs) {
    currentStep.value.config.buildArgs = []
  }
  currentStep.value.config.buildArgs.push({ key: '', value: '' })
}

const removeBuildArg = (index) => {
  currentStep.value.config.buildArgs.splice(index, 1)
}

const onDockerOperationChange = () => {
  // 根据操作类型调整默认配置
  if (currentStep.value.config.operation === 'build') {
    currentStep.value.title = 'Docker镜像构建'
  } else if (currentStep.value.config.operation === 'push') {
    currentStep.value.title = '推送Docker镜像'
  } else if (currentStep.value.config.operation === 'run') {
    currentStep.value.title = '运行Docker容器'
  }
}

const onDeployTypeChange = () => {
  // 根据部署类型调整默认配置
  if (currentStep.value.config.deployType === 'ssh') {
    currentStep.value.title = 'SSH远程部署'
  } else if (currentStep.value.config.deployType === 'k8s') {
    currentStep.value.title = 'Kubernetes部署'
  }
}

const closeEditor = () => {
  emit('close')
}

const saveStep = () => {
  // 验证步骤配置
  if (!currentStep.value.title.trim()) {
    currentStep.value.title = getStepTypeName(currentStep.value.type)
  }

  emit('save', { ...currentStep.value })
}

// 监听props变化
watch(() => props.step, (newStep) => {
  if (newStep && Object.keys(newStep).length > 0) {
    currentStep.value = {
      ...newStep,
      config: {
        ...getDefaultStepConfig(newStep.type),
        ...newStep.config
      }
    }
  } else {
    // 重置为默认状态
    currentStep.value = {
      id: Date.now(),
      type: 'shell',
      title: '',
      config: getDefaultStepConfig('shell')
    }
  }
}, { immediate: true, deep: true })

// 监听显示状态
watch(() => props.show, (show) => {
  if (show) {
    showAdvancedOptions.value = false
  }
})
</script>

<style scoped>
/* 代码编辑器样式 */
textarea[spellcheck="false"] {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.4;
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
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>