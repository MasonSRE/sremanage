<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">站点监控</h2>
      <div class="flex gap-2">
        <button 
          @click="loadSites" 
          class="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600"
          :disabled="loading"
        >
          {{ loading ? '加载中...' : '刷新' }}
        </button>
        <button 
          @click="batchTest" 
          class="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
          :disabled="loading || sites.length === 0"
        >
          批量拨测
        </button>
        <button 
          @click="showAddModal = true" 
          class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
        >
          添加监控
        </button>
      </div>
    </div>
    
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">站点名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">URL</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">响应时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后检查</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td colspan="6" class="px-6 py-4 text-center">
              <div class="flex justify-center items-center">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                <span class="ml-2">加载中...</span>
              </div>
            </td>
          </tr>
          <tr v-else-if="sites.length === 0">
            <td colspan="6" class="px-6 py-4 text-center text-gray-500">
              暂无监控站点，请点击"添加监控"按钮添加
            </td>
          </tr>
          <tr v-else v-for="site in sites" :key="site.id">
            <td class="px-6 py-4 whitespace-nowrap">{{ site.site_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <a :href="site.site_url" target="_blank" class="text-blue-600 hover:text-blue-900">
                {{ site.site_url }}
              </a>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusClass(site.status)">
                {{ getStatusText(site.status) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <span v-if="testingStates[site.id]" class="flex items-center">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
                  测试中...
                </span>
                <span v-else>
                  {{ site.last_response_time ? `${site.last_response_time}ms` : '-' }}
                </span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatTime(site.last_check_time) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button 
                @click="testSite(site.id)" 
                class="text-green-600 hover:text-green-900 mr-3"
                :disabled="testingStates[site.id]"
              >
                {{ testingStates[site.id] ? '拨测中...' : '单点拨测' }}
              </button>
              <button 
                @click="editSite(site)" 
                class="text-blue-600 hover:text-blue-900 mr-3"
              >
                编辑
              </button>
              <button 
                @click="deleteSite(site.id)" 
                class="text-red-600 hover:text-red-900"
                :disabled="loading"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加监控模态框 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">添加站点监控</h3>
          <form @submit.prevent="addSite">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">站点名称</label>
              <input 
                v-model="formData.site_name" 
                type="text" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="请输入站点名称"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">站点URL</label>
              <input 
                v-model="formData.site_url" 
                type="url" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">检查间隔（秒）</label>
              <input 
                v-model="formData.check_interval" 
                type="number" 
                min="60"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="300"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">超时时间（秒）</label>
              <input 
                v-model="formData.timeout" 
                type="number" 
                min="5"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="30"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">描述</label>
              <textarea 
                v-model="formData.description" 
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="请输入站点描述（可选）"
              ></textarea>
            </div>
            <div class="flex justify-end gap-2">
              <button 
                type="button" 
                @click="closeAddModal"
                class="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                取消
              </button>
              <button 
                type="submit"
                :disabled="loading"
                class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                {{ loading ? '添加中...' : '添加' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 编辑监控模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">编辑站点监控</h3>
          <form @submit.prevent="updateSite">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">站点名称</label>
              <input 
                v-model="editFormData.site_name" 
                type="text" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="请输入站点名称"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">站点URL</label>
              <input 
                v-model="editFormData.site_url" 
                type="url" 
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">检查间隔（秒）</label>
              <input 
                v-model="editFormData.check_interval" 
                type="number" 
                min="60"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="300"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">超时时间（秒）</label>
              <input 
                v-model="editFormData.timeout" 
                type="number" 
                min="5"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="30"
              >
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">启用状态</label>
              <select 
                v-model="editFormData.enabled" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option :value="true">启用</option>
                <option :value="false">禁用</option>
              </select>
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">描述</label>
              <textarea 
                v-model="editFormData.description" 
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="请输入站点描述（可选）"
              ></textarea>
            </div>
            <div class="flex justify-end gap-2">
              <button 
                type="button" 
                @click="closeEditModal"
                class="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                取消
              </button>
              <button 
                type="submit"
                :disabled="loading"
                class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                {{ loading ? '更新中...' : '更新' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api'

export default {
  name: 'Sites',
  data() {
    return {
      sites: [],
      loading: false,
      showAddModal: false,
      showEditModal: false,
      editingSiteId: null,
      testingStates: {}, // 跟踪每个站点的拨测状态 {siteId: boolean}
      formData: {
        site_name: '',
        site_url: '',
        check_interval: 300,
        timeout: 30,
        description: ''
      },
      editFormData: {
        site_name: '',
        site_url: '',
        check_interval: 300,
        timeout: 30,
        enabled: true,
        description: ''
      }
    }
  },
  mounted() {
    this.loadSites()
  },
  methods: {
    async loadSites() {
      this.loading = true
      try {
        const response = await api.get('/sites')
        if (response.data.success) {
          this.sites = response.data.data
        } else {
          this.showMessage(response.data.message || '获取站点列表失败', 'error')
        }
      } catch (error) {
        console.error('获取站点列表失败:', error)
        this.showMessage('获取站点列表失败', 'error')
      } finally {
        this.loading = false
      }
    },
    async addSite() {
      if (!this.formData.site_name || !this.formData.site_url) {
        this.showMessage('请填写站点名称和URL', 'error')
        return
      }
      
      this.loading = true
      try {
        const response = await api.post('/sites', this.formData)
        if (response.data.success) {
          this.showMessage('站点监控添加成功', 'success')
          this.closeAddModal()
          this.loadSites()
        } else {
          this.showMessage(response.data.message || '添加站点监控失败', 'error')
        }
      } catch (error) {
        console.error('添加站点监控失败:', error)
        this.showMessage('添加站点监控失败', 'error')
      } finally {
        this.loading = false
      }
    },
    async testSite(siteId) {
      // 设置该站点的拨测状态
      this.testingStates[siteId] = true
      
      try {
        const response = await api.post(`/sites/${siteId}/test`)
        if (response.data.success) {
          this.showMessage('拨测完成', 'success')
          
          // 只更新对应的站点数据，不刷新整个列表
          if (response.data.data && response.data.data.updated_site) {
            const updatedSite = response.data.data.updated_site
            const siteIndex = this.sites.findIndex(site => site.id === siteId)
            if (siteIndex !== -1) {
              // Vue 3 中直接赋值就是响应式的
              this.sites[siteIndex] = updatedSite
            }
          }
        } else {
          this.showMessage(response.data.message || '拨测失败', 'error')
        }
      } catch (error) {
        console.error('拨测失败:', error)
        this.showMessage('拨测失败', 'error')
      } finally {
        // 清除该站点的拨测状态
        this.testingStates[siteId] = false
      }
    },
    async batchTest() {
      this.loading = true
      try {
        const response = await api.post('/sites/batch-test')
        if (response.data.success) {
          this.showMessage(response.data.message || '批量拨测完成', 'success')
          this.loadSites() // 刷新列表显示最新状态
        } else {
          this.showMessage(response.data.message || '批量拨测失败', 'error')
        }
      } catch (error) {
        console.error('批量拨测失败:', error)
        this.showMessage('批量拨测失败', 'error')
      } finally {
        this.loading = false
      }
    },
    async deleteSite(siteId) {
      if (!confirm('确定要删除这个站点监控吗？')) {
        return
      }
      
      this.loading = true
      try {
        const response = await api.delete(`/sites/${siteId}`)
        if (response.data.success) {
          this.showMessage('站点监控删除成功', 'success')
          this.loadSites()
        } else {
          this.showMessage(response.data.message || '删除站点监控失败', 'error')
        }
      } catch (error) {
        console.error('删除站点监控失败:', error)
        this.showMessage('删除站点监控失败', 'error')
      } finally {
        this.loading = false
      }
    },
    editSite(site) {
      this.editingSiteId = site.id
      this.editFormData = {
        site_name: site.site_name,
        site_url: site.site_url,
        check_interval: site.check_interval,
        timeout: site.timeout,
        enabled: Boolean(site.enabled),
        description: site.description || ''
      }
      this.showEditModal = true
    },
    async updateSite() {
      if (!this.editFormData.site_name || !this.editFormData.site_url) {
        this.showMessage('请填写站点名称和URL', 'error')
        return
      }
      
      this.loading = true
      try {
        const response = await api.put(`/sites/${this.editingSiteId}`, this.editFormData)
        if (response.data.success) {
          this.showMessage('站点监控更新成功', 'success')
          this.closeEditModal()
          this.loadSites()
        } else {
          this.showMessage(response.data.message || '更新站点监控失败', 'error')
        }
      } catch (error) {
        console.error('更新站点监控失败:', error)
        this.showMessage('更新站点监控失败', 'error')
      } finally {
        this.loading = false
      }
    },
    closeAddModal() {
      this.showAddModal = false
      this.formData = {
        site_name: '',
        site_url: '',
        check_interval: 300,
        timeout: 30,
        description: ''
      }
    },
    closeEditModal() {
      this.showEditModal = false
      this.editingSiteId = null
      this.editFormData = {
        site_name: '',
        site_url: '',
        check_interval: 300,
        timeout: 30,
        enabled: true,
        description: ''
      }
    },
    getStatusClass(status) {
      const classes = {
        'online': 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800',
        'offline': 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800',
        'timeout': 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800',
        'error': 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800',
        'unknown': 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800'
      }
      return classes[status] || classes.unknown
    },
    getStatusText(status) {
      const texts = {
        'online': '正常',
        'offline': '离线',
        'timeout': '超时',
        'error': '错误',
        'unknown': '未知'
      }
      return texts[status] || '未知'
    },
    formatTime(timeString) {
      if (!timeString) return '-'
      try {
        // 后端返回的GMT时间实际上是本地时间（由于序列化问题）
        // 我们需要将其当作本地时间来解析，而不是GMT时间
        
        // 解析时间字符串，提取各个部分
        const match = timeString.match(/(\w+),\s+(\d+)\s+(\w+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+GMT/)
        if (!match) {
          // 如果不匹配GMT格式，尝试直接解析
          const date = new Date(timeString)
          if (isNaN(date.getTime())) return '-'
          return date.toLocaleString('zh-CN', { 
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
          })
        }
        
        const [, dayName, day, monthName, year, hour, minute, second] = match
        
        // 月份名称到数字的映射
        const months = {
          'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
          'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
        }
        
        // 创建本地时间（不进行时区转换）
        const localDate = new Date(
          parseInt(year),
          months[monthName],
          parseInt(day),
          parseInt(hour),
          parseInt(minute),
          parseInt(second)
        )
        
        return localDate.toLocaleString('zh-CN', { 
          year: 'numeric', 
          month: '2-digit', 
          day: '2-digit',
          hour: '2-digit', 
          minute: '2-digit',
          second: '2-digit'
        })
      } catch (error) {
        console.error('时间格式化错误:', error, timeString)
        return '-'
      }
    },
    showMessage(message, type = 'info') {
      // 简单的消息提示实现
      const colors = {
        success: '#10b981',
        error: '#ef4444', 
        info: '#3b82f6',
        warning: '#f59e0b'
      }
      
      // 创建消息元素
      const messageEl = document.createElement('div')
      messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: 14px;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
      `
      messageEl.textContent = message
      
      // 添加动画样式
      if (!document.getElementById('message-style')) {
        const style = document.createElement('style')
        style.id = 'message-style'
        style.textContent = `
          @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
          }
          @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
          }
        `
        document.head.appendChild(style)
      }
      
      document.body.appendChild(messageEl)
      
      // 3秒后自动消失
      setTimeout(() => {
        messageEl.style.animation = 'slideOut 0.3s ease-in'
        setTimeout(() => {
          if (messageEl.parentNode) {
            messageEl.parentNode.removeChild(messageEl)
          }
        }, 300)
      }, 3000)
      
      console.log(`[${type.toUpperCase()}] ${message}`)
    }
  }
}
</script> 