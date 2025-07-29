<template>
  <div class="bg-black h-screen p-4">
    <div id="terminal" class="h-full w-full"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

const route = useRoute()
const term = new Terminal({
  cursorBlink: true,
  theme: {
    background: '#000000',
    foreground: '#ffffff'
  }
})
const fitAddon = new FitAddon()
let socket = null

onMounted(() => {
  const { hostname, ip, port, username, instance_id, provider } = route.query

  // 初始化终端
  term.loadAddon(fitAddon)
  term.open(document.getElementById('terminal'))
  fitAddon.fit()

  // 构建WebSocket连接URL
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  let wsUrl = `${wsProtocol}//${window.location.hostname}:5000/api/terminal?host=${ip}&port=${port}&username=${username}`
  
  // 如果是阿里云实例，添加额外参数
  if (provider === 'aliyun' && instance_id) {
    wsUrl += `&instance_id=${instance_id}&provider=${provider}`
  }
  
  console.log('Connecting to WebSocket:', wsUrl)  // 添加调试日志
  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    console.log('WebSocket connected')  // 添加调试日志
    term.writeln('Connected to ' + hostname)
  }

  socket.onmessage = (event) => {
    term.write(event.data)
  }

  socket.onerror = (error) => {
    console.error('WebSocket error:', error)  // 添加调试日志
    term.writeln('\r\nError: ' + error.message)
  }

  socket.onclose = () => {
    term.writeln('\r\nConnection closed')
    // 可以添加重连逻辑
  }

  // 监听终端输入
  term.onData(data => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(data)
    }
  })

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

const handleResize = () => {
  fitAddon.fit()
  if (socket && socket.readyState === WebSocket.OPEN) {
    const dimensions = term.rows + ',' + term.cols
    socket.send(`resize:${dimensions}`)
  }
}

onBeforeUnmount(() => {
  if (socket) {
    socket.close()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style>
.xterm {
  height: 100%;
}
</style> 