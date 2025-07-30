import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../components/Layout/MainLayout.vue'
import Terminal from '../views/terminal/Terminal.vue'

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
      {
        path: 'ops/jenkins',
        name: 'jenkins',
        component: () => import('../views/ops/Jenkins.vue')
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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 修改路由守卫，添加更多日志
router.beforeEach((to, from, next) => {
  console.log('Route navigation:', { to, from });
  const token = localStorage.getItem('token');
  const tokenExpireTime = localStorage.getItem('tokenExpireTime');
  
  // 当前时间戳（毫秒）
  const now = Date.now();
  const isTokenExpired = tokenExpireTime && now > parseInt(tokenExpireTime);
  
  console.log('Auth state:', { 
    hasToken: !!token,
    tokenExpireTime,
    now,
    isExpired: isTokenExpired
  });

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token || isTokenExpired) {
      console.log('Auth required but no valid token, redirecting to login');
      if (isTokenExpired) {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('tokenExpireTime');
      }
      
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
    } else {
      console.log('Auth check passed, proceeding to:', to.path);
      next();
    }
  } else {
    if (token && !isTokenExpired && to.path === '/login') {
      console.log('Already logged in, redirecting to home');
      next('/');
    } else {
      console.log('No auth required, proceeding to:', to.path);
      next();
    }
  }
})

export default router