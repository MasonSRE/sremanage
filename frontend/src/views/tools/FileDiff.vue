<template>
  <div class="space-y-4">
    <div class="bg-white rounded-lg p-6 shadow-sm">
      <h2 class="text-lg font-medium mb-4">文件对比工具</h2>
      
      <div class="grid grid-cols-2 gap-4">
        <!-- 左侧文件 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">文件 1</label>
          <textarea
            v-model="file1Content"
            rows="15"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="请输入或粘贴文件内容..."
            @input="updateDiff"
          ></textarea>
        </div>
        
        <!-- 右侧文件 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">文件 2</label>
          <textarea
            v-model="file2Content"
            rows="15"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="请输入或粘贴文件内容..."
            @input="updateDiff"
          ></textarea>
        </div>
      </div>

      <!-- 对比结果 -->
      <div class="mt-6">
        <h3 class="text-lg font-medium mb-4">对比结果</h3>
        <div class="border rounded-lg overflow-hidden">
          <div class="bg-gray-50 px-4 py-2 border-b">
            <div class="flex items-center space-x-4 text-sm">
              <div class="flex items-center">
                <span class="w-3 h-3 bg-green-100 rounded mr-1"></span>
                <span class="text-gray-600">相同内容</span>
              </div>
              <div class="flex items-center">
                <span class="w-3 h-3 bg-red-100 rounded mr-1"></span>
                <span class="text-gray-600">不同内容</span>
              </div>
            </div>
          </div>
          <div class="p-4 space-y-1 font-mono text-sm overflow-x-auto">
            <template v-for="(part, index) in diffResult" :key="index">
              <div
                :class="[
                  'px-2 py-1 rounded',
                  {
                    'bg-green-100': part.added === undefined && part.removed === undefined,
                    'bg-red-100': part.added || part.removed
                  }
                ]"
              >
                {{ part.value }}
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { diffLines } from 'diff'

const file1Content = ref('')
const file2Content = ref('')
const diffResult = ref([])

const updateDiff = () => {
  const diff = diffLines(file1Content.value, file2Content.value, {
    newlineIsToken: true,
    ignoreWhitespace: false
  })
  
  // 处理空行的情况
  diffResult.value = diff.map(part => {
    if (part.value === '') {
      return {
        ...part,
        value: '(空行)'
      }
    }
    return part
  })
}

// 监听内容变化
watch([file1Content, file2Content], () => {
  updateDiff()
}, { immediate: true })
</script>

<style scoped>
/* 自定义滚动条样式 */
.overflow-x-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}
</style> 