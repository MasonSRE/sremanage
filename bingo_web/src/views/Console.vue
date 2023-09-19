<template>
  <div className="console">
    <div id="terminal"></div>
  </div>
</template>

<script setup>
import {onMounted} from "vue";
import {Terminal} from 'xterm'
import settings from "../settings";
import {useRoute} from "vue-router"

const route = useRoute()

// 因爲xterm终端需要修改HTML代码，所以必须等vue显示了页面内容以后才能执行xterm相关的代码
onMounted(
    () => {
      let term = new Terminal({
        rendererType: 'canvas', // 渲染类型
        cols: 100, // 列数
        rows: 50, // 行数
        convertEol: true, // 启用时，光标将设置为下一行的开头
        scrollback: 100, // 终端中的回滚量
        disableStdin: false, // 是否应禁用输入。
        cursorStyle: 'underline', // 光标样式
        cursorBlink: true, // 光标闪烁
        theme: {
          foreground: '#ffffff', // 字体
          background: '#060101', // 背景色
          cursor: 'help' // 设置光标
        }
      })

      // 连接Websocket
      let ws = new WebSocket(`${settings.wsHost}/host/${route.params.id}/console`)
      let cmd = '';  // 拼接用户输入的内容

      ws.onmessage = (event) => {

        console.log("cmd:", cmd)
        console.log("event.data:", event.data)

        if (!cmd) {
          //所要执行的操作
          term.write(event.data);
        } else {
          cmd = ''
          term.write(event.data)
        }
      }

      term.prompt = () => {
        term.write('\r\n')
      }

      // 当用户按了键盘时
      term.onKey(e => {
        console.log(e.key)
        const ev = e.domEvent
        const printable = !ev.altKey && !ev.altGraphKey && !ev.ctrlKey && !ev.metaKey

        if (ev.key === "Enter") { // 回车
          // 按下回车键进行指令的发送
          console.log("cmd", cmd)
          ws.send(cmd)
          term.write('\r\n')
        } else if (ev.key === "Backspace") { // 删除
          cmd = cmd.slice(0, cmd.length - 1)
          // Do not delete the prompt
          if (term._core.buffer.x > 2) {
            term.write('\b \b')
          }
        } else if (printable) {
          term.write(e.key)
          cmd += e.key
        }
      })

      // 显示一个ssh终端窗口
      term.open(document.getElementById('terminal'))
    }
)
</script>

<style scoped>

</style>