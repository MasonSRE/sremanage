<template>
  <div class="bg-white rounded-lg shadow p-6 h-full">
    <h2 class="text-xl font-semibold mb-6">JSON解析工具</h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 输入区域 -->
      <div class="flex flex-col">
        <div class="flex justify-between items-center mb-2">
          <label class="block text-sm font-medium text-gray-700">输入JSON</label>
          <button
            @click="formatInput"
            class="text-sm text-blue-600 hover:text-blue-800"
          >
            格式化
          </button>
        </div>
        <textarea
          v-model="inputJson"
          class="w-full h-[600px] p-4 border border-gray-300 rounded-md font-mono text-sm resize-none"
          placeholder="请输入要解析的JSON字符串..."
          @input="handleInput"
        ></textarea>
      </div>

      <!-- 输出区域 -->
      <div class="flex flex-col h-full">
        <div class="flex justify-between items-center mb-2">
          <label class="block text-sm font-medium text-gray-700">解析结果</label>
          <div class="space-x-2">
            <button
              @click="copyOutput"
              class="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
            >
              <span v-if="copySuccess" class="text-green-600">已复制!</span>
              <span v-else>复制</span>
            </button>
          </div>
        </div>
        <div
          class="w-full h-[600px] p-4 border border-gray-300 rounded-md overflow-auto bg-gray-50"
        >
          <JsonHighlight v-if="!error" :json="formattedOutput" />
          <div v-else class="text-red-500 text-sm">{{ error }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import JsonHighlight from './components/JsonHighlight.vue'

const inputJson = ref('')
const formattedOutput = ref('')
const error = ref('')
const copySuccess = ref(false)

const handleInput = () => {
  try {
    if (!inputJson.value.trim()) {
      formattedOutput.value = ''
      error.value = ''
      return
    }
    
    const parsed = JSON.parse(inputJson.value)
    formattedOutput.value = JSON.stringify(parsed, null, 2)
    error.value = ''
  } catch (e) {
    error.value = `解析错误: ${e.message}`
  }
}

const formatInput = () => {
  try {
    if (!inputJson.value.trim()) return
    const parsed = JSON.parse(inputJson.value)
    inputJson.value = JSON.stringify(parsed, null, 2)
    handleInput()
  } catch (e) {
    error.value = `格式化错误: ${e.message}`
  }
}

const copyOutput = async () => {
  try {
    await navigator.clipboard.writeText(formattedOutput.value)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (e) {
    error.value = '复制失败，请手动复制'
  }
}
</script>

<style scoped>
/* 添加一些过渡效果 */
.text-green-600 {
  transition: opacity 0.3s ease-in-out;
}
</style> 