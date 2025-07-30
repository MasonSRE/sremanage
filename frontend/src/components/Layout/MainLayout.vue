<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 侧边栏背景色改为深色渐变 -->
    <div
      :class="[
        'fixed inset-y-0 left-0 z-50 transition-all duration-300 bg-gradient-to-b from-gray-800 to-gray-900',
        collapsed ? 'w-16' : 'w-64'
      ]"
    >
      <!-- Logo 部分改造 -->
      <div class="h-16 flex items-center justify-between px-4 border-b border-gray-700/50">
        <div class="flex items-center">
          <img src="@/assets/logo.svg" alt="Logo" class="w-8 h-8 mr-3" />
          <span v-if="!collapsed" class="modern-logo-text">
            运维管理平台
          </span>
        </div>
        <button
          @click="toggleSidebar"
          class="modern-collapse-btn"
          :title="collapsed ? '展开菜单' : '收起菜单'"
        >
          <Bars3Icon class="h-5 w-5" />
        </button>
      </div>

      <!-- 菜单部分改造 -->
      <nav class="mt-6 px-2">
        <template v-for="menu in menus" :key="menu.key">
          <div class="mb-2">
            <button
              @click="handleMenuClick(menu.key)"
              :class="[
                'modern-menu-item',
                activeMenu === menu.key ? 'modern-menu-item-active' : '',
                menu.disabled ? 'menu-item-disabled' : ''
              ]"
              :disabled="menu.disabled"
            >
              <component :is="menu.icon" class="h-5 w-5" />
              <span v-if="!collapsed" class="ml-3" :class="{ 'line-through': menu.disabled }">
                {{ menu.label }}
              </span>
            </button>

            <!-- 子菜单样式改造 -->
            <div v-if="!collapsed && menu.children && activeMenu === menu.key" 
                 class="modern-submenu-container">
              <router-link
                v-for="submenu in menu.children"
                :key="submenu.key"
                :to="{ name: submenu.key }"
                :class="[
                  'modern-submenu-item',
                  $route.name === submenu.key ? 'modern-submenu-item-active' : ''
                ]"
              >
                <component :is="submenu.icon" class="h-4 w-4" />
                <span class="ml-3">{{ submenu.label }}</span>
              </router-link>
            </div>
          </div>
        </template>
      </nav>
    </div>

    <!-- 主内容区 -->
    <div :class="['main-content', collapsed ? 'ml-16' : 'ml-64']">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="flex justify-between items-center w-full">
          <h1 class="page-title">
            {{ currentMenuTitle }}
          </h1>
          <div class="flex items-center">
            <span class="mr-4 text-gray-600">{{ username }}</span>
            <button
              @click="handleLogout"
              class="px-3 py-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-200"
            >
              退出登录
            </button>
          </div>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="p-6">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router' 
