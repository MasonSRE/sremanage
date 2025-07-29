<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">Jenkins配置</h2>
      <button 
        @click="showAddDialog = true"
        class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      >
        添加Jenkins实例
      </button>
    </div>

    <!-- Jenkins实例列表 -->
    <div class="space-y-4">
      <div v-if="instances.length === 0" class="text-center py-8 text-gray-500">
        暂无Jenkins实例配置
      </div>
      
      <div v-for="instance in instances" :key="instance.id" 
           class="border rounded-lg p-4 hover:bg-gray-50">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <h3 class="text-lg font-medium">{{ instance.name }}</h3>
              <span :class="[
                'px-2 py-1 text-xs rounded-full',
                instance.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              ]">
                {{ instance.enabled ? '启用' : '禁用' }}
              </span>
            </div>
            <p class="text-gray-600 mt-1">{{ instance.url }}</p>
            <p class="text-sm text-gray-500 mt-1">用户名: {{ instance.username }}</p>
          </div>
          
          <div class="flex space-x-2">
            <button 
              @click="testConnection(instance)"
              class="text-blue-600 hover:text-blue-800 text-sm"
            >
              测试连接
            </button>
            <button 
              @click="editInstance(instance)"
              class="text-green-600 hover:text-green-800 text-sm"
            >
              编辑
            </button>
            <button 
              @click="deleteInstance(instance)"
              class="text-red-600 hover:text-red-800 text-sm"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑Jenkins实例对话框 -->
    <TransitionRoot appear :show="showAddDialog || showEditDialog" as="template">
      <Dialog as="div" @close="closeDialog" class="relative z-10">
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
                  {{ showEditDialog ? '编辑Jenkins实例' : '添加Jenkins实例' }}
                </DialogTitle>

                <form @submit.prevent="saveInstance" class="mt-4 space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">实例名称</label>
                    <input 
                      type="text"
                      v-model="formData.name"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="如: 生产环境Jenkins"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Jenkins URL</label>
                    <input 
                      type="url"
                      v-model="formData.url"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="https://jenkins.example.com"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">用户名</label>
                    <input 
                      type="text"
                      v-model="formData.username"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">API Token</label>
                    <input 
                      type="password"
                      v-model="formData.token"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="Jenkins API Token"
                    >
                    <p class="mt-1 text-xs text-gray-500">
                      在Jenkins中生成API Token: 用户设置 → API Token → 新增Token
                    </p>
                  </div>
                  
                  <div class="flex items-center">
                    <input 
                      type="checkbox"
                      v-model="formData.enabled"
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    >
                    <label class="ml-2 text-sm text-gray-900">启用此实例</label>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                      @click="closeDialog"
                    >
                      取消
                    </button>
                    <button
                      type="submit"
                      class="inline-flex justify-center rounded-md border border-transparent bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600"
                    >
                      {{ showEditDialog ? '更新' : '保存' }}
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { fetchApi } from '@/utils/api'

const instances = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingInstance = ref(null)

const formData = ref({
  name: '',
  url: '',
  username: '',
  token: '',
  enabled: true
})

const fetchInstances = async () => {
  try {
    const response = await fetchApi('/settings/jenkins', {
      method: 'GET'
    })
    if (response.success) {
      instances.value = response.data
    }
  } catch (error) {
    console.error('获取Jenkins实例失败:', error)
    alert('获取Jenkins实例失败')
  }
}

const saveInstance = async () => {
  try {
    const url = showEditDialog.value 
      ? `/settings/jenkins/${editingInstance.value.id}`
      : '/settings/jenkins'
    
    const method = showEditDialog.value ? 'PUT' : 'POST'
    
    const response = await fetchApi(url, {
      method,
      body: formData.value
    })
    
    if (response.success) {
      alert(response.message || '保存成功')
      closeDialog()
      await fetchInstances()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('保存Jenkins实例失败:', error)
    alert(error.message || '保存失败')
  }
}

const editInstance = (instance) => {
  editingInstance.value = instance
  formData.value = {
    name: instance.name,
    url: instance.url,
    username: instance.username,
    token: '', // 不显示原密码
    enabled: instance.enabled
  }
  showEditDialog.value = true
}

const deleteInstance = async (instance) => {
  if (!confirm(`确定要删除Jenkins实例 "${instance.name}" 吗？`)) {
    return
  }
  
  try {
    const response = await fetchApi(`/settings/jenkins/${instance.id}`, {
      method: 'DELETE'
    })
    
    if (response.success) {
      alert('删除成功')
      await fetchInstances()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('删除Jenkins实例失败:', error)
    alert(error.message || '删除失败')
  }
}

const testConnection = async (instance) => {
  try {
    const response = await fetchApi(`/ops/jenkins/test/${instance.id}`, {
      method: 'POST'
    })
    
    if (response.success) {
      alert(response.message)
    } else {
      alert(response.message || '连接测试失败')
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    alert('连接测试失败')
  }
}

const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  editingInstance.value = null
  formData.value = {
    name: '',
    url: '',
    username: '',
    token: '',
    enabled: true
  }
}

onMounted(fetchInstances)
</script>