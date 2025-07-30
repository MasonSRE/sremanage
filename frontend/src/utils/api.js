const API_BASE_URL = '/api';

// 创建基础的API客户端
const api = {
  async get(url, config = {}) {
    return await this.request(url, { ...config, method: 'GET' })
  },
  
  async post(url, data = null, config = {}) {
    return await this.request(url, { ...config, method: 'POST', data })
  },
  
  async put(url, data = null, config = {}) {
    return await this.request(url, { ...config, method: 'PUT', data })
  },
  
  async delete(url, config = {}) {
    return await this.request(url, { ...config, method: 'DELETE' })
  },
  
  async request(url, config = {}) {
    const token = localStorage.getItem('token')
    
    const options = {
      method: config.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...config.headers
      },
      credentials: 'include',
      ...config
    }
    
    if (config.data && (config.method === 'POST' || config.method === 'PUT')) {
      options.body = JSON.stringify(config.data)
    }
    
    console.debug('API Request:', options.method, `${API_BASE_URL}${url}`, config.data)
    
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, options)
      
      // 安全地解析JSON响应 - 先读取文本避免body stream重复读取问题
      const responseText = await response.text()
      let data
      
      if (responseText.trim()) {
        try {
          data = JSON.parse(responseText)
        } catch (parseError) {
          console.error(`JSON parse error for ${url}:`, parseError)
          console.error('Response text that failed to parse:', responseText)
          throw new Error(`服务器返回了无效的JSON响应: ${parseError.message}`)
        }
      } else {
        data = { success: true, message: 'Empty response' }
      }
      
      console.debug('API Response:', options.method, `${API_BASE_URL}${url}`, data)
      
      // 处理401错误
      if (response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        localStorage.removeItem('tokenExpireTime')
        
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        throw new Error('登录已过期，请重新登录')
      }
      
      if (!response.ok) {
        throw new Error(data.message || `请求失败(${response.status})`)
      }
      
      return { data }
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }
}

export default api

export const fetchApi = async (endpoint, options = {}) => {
  try {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token');
    
    const config = {
      ...options,
      credentials: 'include',  // 确保包含Cookie
      mode: 'cors',  // 明确使用CORS模式
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        'Cache-Control': 'no-cache',  // 防止缓存
        ...options.headers
      }
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    // 安全地解析JSON响应 - 先读取文本避免body stream重复读取问题
    let data;
    const responseText = await response.text();
    
    if (responseText.trim()) {
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        console.error(`JSON parse error for ${endpoint}:`, parseError);
        console.error('Response text that failed to parse:', responseText);
        throw new Error(`服务器返回了无效的JSON响应: ${parseError.message}`);
      }
    } else {
      // 空响应，设置为默认结构
      data = { success: true, message: 'Empty response' };
    }
    
    // 检查是否是 token 过期
    if (!response.ok && (
      data.message?.includes('Token has expired') || 
      data.message?.includes('Invalid token') ||
      response.status === 401
    )) {
      // 清除本地存储的登录信息
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('tokenExpireTime');
      
      // 如果不在登录页面，则重定向到登录页
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
      throw new Error('登录已过期，请重新登录');
    }

    if (!response.ok) {
      throw new Error(data.message || `请求失败(${response.status})`);
    }

    return data;
  } catch (error) {
    if (error.message === 'Failed to fetch') {
      throw new Error('无法连接到服务器，请检查后端服务是否正常运行');
    }
    throw error;
  }
}; 