import {
  Bars3Icon,
  HomeIcon,
  CloudIcon,
  ComputerDesktopIcon,
  UsersIcon,
  FolderIcon,
  ArrowPathIcon,
  FireIcon,
  WrenchScrewdriverIcon,
  GlobeAltIcon,
  ArrowsRightLeftIcon,
  DevicePhoneMobileIcon,
  ServerIcon,
  KeyIcon,
  CalendarIcon,
  CircleStackIcon,
  CalculatorIcon,
  DocumentDuplicateIcon,
  SignalIcon,
  Cog6ToothIcon,
  BellIcon,
  EnvelopeIcon,
  CubeIcon,
  CommandLineIcon,
  SparklesIcon,
  RocketLaunchIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter() 
const collapsed = ref(false)
const activeMenu = ref('dashboard')
const username = ref(localStorage.getItem('username'))

const menus = [
  {
    key: 'dashboard',
    icon: HomeIcon,
    label: '控制台概览'
  },
  {
    key: 'assets',
    icon: ServerIcon,
    label: '资产管理',
    children: [
      { key: 'hosts', icon: ComputerDesktopIcon, label: '主机列表' },
      { key: 'sites', icon: GlobeAltIcon, label: '站点监控' }
    ]
  },
  {
    key: 'ops',
    icon: CloudIcon,
    label: '运维操作',
    children: [
      { key: 'cdn-management', icon: CloudIcon, label: 'CDN管理' },
      { key: 'jenkins', icon: WrenchScrewdriverIcon, label: 'Jenkins管理' },
      { key: 'domain', icon: GlobeAltIcon, label: '域名管理' },
      { key: 'migration', icon: ArrowsRightLeftIcon, label: '迁移计划' },
      { key: 'batch-command', icon: CommandLineIcon, label: '批量操作' }
    ]
  },
  {
    key: 'tools',
    icon: ComputerDesktopIcon,
    label: '工具操作',
    children: [
      { key: 'file-diff', icon: DocumentDuplicateIcon, label: '文件对比' },
      { key: 'password-gen', icon: KeyIcon, label: '强密码生成器' },
      { key: 'ping', icon: SignalIcon, label: '多地Ping工具' },
      { key: 'json-parser', icon: DocumentDuplicateIcon, label: 'JSON解析工具' }
    ]
  },
  {
    key: 'batch-execute',
    icon: CommandLineIcon,
    label: '批量执行'
  },
  {
    key: 'ai-assistant',
    icon: SparklesIcon,
    label: 'AI助手',
    children: [
      { key: 'docker-generator', icon: CubeIcon, label: 'Docker配置生成器' },
      { key: 'sre-assistant', icon: WrenchScrewdriverIcon, label: 'SRE助手' }
    ]
  },
  {
    key: 'users',
    icon: UsersIcon,
    label: '用户权限',
    disabled: true
  },
  {
    key: 'settings',
    icon: Cog6ToothIcon,
    label: '系统设置',
    children: [
      { key: 'notification', icon: BellIcon, label: '告警设置' },
      { key: 'cloud-providers', icon: CloudIcon, label: '云厂商配置' },
      { key: 'mail', icon: EnvelopeIcon, label: '邮箱配置' },
      { key: 'jenkins-settings', icon: WrenchScrewdriverIcon, label: 'Jenkins配置' }
    ]
  }
]

const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

const handleMenuClick = (menuKey) => {
  activeMenu.value = menuKey

  // 添加路由跳转逻辑
  const menu = menus.find(m => m.key === menuKey)
  if (!menu?.children) {
    // 如果点击的菜单没有子菜单，则进行路由跳转
    router.push({ name: menuKey })
  }
}

const currentMenuTitle = computed(() => {
  const currentMenu = menus.find(m => {
    if (m.children) {
      return m.children.some(sub => sub.key === route.name)
    }
    return m.key === route.name
  })

  if (!currentMenu) return ''

  if (currentMenu.children) {
    const currentSubmenu = currentMenu.children.find(sub => sub.key === route.name)
    if (currentSubmenu) {
      return `${currentMenu.label} / ${currentSubmenu.label}`
    }
  }

  return currentMenu.label
})

const handleLogout = () => {
  // 调用后端登出接口
  fetch('http://localhost:5000/api/logout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  }).finally(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
  })
}
</script>

<style scoped>
/* 新增现代化样式 */
.modern-logo-text {
  @apply text-lg font-semibold tracking-wide;
  background: linear-gradient(135deg, #60A5FA 0%, #34D399 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.modern-collapse-btn {
  @apply p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10
         transition-all duration-200 ease-in-out backdrop-blur-sm;
}

.modern-menu-item {
  @apply w-full flex items-center px-3 py-2.5 rounded-lg text-gray-300
         hover:text-white hover:bg-white/10 transition-all duration-200
         font-medium tracking-wide text-sm;
}

.modern-menu-item-active {
  @apply bg-white/10 text-white;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
}

.modern-submenu-container {
  @apply mt-2 ml-4 space-y-1;
}

.modern-submenu-item {
  @apply flex items-center px-3 py-2 rounded-lg text-gray-400
         hover:text-white hover:bg-white/5 transition-all duration-200
         text-sm tracking-wide;
}

.modern-submenu-item-active {
  @apply bg-white/5 text-white;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.03);
}

/* 添加鼠标悬停时的微妙缩放效果 */
.modern-menu-item:hover,
.modern-submenu-item:hover {
  transform: translateX(4px);
}

/* 为激活状态添加微光效果 */
.modern-menu-item-active::before,
.modern-submenu-item-active::before {
  content: '';
  position: absolute;
  left: 0;
  width: 3px;
  height: 20px;
  background: linear-gradient(135deg, #60A5FA 0%, #34D399 100%);
  border-radius: 0 4px 4px 0;
}

/* 添加平滑滚动 */
nav {
  @apply overflow-y-auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

nav::-webkit-scrollbar {
  width: 4px;
}

nav::-webkit-scrollbar-track {
  background: transparent;
}

nav::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

.main-content {
  @apply transition-all duration-300;
}

.header {
  @apply h-16 bg-white shadow-sm flex items-center px-6;
}

.page-title {
  @apply text-xl font-semibold text-gray-800;
}

/* 新增Logo相关样式 */
img {
  @apply transition-transform duration-200;
}

img:hover {
  transform: rotate(15deg);
}

.menu-item-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
</style>