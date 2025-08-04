<template>
  <div class="encryption-manager">
    <!-- 数据加密强化管理面板 -->
    <div class="bg-white shadow rounded-lg">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8 px-6" aria-label="Tabs">
          <button
            @click="activeTab = 'encrypt'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'encrypt'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🔐 数据加密
          </button>
          <button
            @click="activeTab = 'token'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'token'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🎫 安全令牌
          </button>
          <button
            @click="activeTab = 'masking'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'masking'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🎭 数据脱敏
          </button>
          <button
            @click="activeTab = 'ssl'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'ssl'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🔑 SSL密钥
          </button>
          <button
            @click="activeTab = 'status'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'status'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            📊 系统状态
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- 数据加密面板 -->
        <div v-show="activeTab === 'encrypt'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">🔐 敏感数据加密</h4>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- 加密操作 -->
            <div class="border rounded-lg p-4">
              <h5 class="text-md font-medium text-gray-800 mb-3">数据加密</h5>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">密钥ID</label>
                  <input
                    v-model="encryptForm.keyId"
                    type="text"
                    class="w-full border rounded-md px-3 py-2 text-sm"
                    placeholder="default"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">要加密的数据</label>
                  <textarea
                    v-model="encryptForm.data"
                    rows="4"
                    class="w-full border rounded-md px-3 py-2 text-sm"
                    placeholder="输入要加密的敏感数据..."
                  ></textarea>
                </div>
                <button
                  @click="encryptData"
                  :disabled="!encryptForm.data || encryptLoading"
                  class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {{ encryptLoading ? '加密中...' : '🔐 加密数据' }}
                </button>
              </div>
              
              <div v-if="encryptResult" class="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <p class="text-sm font-medium text-green-800 mb-2">加密成功！</p>
                <textarea
                  :value="JSON.stringify(encryptResult, null, 2)"
                  rows="6"
                  class="w-full border rounded-md px-3 py-2 text-xs bg-gray-50"
                  readonly
                ></textarea>
              </div>
            </div>
            
            <!-- 解密操作 -->
            <div class="border rounded-lg p-4">
              <h5 class="text-md font-medium text-gray-800 mb-3">数据解密</h5>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">加密信息 (JSON)</label>
                  <textarea
                    v-model="decryptForm.encryptionInfo"
                    rows="4"
                    class="w-full border rounded-md px-3 py-2 text-sm"
                    placeholder="粘贴加密信息JSON..."
                  ></textarea>
                </div>
                <button
                  @click="decryptData"
                  :disabled="!decryptForm.encryptionInfo || decryptLoading"
                  class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {{ decryptLoading ? '解密中...' : '🔓 解密数据' }}
                </button>
              </div>
              
              <div v-if="decryptResult" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p class="text-sm font-medium text-blue-800 mb-2">解密结果：</p>
                <div class="text-sm bg-white border rounded-md p-2">
                  {{ typeof decryptResult === 'object' ? JSON.stringify(decryptResult, null, 2) : decryptResult }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 安全令牌面板 -->
        <div v-show="activeTab === 'token'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">🎫 安全令牌管理</h4>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- 生成令牌 -->
            <div class="border rounded-lg p-4">
              <h5 class="text-md font-medium text-gray-800 mb-3">生成安全令牌</h5>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">过期时间 (秒)</label>
                  <input
                    v-model.number="tokenForm.expiresIn"
                    type="number"
                    class="w-full border rounded-md px-3 py-2 text-sm"
                    placeholder="3600"
                    min="60"
                    max="86400"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">权限列表 (一行一个)</label>
                  <textarea
                    v-model="tokenForm.permissionsText"
                    rows="3"
                    class="w-full border rounded-md px-3 py-2 text-sm"
                    placeholder="read_data&#10;write_data&#10;admin_access"
                  ></textarea>
                </div>
                <button
                  @click="generateToken"
                  :disabled="tokenLoading"
                  class="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                  {{ tokenLoading ? '生成中...' : '🎫 生成令牌' }}
                </button>
              </div>
              
              <div v-if="tokenResult" class="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-md">
                <p class="text-sm font-medium text-purple-800 mb-2">令牌生成成功！</p>
                <div class="space-y-2">
                  <div>
                    <span class="text-xs font-medium text-gray-600">令牌ID:</span>
                    <div class="text-xs bg-white border rounded p-1 font-mono">{{ tokenResult.token_id }}</div>
                  </div>
                  <div>
                    <span class="text-xs font-medium text-gray-600">过期时间:</span>
                    <div class="text-xs bg-white border rounded p-1">{{ tokenResult.expires_at }}</div>
                  </div>
                  <div>
                    <span class="text-xs font-medium text-gray-600">令牌:</span>
                    <div class="text-xs bg-white border rounded p-1 font-mono break-all">{{ tokenResult.token }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 验证令牌 -->
            <div class="border rounded-lg p-4">
              <h5 class="text-md font-medium text-gray-800 mb-3">验证/撤销令牌</h5>
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">令牌</label>
                  <textarea
                    v-model="validateForm.token"
                    rows="3"
                    class="w-full border rounded-md px-3 py-2 text-sm"
                    placeholder="粘贴令牌..."
                  ></textarea>
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="validateToken"
                    :disabled="!validateForm.token || validateLoading"
                    class="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
                  >
                    {{ validateLoading ? '验证中...' : '✅ 验证令牌' }}
                  </button>
                  <button
                    @click="revokeToken"
                    :disabled="!validateForm.token || revokeLoading"
                    class="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 disabled:opacity-50"
                  >
                    {{ revokeLoading ? '撤销中...' : '❌ 撤销令牌' }}
                  </button>
                </div>
              </div>
              
              <div v-if="validateResult" class="mt-4 p-3 border rounded-md" :class="{
                'bg-green-50 border-green-200': validateResult.valid,
                'bg-red-50 border-red-200': !validateResult.valid
              }">
                <p class="text-sm font-medium mb-2" :class="{
                  'text-green-800': validateResult.valid,
                  'text-red-800': !validateResult.valid
                }">
                  {{ validateResult.valid ? '令牌有效' : '令牌无效' }}
                </p>
                <div v-if="validateResult.valid && validateResult.data" class="text-xs space-y-1">
                  <p><strong>用户ID:</strong> {{ validateResult.data.user_id }}</p>
                  <p><strong>过期时间:</strong> {{ validateResult.data.expires_at }}</p>
                  <p><strong>权限:</strong> {{ validateResult.data.permissions.join(', ') || '无特殊权限' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据脱敏面板 -->
        <div v-show="activeTab === 'masking'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">🎭 数据脱敏处理</h4>
          
          <div class="border rounded-lg p-4">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">敏感数据 (JSON格式)</label>
                <textarea
                  v-model="maskingForm.data"
                  rows="6"
                  class="w-full border rounded-md px-3 py-2 text-sm"
                  placeholder='{"email": "user@example.com", "phone": "13812345678", "password": "secret123"}'
                ></textarea>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">敏感字段 (可选，一行一个)</label>
                <textarea
                  v-model="maskingForm.sensitiveFields"
                  rows="3"
                  class="w-full border rounded-md px-3 py-2 text-sm"
                  placeholder="email&#10;phone&#10;password"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">
                  留空则自动检测常见敏感字段
                </p>
              </div>
              <button
                @click="maskData"
                :disabled="!maskingForm.data || maskingLoading"
                class="w-full bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 disabled:opacity-50"
              >
                {{ maskingLoading ? '处理中...' : '🎭 执行脱敏' }}
              </button>
            </div>
            
            <div v-if="maskingResult" class="mt-6">
              <h6 class="text-sm font-medium text-gray-800 mb-2">脱敏结果对比：</h6>
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div>
                  <p class="text-xs font-medium text-gray-600 mb-1">原始数据:</p>
                  <pre class="text-xs bg-red-50 border border-red-200 rounded p-2 overflow-auto">{{ maskingOriginal }}</pre>
                </div>
                <div>
                  <p class="text-xs font-medium text-gray-600 mb-1">脱敏数据:</p>
                  <pre class="text-xs bg-green-50 border border-green-200 rounded p-2 overflow-auto">{{ JSON.stringify(maskingResult, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- SSL密钥面板 -->
        <div v-show="activeTab === 'ssl'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">🔑 SSL密钥对生成</h4>
          
          <div class="border rounded-lg p-4">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">密钥长度</label>
                <select
                  v-model.number="sslForm.keySize"
                  class="w-full border rounded-md px-3 py-2 text-sm"
                >
                  <option :value="1024">1024 位 (不推荐)</option>
                  <option :value="2048">2048 位 (推荐)</option>
                  <option :value="4096">4096 位 (高安全)</option>
                </select>
              </div>
              <button
                @click="generateSSLKeypair"
                :disabled="sslLoading"
                class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {{ sslLoading ? '生成中...' : '🔑 生成SSL密钥对' }}
              </button>
            </div>
            
            <div v-if="sslResult" class="mt-6 space-y-4">
              <div>
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-gray-700">私钥 (请安全保存):</span>
                  <button @click="copyToClipboard(sslResult.private_key)" class="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded">
                    复制
                  </button>
                </div>
                <textarea
                  :value="sslResult.private_key"
                  rows="8"
                  class="w-full border rounded-md px-3 py-2 text-xs bg-gray-50 font-mono"
                  readonly
                ></textarea>
              </div>
              <div>
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-gray-700">公钥:</span>
                  <button @click="copyToClipboard(sslResult.public_key)" class="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded">
                    复制
                  </button>
                </div>
                <textarea
                  :value="sslResult.public_key"
                  rows="6"
                  class="w-full border rounded-md px-3 py-2 text-xs bg-gray-50 font-mono"
                  readonly
                ></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统状态面板 -->
        <div v-show="activeTab === 'status'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">📊 加密系统状态</h4>
          
          <div v-if="systemStatus" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- 加密管理器 -->
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h6 class="text-sm font-medium text-blue-800 mb-2">🔐 加密管理器</h6>
                <div class="text-xs space-y-1 text-blue-700">
                  <p>状态: {{ systemStatus.encryption_manager.status }}</p>
                  <p>算法: {{ systemStatus.encryption_manager.algorithm }}</p>
                  <p>缓存大小: {{ systemStatus.encryption_manager.key_cache_size }}</p>
                </div>
              </div>
              
              <!-- 令牌管理器 -->
              <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h6 class="text-sm font-medium text-purple-800 mb-2">🎫 令牌管理器</h6>
                <div class="text-xs space-y-1 text-purple-700">
                  <p>状态: {{ systemStatus.token_manager.status }}</p>
                  <p>活跃令牌: {{ systemStatus.token_manager.active_tokens }}</p>
                  <p>已撤销: {{ systemStatus.token_manager.revoked_tokens }}</p>
                </div>
              </div>
              
              <!-- 数据脱敏 -->
              <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h6 class="text-sm font-medium text-yellow-800 mb-2">🎭 数据脱敏</h6>
                <div class="text-xs space-y-1 text-yellow-700">
                  <p>状态: {{ systemStatus.data_masking.status }}</p>
                  <p>支持字段: {{ systemStatus.data_masking.supported_fields.length }}种</p>
                </div>
              </div>
              
              <!-- SSL管理器 -->
              <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                <h6 class="text-sm font-medium text-green-800 mb-2">🔑 SSL管理器</h6>
                <div class="text-xs space-y-1 text-green-700">
                  <p>状态: {{ systemStatus.ssl_manager.status }}</p>
                  <p>支持长度: {{ systemStatus.ssl_manager.supported_key_sizes.join(', ') }}</p>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 border rounded-lg p-4">
              <h6 class="text-sm font-medium text-gray-800 mb-3">系统信息</h6>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <span class="font-medium">加密启用:</span> 
                  <span :class="systemStatus.system_info.encryption_enabled ? 'text-green-600' : 'text-red-600'">
                    {{ systemStatus.system_info.encryption_enabled ? '是' : '否' }}
                  </span>
                </div>
                <div>
                  <span class="font-medium">最后更新:</span> 
                  <span class="text-gray-600">{{ formatDateTime(systemStatus.system_info.last_updated) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="mt-4">
            <button
              @click="refreshSystemStatus"
              :disabled="statusLoading"
              class="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 disabled:opacity-50"
            >
              {{ statusLoading ? '刷新中...' : '🔄 刷新状态' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { notification } from '@/utils/notification'

// 响应式数据
const activeTab = ref('encrypt')

// 加密相关
const encryptForm = ref({
  keyId: 'default',
  data: ''
})
const encryptResult = ref(null)
const encryptLoading = ref(false)

const decryptForm = ref({
  encryptionInfo: ''
})
const decryptResult = ref(null)
const decryptLoading = ref(false)

// 令牌相关
const tokenForm = ref({
  expiresIn: 3600,
  permissionsText: ''
})
const tokenResult = ref(null)
const tokenLoading = ref(false)

const validateForm = ref({
  token: ''
})
const validateResult = ref(null)
const validateLoading = ref(false)
const revokeLoading = ref(false)

// 数据脱敏相关
const maskingForm = ref({
  data: '',
  sensitiveFields: ''
})
const maskingResult = ref(null)
const maskingOriginal = ref('')
const maskingLoading = ref(false)

// SSL密钥相关
const sslForm = ref({
  keySize: 2048
})
const sslResult = ref(null)
const sslLoading = ref(false)

// 系统状态相关
const systemStatus = ref(null)
const statusLoading = ref(false)

// 方法
const encryptData = async () => {
  if (!encryptForm.value.data.trim()) {
    notification.error('请输入要加密的数据')
    return
  }
  
  encryptLoading.value = true
  try {
    let dataToEncrypt = encryptForm.value.data.trim()
    
    // 尝试解析JSON
    try {
      dataToEncrypt = JSON.parse(dataToEncrypt)
    } catch {
      // 保持字符串格式
    }
    
    const response = await fetch('/api/ops/encryption/encrypt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        data: dataToEncrypt,
        key_id: encryptForm.value.keyId || 'default'
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      encryptResult.value = result.data
      notification.success('数据加密成功')
    } else {
      notification.error(result.message || '加密失败')
    }
  } catch (error) {
    notification.error('加密请求失败')
    console.error('加密错误:', error)
  } finally {
    encryptLoading.value = false
  }
}

const decryptData = async () => {
  if (!decryptForm.value.encryptionInfo.trim()) {
    notification.error('请输入加密信息')
    return
  }
  
  decryptLoading.value = true
  try {
    const encryptionInfo = JSON.parse(decryptForm.value.encryptionInfo.trim())
    
    const response = await fetch('/api/ops/encryption/decrypt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        encryption_info: encryptionInfo
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      decryptResult.value = result.data
      notification.success('数据解密成功')
    } else {
      notification.error(result.message || '解密失败')
    }
  } catch (error) {
    notification.error('解密请求失败或JSON格式错误')
    console.error('解密错误:', error)
  } finally {
    decryptLoading.value = false
  }
}

const generateToken = async () => {
  tokenLoading.value = true
  try {
    const permissions = tokenForm.value.permissionsText
      .split('\n')
      .map(p => p.trim())
      .filter(p => p)
    
    const response = await fetch('/api/ops/encryption/token/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        expires_in: tokenForm.value.expiresIn,
        permissions
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      tokenResult.value = result.data
      notification.success('安全令牌生成成功')
    } else {
      notification.error(result.message || '令牌生成失败')
    }
  } catch (error) {
    notification.error('令牌生成请求失败')
    console.error('令牌生成错误:', error)
  } finally {
    tokenLoading.value = false
  }
}

const validateToken = async () => {
  if (!validateForm.value.token.trim()) {
    notification.error('请输入令牌')
    return
  }
  
  validateLoading.value = true
  try {
    const response = await fetch('/api/ops/encryption/token/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        token: validateForm.value.token.trim()
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      validateResult.value = result
      notification.success('令牌验证完成')
    } else {
      notification.error(result.message || '令牌验证失败')
    }
  } catch (error) {
    notification.error('令牌验证请求失败')
    console.error('令牌验证错误:', error)
  } finally {
    validateLoading.value = false
  }
}

const revokeToken = async () => {
  if (!validateForm.value.token.trim()) {
    notification.error('请输入要撤销的令牌')
    return
  }
  
  // 首先验证令牌获取token_id
  try {
    const validateResponse = await fetch('/api/ops/encryption/token/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        token: validateForm.value.token.trim()
      })
    })
    
    const validateResult = await validateResponse.json()
    
    if (!validateResult.success || !validateResult.valid) {
      notification.error('无法撤销：令牌无效')
      return
    }
    
    // 从令牌中提取token_id (这里需要解析令牌)
    // 简化处理，假设可以从验证结果获取token_id
    const tokenData = JSON.parse(atob(validateForm.value.token.trim()))
    const payload = JSON.parse(atob(tokenData.payload))
    const tokenId = payload.token_id
    
    revokeLoading.value = true
    
    const response = await fetch('/api/ops/encryption/token/revoke', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        token_id: tokenId,
        reason: 'manual_revocation'
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      notification.success('令牌已撤销')
      validateResult.value = null
    } else {
      notification.error(result.message || '令牌撤销失败')
    }
  } catch (error) {
    notification.error('令牌撤销失败')
    console.error('令牌撤销错误:', error)
  } finally {
    revokeLoading.value = false
  }
}

const maskData = async () => {
  if (!maskingForm.value.data.trim()) {
    notification.error('请输入要脱敏的数据')
    return
  }
  
  maskingLoading.value = true
  try {
    const data = JSON.parse(maskingForm.value.data.trim())
    const sensitiveFields = maskingForm.value.sensitiveFields
      .split('\n')
      .map(f => f.trim())
      .filter(f => f)
    
    maskingOriginal.value = JSON.stringify(data, null, 2)
    
    const response = await fetch('/api/ops/encryption/mask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        data,
        sensitive_fields: sensitiveFields.length > 0 ? sensitiveFields : null
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      maskingResult.value = result.data
      notification.success('数据脱敏成功')
    } else {
      notification.error(result.message || '数据脱敏失败')
    }
  } catch (error) {
    notification.error('数据脱敏失败或JSON格式错误')
    console.error('数据脱敏错误:', error)
  } finally {
    maskingLoading.value = false
  }
}

const generateSSLKeypair = async () => {
  sslLoading.value = true
  try {
    const response = await fetch('/api/ops/encryption/ssl/keypair', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        key_size: sslForm.value.keySize
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      sslResult.value = result.data
      notification.success('SSL密钥对生成成功')
    } else {
      notification.error(result.message || 'SSL密钥对生成失败')
    }
  } catch (error) {
    notification.error('SSL密钥对生成请求失败')
    console.error('SSL密钥对生成错误:', error)
  } finally {
    sslLoading.value = false
  }
}

const refreshSystemStatus = async () => {
  statusLoading.value = true
  try {
    const response = await fetch('/api/ops/encryption/status', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    const result = await response.json()
    
    if (result.success) {
      systemStatus.value = result.data
      notification.success('系统状态刷新成功')
    } else {
      notification.error(result.message || '获取系统状态失败')
    }
  } catch (error) {
    notification.error('系统状态请求失败')
    console.error('系统状态错误:', error)
  } finally {
    statusLoading.value = false
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    notification.success('已复制到剪贴板')
  } catch (error) {
    notification.error('复制失败')
  }
}

const formatDateTime = (isoString) => {
  return new Date(isoString).toLocaleString()
}

// 生命周期
onMounted(() => {
  refreshSystemStatus()
})
</script>

<style scoped>
.encryption-manager {
  /* 组件特定样式 */
}

/* 状态指示器 */
.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
}

.status-active {
  background-color: #10b981;
}

.status-inactive {
  background-color: #ef4444;
}

/* 代码样式 */
pre {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>