<template>
  <div class="json-highlight font-mono text-sm">
    <pre v-html="highlightedJson"></pre>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  json: {
    type: String,
    required: true
  }
})

const highlightedJson = computed(() => {
  try {
    // 如果输入是字符串形式的JSON，先解析它
    const obj = typeof props.json === 'string' ? JSON.parse(props.json) : props.json
    // 重新格式化JSON并添加高亮
    return syntaxHighlight(JSON.stringify(obj, null, 2))
  } catch (e) {
    return props.json
  }
})

function syntaxHighlight(json) {
  // 转义HTML特殊字符
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  
  // 使用正则表达式为不同类型添加样式
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
    let cls = 'json-number' // 数字
    if (/^"/.test(match)) {
      if (/:$/.test(match)) {
        cls = 'json-key' // 键名
      } else {
        cls = 'json-string' // 字符串
      }
    } else if (/true|false/.test(match)) {
      cls = 'json-boolean' // 布尔值
    } else if (/null/.test(match)) {
      cls = 'json-null' // null
    }
    return '<span class="' + cls + '">' + match + '</span>'
  })
}
</script>

<style scoped>
.json-highlight {
  line-height: 1.5;
}

/* 键名 */
:deep(.json-key) {
  color: #881391;
}

/* 字符串 */
:deep(.json-string) {
  color: #268bd2;
}

/* 数字 */
:deep(.json-number) {
  color: #b58900;
}

/* 布尔值 */
:deep(.json-boolean) {
  color: #859900;
}

/* null */
:deep(.json-null) {
  color: #dc322f;
}

/* 缩进指示线 */
.json-highlight pre {
  position: relative;
  padding-left: 0.5rem;
}

/* 添加悬停效果 */
:deep(.json-key),
:deep(.json-string),
:deep(.json-number),
:deep(.json-boolean),
:deep(.json-null) {
  transition: background-color 0.2s;
  border-radius: 2px;
  padding: 0 2px;
}

:deep(.json-key):hover,
:deep(.json-string):hover,
:deep(.json-number):hover,
:deep(.json-boolean):hover,
:deep(.json-null):hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style> 