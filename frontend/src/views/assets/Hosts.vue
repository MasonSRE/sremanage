<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">资产管理</h2>
      <button @click="showAddDialog = true" 
              class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
        添加主机
      </button>
    </div>
    
    <!-- 标签导航 -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'manual'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'manual'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          手动添加主机 ({{ manualHosts.length }})
        </button>
        
        <button
          @click="activeTab = 'aliyun'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'aliyun'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          <div class="flex items-center">
            <span class="w-4 h-4 mr-2 bg-orange-500 rounded text-white text-xs flex items-center justify-center font-bold">阿</span>
            阿里云 ECS ({{ aliyunInstances.length }})
          </div>
        </button>
        
        <button
          @click="activeTab = 'aws'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm opacity-50 cursor-not-allowed',
            activeTab === 'aws'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-400'
          ]"
          disabled
        >
          <div class="flex items-center">
            <span class="w-4 h-4 mr-2 bg-orange-500 rounded text-white text-xs flex items-center justify-center">A</span>
            AWS EC2 (敬请期待)
          </div>
        </button>
        
        <button
          @click="activeTab = 'tencent'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm opacity-50 cursor-not-allowed',
            activeTab === 'tencent'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-400'
          ]"
          disabled
        >
          <div class="flex items-center">
            <span class="w-4 h-4 mr-2 bg-blue-600 rounded text-white text-xs flex items-center justify-center">T</span>
            腾讯云 CVM (敬请期待)
          </div>
        </button>
      </nav>
    </div>

    <!-- 手动添加主机标签页 -->
    <div v-if="activeTab === 'manual'">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">主机名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP地址</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">系统类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">协议</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="host in manualHosts" :key="host.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ host.hostname }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ host.ip }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <component 
                    :is="host.system_type.toLowerCase() === 'linux' ? 'ServerIcon' : 'ComputerDesktopIcon'"
                    class="w-4 h-4 mr-2"
                  />
                  {{ host.system_type }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  host.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                ]">
                  {{ host.status === 'running' ? '运行中' : '维护中' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">{{ host.protocol }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-500">{{ host.created_at }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button @click="handleEdit(host)" class="text-blue-600 hover:text-blue-900 mr-2">编辑</button>
                <button @click="handleConnect(host)" class="text-green-600 hover:text-green-900 mr-2">连接</button>
                <button @click="handleDelete(host)" class="text-red-600 hover:text-red-900">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="manualHosts.length === 0" class="text-center py-12">
          <ServerIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">暂无手动添加的主机</h3>
          <p class="mt-1 text-sm text-gray-500">点击"添加主机"按钮添加您的第一台主机</p>
        </div>
      </div>
    </div>

    <!-- 阿里云ECS标签页 -->
    <div v-if="activeTab === 'aliyun'">
      <div class="mb-4 flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <button
            @click="fetchAliyunInstances(true)"
            :disabled="loadingAliyun"
            class="bg-orange-500 text-white px-4 py-2 rounded-md hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loadingAliyun">同步中...</span>
            <span v-else>{{ fromCache && aliyunInstances.length > 0 ? '强制刷新' : '同步ECS实例' }}</span>
          </button>
          
          <div v-if="lastSyncTime" class="flex items-center space-x-2 text-sm text-gray-500">
            <span>最后同步: {{ lastSyncTime }}</span>
            <span v-if="fromCache" class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
              缓存数据
            </span>
          </div>
          
          <div v-if="aliyunInstances.length > 0 && !loadingAliyun" class="text-sm text-green-600">
            ✓ 已缓存，下次访问无需等待
          </div>
        </div>
        
        <div v-if="!hasAliyunConfig" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-md">
          需要添加阿里云账号相关配置
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">实例名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">实例ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">公网IP</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">私网IP</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">实例类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">区域</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="instance in aliyunInstances" :key="instance.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="w-2 h-2 mr-2 bg-orange-500 rounded-full"></span>
                  {{ instance.name }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ instance.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ instance.public_ip || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ instance.private_ip || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  instance.status === 'Running' ? 'bg-green-100 text-green-800' : 
                  instance.status === 'Stopped' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                ]">
                  {{ getStatusText(instance.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ instance.instance_type }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ instance.region }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button 
                  @click="handleAliyunEdit(instance)"
                  class="text-blue-600 hover:text-blue-900 mr-2"
                >
                  编辑
                </button>
                <button 
                  v-if="instance.public_ip && instance.status === 'Running'"
                  @click="handleAliyunConnect(instance)" 
                  class="text-green-600 hover:text-green-900 mr-2"
                >
                  连接
                </button>
                <span v-if="!instance.public_ip || instance.status !== 'Running'" class="text-gray-400">-</span>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!loadingAliyun && aliyunInstances.length === 0" class="text-center py-12">
          <div v-if="hasAliyunConfig">
            <ServerIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">暂无ECS实例</h3>
            <p class="mt-1 text-sm text-gray-500">点击"同步ECS实例"按钮获取您的阿里云ECS实例列表</p>
          </div>
          <div v-else>
            <ExclamationTriangleIcon class="mx-auto h-12 w-12 text-orange-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">需要配置阿里云账号</h3>
            <p class="mt-1 text-sm text-gray-500">请先在系统设置中配置阿里云Access Key ID和Secret</p>
            <router-link 
              to="/settings/aliyun" 
              class="mt-3 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-orange-700 bg-orange-100 hover:bg-orange-200"
            >
              前往配置
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 手动添加主机的所有对话框保持不变 -->
    <!-- 添加主机对话框 -->
    <TransitionRoot appear :show="showAddDialog" as="template">
      <Dialog as="div" @close="showAddDialog = false" class="relative z-10">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as="template"
              enter="duration-300 ease-out"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="duration-200 ease-in"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  添加主机
                </DialogTitle>

                <form @submit.prevent="handleSubmit" class="mt-4">
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">主机名</label>
                      <input v-model="form.hostname" type="text" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700">IP地址</label>
                      <input v-model="form.ip" type="text" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">系统类型</label>
                      <select v-model="form.system_type" required
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                        <option value="Linux">Linux</option>
                        <option value="Windows">Windows</option>
                      </select>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">协议</label>
                      <select v-model="form.protocol" required
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                        <option value="SSH">SSH</option>
                        <option value="RDP">RDP</option>
                      </select>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">端口</label>
                      <input v-model.number="form.port" type="number" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">用户名</label>
                      <input v-model="form.username" type="text" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">密码</label>
                      <input v-model="form.password" type="password"
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">描述</label>
                      <textarea v-model="form.description"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2"></textarea>
                    </div>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button type="button"
                            @click="showAddDialog = false"
                            class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                      取消
                    </button>
                    <button type="submit"
                            class="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                      添加
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- 编辑主机对话框 -->
    <TransitionRoot appear :show="showEditDialog" as="template">
      <Dialog as="div" @close="showEditDialog = false" class="relative z-10">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as="template"
              enter="duration-300 ease-out"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="duration-200 ease-in"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                  编辑主机
                </DialogTitle>

                <form @submit.prevent="handleEditSubmit" class="mt-4">
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">主机名</label>
                      <input v-model="form.hostname" type="text" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700">IP地址</label>
                      <input v-model="form.ip" type="text" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">系统类型</label>
                      <select v-model="form.system_type" required
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                        <option value="Linux">Linux</option>
                        <option value="Windows">Windows</option>
                      </select>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">协议</label>
                      <select v-model="form.protocol" required
                              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                        <option value="SSH">SSH</option>
                        <option value="RDP">RDP</option>
                      </select>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">端口</label>
                      <input v-model.number="form.port" type="number" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">用户名</label>
                      <input v-model="form.username" type="text" required
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">密码</label>
                      <input v-model="form.password" type="password"
                             class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700">描述</label>
                      <textarea v-model="form.description"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2"></textarea>
                    </div>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button type="button"
                            @click="showEditDialog = false"
                            class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                      取消
                    </button>
                    <button type="submit"
                            class="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                      更新
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- 阿里云实例编辑对话框 -->
    <TransitionRoot appear :show="showAliyunEditDialog" as="template">
      <Dialog as="div" @close="showAliyunEditDialog = false" class="relative z-10">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as="template"
              enter="duration-300 ease-out"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="duration-200 ease-in"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                  编辑阿里云实例连接配置
                </DialogTitle>

                <div v-if="currentAliyunInstance" class="mb-4 p-3 bg-gray-50 rounded-md">
                  <p class="text-sm text-gray-600">实例信息</p>
                  <p class="font-medium">{{ currentAliyunInstance.name }}</p>
                  <p class="text-sm text-gray-500">{{ currentAliyunInstance.id }}</p>
                  <p class="text-sm text-gray-500">{{ currentAliyunInstance.public_ip }}</p>
                </div>

                <form @submit.prevent="handleAliyunEditSubmit" class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">SSH端口</label>
                    <input 
                      v-model.number="aliyunForm.ssh_port" 
                      type="number" 
                      required 
                      min="1" 
                      max="65535"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" 
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">用户名</label>
                    <input 
                      v-model="aliyunForm.username" 
                      type="text" 
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" 
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">密码</label>
                    <input 
                      v-model="aliyunForm.password" 
                      type="password"
                      placeholder="留空则不更改密码"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2" 
                    />
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button 
                      type="button"
                      @click="showAliyunEditDialog = false"
                      class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      取消
                    </button>
                    <button 
                      type="submit"
                      class="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      保存
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- 删除确认对话框 -->
    <TransitionRoot appear :show="showDeleteDialog" as="template">
      <Dialog as="div" @close="showDeleteDialog = false" class="relative z-10">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                删除主机确认
              </DialogTitle>

              <div class="mt-4">
                <p class="text-sm text-gray-500 mb-4">
                  您确定要删除以下主机吗？此操作不可恢复。
                </p>
                <div class="bg-gray-50 p-4 rounded-md">
                  <p class="text-sm"><span class="font-medium">主机名：</span>{{ currentHost?.hostname }}</p>
                  <p class="text-sm mt-1"><span class="font-medium">IP地址：</span>{{ currentHost?.ip }}</p>
                </div>
                <div class="mt-4">
                  <label class="block text-sm font-medium text-gray-700">
                    <span class="text-blue-600">请输入IP地址以确认删除</span>
                  </label>
                  <input 
                    v-model="deleteConfirmIP"
                    type="text"
                    class="mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2"
                    placeholder="请输入IP地址"
                    autofocus
                  />
                </div>
              </div>

              <div class="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  @click="showDeleteDialog = false"
                  class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  取消
                </button>
                <button
                  type="button"
                  @click="confirmDelete"
                  :disabled="!isDeleteConfirmValid"
                  :class="[
                    'inline-flex justify-center rounded-md border border-transparent px-4 py-2 text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2',
                    isDeleteConfirmValid 
                      ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                      : 'bg-gray-300 cursor-not-allowed'
                  ]"
                >
                  删除
                </button>
              </div>
            </DialogPanel>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ServerIcon, ComputerDesktopIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import { fetchApi } from '../../utils/api'

const activeTab = ref('manual')
const manualHosts = ref([])
const aliyunInstances = ref([])
const loadingAliyun = ref(false)
const hasAliyunConfig = ref(false)
const lastSyncTime = ref('')
const fromCache = ref(false)
const syncStatus = ref('completed')

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const showAliyunEditDialog = ref(false)
const currentHost = ref(null)
const currentAliyunInstance = ref(null)
const deleteConfirmIP = ref('')
const form = ref({
  hostname: '',
  ip: '',
  system_type: 'Linux',
  protocol: 'SSH',
  port: 22,
  username: '',
  password: '',
  description: ''
})
const aliyunForm = ref({
  ssh_port: 22,
  username: 'root',
  password: ''
})
const aliyunConfigs = ref({})
const router = useRouter()

// 获取手动添加的主机列表
const fetchManualHosts = async () => {
  try {
    console.log('开始获取手动主机列表')
    
    const token = localStorage.getItem('token')
    console.log('当前使用的Token:', token ? token.substring(0, 20) + '...' : 'No token')
    
    const data = await fetchApi('/hosts');
    
    console.log('获取到的数据:', data)

    if (data.success) {
      manualHosts.value = data.data;
      console.log('成功获取到手动主机列表，数量:', data.data.length)
    } else {
      throw new Error(data.message || '获取主机列表失败');
    }
  } catch (error) {
    console.error('获取手动主机列表失败:', error);
    throw error;
  }
}

// 检查阿里云配置
const checkAliyunConfig = async () => {
  try {
    const response = await fetchApi('/settings/aliyun')
    if (response.success && response.data.accessKeyId && response.data.accessKeyId.trim() !== '') {
      hasAliyunConfig.value = true
      return true
    }
    hasAliyunConfig.value = false
    return false
  } catch (error) {
    console.error('检查阿里云配置失败:', error)
    hasAliyunConfig.value = false
    return false
  }
}

// 获取阿里云ECS实例（支持缓存）
const fetchAliyunInstances = async (forceRefresh = false) => {
  // 如果强制刷新，需要检查配置
  if (forceRefresh && !await checkAliyunConfig()) {
    alert('请先配置阿里云账号信息')
    return
  }

  loadingAliyun.value = true
  try {
    const url = forceRefresh ? '/aliyun/ecs/instances?force_refresh=true' : '/aliyun/ecs/instances'
    const response = await fetchApi(url)
    
    if (response.success) {
      aliyunInstances.value = response.data || []
      fromCache.value = response.from_cache || false
      
      // 更新同步时间
      if (response.synced_at) {
        lastSyncTime.value = response.synced_at
      } else if (response.last_sync_time) {
        lastSyncTime.value = response.last_sync_time
      } else if (!fromCache.value) {
        lastSyncTime.value = new Date().toLocaleString()
      }
      
      console.log(`获取到阿里云ECS实例: ${response.data.length} 个，来源: ${fromCache.value ? '缓存' : '实时同步'}`)
      
      // 如果有警告信息，显示给用户
      if (response.warning) {
        console.warn(response.warning)
      }
    } else {
      throw new Error(response.message || '获取阿里云ECS实例失败')
    }
  } catch (error) {
    console.error('获取阿里云ECS实例失败:', error)
    alert('获取阿里云ECS实例失败: ' + error.message)
  } finally {
    loadingAliyun.value = false
  }
}

// 状态文本转换
const getStatusText = (status) => {
  const statusMap = {
    'Running': '运行中',
    'Stopped': '已停止',
    'Starting': '启动中',
    'Stopping': '停止中'
  }
  return statusMap[status] || status
}

// 获取阿里云实例连接配置
const fetchAliyunConfigs = async () => {
  try {
    const response = await fetchApi('/aliyun/instance/config')
    if (response.success) {
      aliyunConfigs.value = response.data || {}
    }
  } catch (error) {
    console.error('获取阿里云实例配置失败:', error)
  }
}

// 编辑阿里云实例
const handleAliyunEdit = async (instance) => {
  currentAliyunInstance.value = instance
  
  try {
    // 获取当前实例的配置
    const response = await fetchApi(`/aliyun/instance/config/${instance.id}`)
    if (response.success) {
      aliyunForm.value = {
        ssh_port: response.data.ssh_port || 22,
        username: response.data.username || 'root',
        password: ''  // 不显示已保存的密码
      }
    } else {
      // 使用默认配置
      aliyunForm.value = {
        ssh_port: 22,
        username: 'root',
        password: ''
      }
    }
    
    showAliyunEditDialog.value = true
  } catch (error) {
    console.error('获取实例配置失败:', error)
    alert('获取实例配置失败: ' + error.message)
  }
}

// 保存阿里云实例配置
const handleAliyunEditSubmit = async () => {
  try {
    const response = await fetchApi(`/aliyun/instance/config/${currentAliyunInstance.value.id}`, {
      method: 'PUT',
      body: aliyunForm.value
    })
    
    if (response.success) {
      alert('配置保存成功')
      showAliyunEditDialog.value = false
      // 刷新配置
      await fetchAliyunConfigs()
    } else {
      alert(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    alert('保存配置失败: ' + error.message)
  }
}

// 连接阿里云实例（使用配置的端口和用户名）
const handleAliyunConnect = (instance) => {
  const ip = instance.public_ip
  const config = aliyunConfigs.value[instance.id] || { ssh_port: 22, username: 'root' }
  
  const currentOrigin = window.location.origin
  const terminalUrl = `${currentOrigin}/terminal?hostname=${encodeURIComponent(instance.name)}&ip=${encodeURIComponent(ip)}&port=${config.ssh_port}&username=${encodeURIComponent(config.username)}&instance_id=${encodeURIComponent(instance.id)}&provider=aliyun`
  window.open(terminalUrl, '_blank')
}

// 原有的手动主机相关函数保持不变
const handleSubmit = async () => {
  try {
    console.log('发送的表单数据:', form.value)

    const response = await fetchApi('/hosts', {
      method: 'POST',
      body: form.value
    });
    
    console.log('添加主机响应数据:', response)
    
    if (response.success) {
      alert('添加成功')
      showAddDialog.value = false
      fetchManualHosts()
      // 重置表单
      form.value = {
        hostname: '',
        ip: '',
        system_type: 'Linux',
        protocol: 'SSH',
        port: 22,
        username: '',
        password: '',
        description: ''
      }
    } else {
      alert(response.message)
    }
  } catch (error) {
    console.error('添加主机失败:', error)
    alert('添加主机失败: ' + error.message)
  }
}

// 编辑相关
const handleEdit = (host) => {
  currentHost.value = host
  form.value = {
    hostname: host.hostname,
    ip: host.ip,
    system_type: host.system_type,
    protocol: host.protocol,
    port: host.port,
    username: host.username,
    password: host.password || '',
    description: host.description || ''
  }
  showEditDialog.value = true
}

const handleEditSubmit = async () => {
  try {
    console.log('发送编辑请求:', form.value)

    const response = await fetchApi(`/hosts/${currentHost.value.id}`, {
      method: 'PUT',
      body: form.value
    });

    console.log('编辑响应:', response)
    
    if (response.success) {
      alert('更新成功')
      showEditDialog.value = false
      fetchManualHosts()
    } else {
      alert(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新主机失败:', error)
    alert('更新主机失败: ' + error.message)
  }
}

// 删除相关
const handleDelete = (host) => {
  currentHost.value = host
  deleteConfirmIP.value = ''
  showDeleteDialog.value = true
}

const isDeleteConfirmValid = computed(() => {
  return deleteConfirmIP.value === currentHost.value?.ip
})

const confirmDelete = async () => {
  if (!isDeleteConfirmValid.value) return

  try {
    console.log('发送删除请求:', currentHost.value.id)
    
    const response = await fetchApi(`/hosts/${currentHost.value.id}`, {
      method: 'DELETE'
    });
    
    console.log('删除响应:', response)
    
    if (response.success) {
      alert('删除成功')
      showDeleteDialog.value = false
      fetchManualHosts()
    } else {
      alert(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除主机失败:', error)
    alert('删除主机失败: ' + error.message)
  }
}

// 连接相关
const handleConnect = (host) => {
  const currentOrigin = window.location.origin
  const terminalUrl = `${currentOrigin}/terminal?hostname=${encodeURIComponent(host.hostname)}&ip=${encodeURIComponent(host.ip)}&port=${host.port}&username=${encodeURIComponent(host.username)}`
  window.open(terminalUrl, '_blank')
}

onMounted(async () => {
  await fetchManualHosts()
  await checkAliyunConfig()
  // 如果有阿里云配置，自动同步一次ECS实例和获取配置
  if (hasAliyunConfig.value) {
    await Promise.all([
      fetchAliyunInstances(),
      fetchAliyunConfigs()
    ])
  }
})
</script>