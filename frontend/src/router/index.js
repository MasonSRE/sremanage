import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../components/Layout/MainLayout.vue'
import Terminal from '../views/terminal/Terminal.vue'

// Jenkins组件静态导入
import JobList from '../views/jenkins/JobList.vue'
import JobWizard from '../views/jenkins/JobWizard.vue'
import BuildMonitor from '../views/jenkins/BuildMonitor.vue'
import InstanceManager from '../views/jenkins/InstanceManager.vue'
import Analytics from '../views/jenkins/Analytics.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/Login.vue')
  },
  {
    path: '/terminal',
    name: 'terminal',
    component: Terminal,
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('../views/dashboard/index.vue')
      },

      // 资产管理路由
      {
        path: 'assets/hosts',
        name: 'hosts',
        component: () => import('../views/assets/Hosts.vue')
      },
      {
        path: 'assets/sites',
        name: 'sites', 
        component: () => import('../views/assets/Sites.vue')
      },

      // 运维操作路由
      {
        path: 'ops/cdn-management',
        name: 'cdn-management',
        component: () => import('../views/ops/CdnManagement.vue')
      },
      // Jenkins管理路由群组 - 使用统一布局
      {
        path: 'jenkins',
        component: () => import('../components/jenkins/layout/JenkinsLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: '',
            redirect: '/jenkins/jobs'
          },
          {
            path: 'jobs',
            name: 'jenkins-jobs',
            component: JobList,
            meta: { title: '任务列表' }
          },
          {
            path: 'create',
            name: 'jenkins-create',
            component: JobWizard,
            meta: { title: '创建任务' }
          },
          {
            path: 'monitor',
            name: 'jenkins-monitor',
            component: BuildMonitor,
            meta: { title: '构建监控' }
          },
          {
            path: 'instances',
            name: 'jenkins-instances',
            component: InstanceManager,
            meta: { title: '实例管理' }
          },
          {
            path: 'analytics',
            name: 'jenkins-analytics',
            component: Analytics,
            meta: { title: '分析报告' }
          }
        ]
      },
      // 保留原有路由作为重定向
      {
        path: 'ops/jenkins',
        redirect: '/jenkins/jobs'
      },
      {
        path: 'ops/domain',
        name: 'domain',
        component: () => import('../views/ops/Domain.vue')
      },
      {
        path: 'ops/migration',
        name: 'migration',
        component: () => import('../views/ops/Migration.vue')
      },
      {
        path: 'ops/batch-command',
        name: 'batch-command',
        component: () => import('../views/ops/BatchCommand.vue')
      },

      // 工具操作路由
      {
        path: 'tools/file-diff',
        name: 'file-diff',
        component: () => import('../views/tools/FileDiff.vue')
      },
      {
        path: 'tools/password-gen',
        name: 'password-gen',
        component: () => import('../views/tools/PasswordGen.vue')
      },
      {
        path: 'tools/ping',
        name: 'ping',
        component: () => import('../views/tools/PingTool.vue')
      },
      {
        path: 'tools/json-parser',
        name: 'json-parser',
        component: () => import('../views/tools/JsonParser.vue')
      },
      // 用户权限路由
      {
        path: 'users',
        name: 'users',
        component: () => import('../views/users/index.vue')
      },
      // 项目管理路由
      {
        path: 'projects',
        name: 'projects',
        component: () => import('../views/projects/index.vue')
      },
      // 系统设置路由
      {
        path: 'settings/notification',
        name: 'notification',
        component: () => import('../views/settings/Notification.vue')
      },
      {
        path: 'settings/cloud-providers',
        name: 'cloud-providers',
        component: () => import('../views/settings/CloudProviders.vue')
      },
      {
        path: 'settings/aliyun',
        name: 'aliyun',
        component: () => import('../views/settings/Aliyun.vue'),
        meta: { deprecated: true }  // 标记为已弃用，保持向后兼容
      },
      {
        path: 'settings/mail',
        name: 'mail',
        component: () => import('../views/settings/Mail.vue')
      },
      {
        path: 'settings/jenkins',
        name: 'jenkins-settings',
        component: () => import('../views/settings/Jenkins.vue')
      },
      
      // 批量执行路由
      {
        path: 'batch-execute',
        name: 'batch-execute',
        component: () => import('../views/batch/BatchExecute.vue')
      },
      
      // AI助手路由
      {
        path: 'ai/docker-generator',
        name: 'docker-generator',
        component: () => import('../views/ai/DockerGenerator.vue')
      },
      {
        path: 'ai/sre-assistant',
        name: 'sre-assistant',
        component: () => import('../views/ai/SREAssistant.vue')
      },
      
      // 测试路由
      {
        path: 'test/simple',
        name: 'simple-test',
        component: () => import('../views/test/SimpleTest.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 临时完全禁用路由守卫用于调试
router.beforeEach((to, from, next) => {
  console.log('Router beforeEach - navigating to:', to.path);
  next();
})

export default router