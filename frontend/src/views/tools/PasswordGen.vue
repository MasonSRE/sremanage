<template>
  <div class="space-y-4">
    <div class="bg-white rounded-lg p-6 shadow-sm">
      <h2 class="text-lg font-medium mb-4">强密码生成器</h2>
      
      <div class="space-y-4 max-w-xl">
        <!-- 选项设置 -->
        <div class="space-y-3">
          <div class="flex items-center">
            <input
              type="checkbox"
              id="uppercase"
              v-model="options.uppercase"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            >
            <label for="uppercase" class="ml-2 text-sm text-gray-700">包含大写字母</label>
          </div>
          
          <div class="flex items-center">
            <input
              type="checkbox"
              id="numbers"
              v-model="options.numbers"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            >
            <label for="numbers" class="ml-2 text-sm text-gray-700">包含数字</label>
          </div>
          
          <div class="flex items-center">
            <input
              type="checkbox"
              id="symbols"
              v-model="options.symbols"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            >
            <label for="symbols" class="ml-2 text-sm text-gray-700">包含特殊字符</label>
          </div>
          
          <div class="flex items-center space-x-4">
            <label class="text-sm text-gray-700">密码长度:</label>
            <input
              type="number"
              v-model="options.length"
              min="8"
              max="32"
              class="w-20 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-center"
            >
          </div>
        </div>

        <!-- 生成的密码显示 -->
        <div class="relative">
          <input
            type="text"
            v-model="generatedPassword"
            readonly
            class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
          <button
            @click="copyPassword"
            class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <ClipboardDocumentIcon class="h-5 w-5" />
          </button>
        </div>

        <!-- 生成按钮 -->
        <button
          @click="generatePassword"
          class="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          生成密码
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ClipboardDocumentIcon } from '@heroicons/vue/24/outline'

const options = ref({
  uppercase: true,
  numbers: true,
  symbols: true,
  length: 16
})

const generatedPassword = ref('')

const generatePassword = () => {
  const chars = {
    lowercase: 'abcdefghijklmnopqrstuvwxyz',
    uppercase: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    numbers: '0123456789',
    symbols: '!@#$%^&*()_+-=[]{}|;:,.<>?'
  }

  let availableChars = chars.lowercase
  if (options.value.uppercase) availableChars += chars.uppercase
  if (options.value.numbers) availableChars += chars.numbers
  if (options.value.symbols) availableChars += chars.symbols

  let password = ''
  for (let i = 0; i < options.value.length; i++) {
    const randomIndex = Math.floor(Math.random() * availableChars.length)
    password += availableChars[randomIndex]
  }

  generatedPassword.value = password
}

const copyPassword = async () => {
  try {
    await navigator.clipboard.writeText(generatedPassword.value)
    alert('密码已复制到剪贴板')
  } catch (err) {
    alert('复制失败')
  }
}
</script> 