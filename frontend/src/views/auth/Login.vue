<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          登录系统
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">用户名</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="用户名"
            >
          </div>
          <div>
            <label for="password" class="sr-only">密码</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="密码"
            >
          </div>
          <div class="captcha-wrapper">
            <img 
              :src="captchaImage" 
              @click="refreshCaptcha" 
              alt="验证码"
              class="captcha-image"
            />
            <input 
              v-model="formData.captcha" 
              type="text" 
              placeholder="请输入验证码"
              class="captcha-input"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <LockClosedIcon class="h-5 w-5 text-blue-500 group-hover:text-blue-400" aria-hidden="true" />
            </span>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>

        <!-- 调试按钮区域 -->
        <div class="mt-4 space-y-2">
          <button 
            type="button" 
            @click="testSession" 
            class="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            测试会话
          </button>
          
          <button 
            type="button" 
            @click="testCaptcha" 
            class="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          >
            查看验证码存储
          </button>
          
          <button 
            type="button" 
            @click="testCookies" 
            class="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
          >
            自动登录测试
          </button>
          
          <div v-if="sessionTestResult" class="mt-2 text-sm text-gray-600 bg-gray-100 p-2 rounded overflow-auto max-h-32">
            {{ sessionTestResult }}
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { LockClosedIcon } from '@heroicons/vue/24/solid'
import { fetchApi } from '@/utils/api'  // 导入 API 工具

const router = useRouter()
const loading = ref(false)
const captchaImage = ref('')

const formData = ref({
  username: '',
  password: '',
  captcha: '',
  captcha_id: ''
})

const sessionTestResult = ref('');

const refreshCaptcha = async () => {
  try {
    const data = await fetchApi('/captcha', {
      method: 'GET'
    });
    
    if (data.success && data.data) {
      captchaImage.value = `data:image/png;base64,${data.data.image}`;
      formData.value.captcha_id = data.data.captcha_id;  // 保存验证码ID
      // 设置验证码自动刷新时间为后端返回的过期时间
      if (captchaTimer) {
        clearInterval(captchaTimer);
      }
      // 在过期前30秒刷新验证码
      const refreshTime = (data.data.expires - 30) * 1000;
      captchaTimer = setTimeout(refreshCaptcha, refreshTime);
    } else {
      throw new Error('获取验证码失败');
    }
  } catch (error) {
    console.error('获取验证码失败:', error);
    alert(error.message);
  }
};

// 添加验证码自动刷新
let captchaTimer = null

const handleLogin = async () => {
  try {
    loading.value = true;
    // 确保验证码ID存在
    if (!formData.value.captcha_id) {
      throw new Error('请先获取验证码');
    }
    const data = await fetchApi('/login', {
      method: 'POST',
      body: formData.value
    });
    
    console.log('Login response:', data);
    
    if (data.success) {
      console.log('Login successful, saving token...');
      
      // 保存登录信息
      localStorage.setItem('token', data.data.token);
      localStorage.setItem('username', data.data.username);
      localStorage.setItem('tokenExpireTime', String(data.data.expires * 1000));
      
      // 直接使用路由名称进行导航
      try {
        console.log('Attempting navigation to dashboard...');
        await router.push({ name: 'dashboard' });
        console.log('Navigation successful');
      } catch (navigationError) {
        console.error('Navigation failed, error:', navigationError);
        console.log('Trying fallback navigation...');
        // 回退方案：使用完整路径
        try {
          await router.push('/');
        } catch (error) {
          console.error('Fallback navigation failed, using location.href');
          window.location.href = '/';
        }
      }
    } else {
      alert(data.message || '登录失败');
      refreshCaptcha();
    }
  } catch (error) {
    console.error('Login error:', error);
    let errorMessage = '登录失败，请重试';
    
    if (error.message === 'Failed to fetch') {
      errorMessage = '无法连接到服务器，请检查:\n' +
        '1. 后端服务是否已启动(默认端口5000)\n' +
        '2. 网络连接是否正常';
    } else {
      errorMessage = error.message;
    }
    
    alert(errorMessage);
    refreshCaptcha();
  } finally {
    loading.value = false;
  }
};

// 测试会话功能
const testSession = async () => {
  try {
    const data = await fetchApi('/test-session', {
      method: 'GET'
    });
    console.log('Session test result:', data);
    sessionTestResult.value = JSON.stringify(data, null, 2);
  } catch (error) {
    console.error('Session test failed:', error);
    sessionTestResult.value = `测试失败: ${error.message}`;
  }
};

// 测试验证码功能
const testCaptcha = async () => {
  try {
    const data = await fetchApi('/test-captcha', {
      method: 'GET'
    });
    console.log('Captcha test result:', data);
    sessionTestResult.value = JSON.stringify(data, null, 2);
  } catch (error) {
    console.error('Captcha test failed:', error);
    sessionTestResult.value = `测试失败: ${error.message}`;
  }
};

// 测试浏览器Cookie
const testCookies = async () => {
  try {
    // 获取验证码测试数据
    const data = await fetchApi('/test-cookie', {
      method: 'GET'
    });
    console.log('Test captcha created:', data);
    
    // 获取测试验证码和ID
    const testCode = data.data.test_code;
    const testId = data.data.test_id;
    
    // 验证测试验证码
    const validationResult = await fetchApi('/login', {
      method: 'POST',
      body: {
        username: 'admin',
        password: 'admin123',
        captcha: testCode,
        captcha_id: testId
      }
    });
    
    console.log('Validation result:', validationResult);
    
    sessionTestResult.value = JSON.stringify({
      testCaptcha: data,
      validationResult: validationResult
    }, null, 2);
  } catch (error) {
    console.error('Test failed:', error);
    sessionTestResult.value = `测试失败: ${error.message}`;
  }
};

onMounted(() => {
  refreshCaptcha()
  // 每4分钟自动刷新验证码
  captchaTimer = setInterval(refreshCaptcha, 4 * 60 * 1000)
})

onUnmounted(() => {
  if (captchaTimer) {
    clearTimeout(captchaTimer)
  }
})
</script>

<style scoped>
.captcha-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.captcha-image {
  height: 40px;
  width: 120px;
  cursor: pointer;
  border: 1px solid #ddd;
  border-radius: 4px;
  object-fit: contain;
  background-color: #fff;
}

.captcha-input {
  flex: 1;
  height: 40px;
  padding: 0 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}
</style> 