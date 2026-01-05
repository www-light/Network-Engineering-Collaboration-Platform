import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token && config.headers) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data
    
    // 如果没有 code 字段，直接返回（可能是其他格式的响应）
    if (res.code === undefined) {
      return res
    }
    
    // 如果返回的code是201（创建成功），返回完整响应以便前端处理
    if (res.code === 201) {
      return res
    }
    
    // 如果返回的code不是200，则视为错误
    if (res.code !== 200) {
      // 对于登录接口的账号不存在错误，不在这里显示消息，让store中的loginUser处理
      const isLoginError = response.config?.url?.includes('/auth/login')
      if (isLoginError && (res.msg?.includes('请先注册') || res.msg?.includes('不存在'))) {
        return Promise.reject(new Error(res.msg || '请先注册'))
      }
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    
    // code === 200 时，返回完整响应对象，让前端自己决定如何使用
    // 这样前端可以访问 code, msg, data 等字段
    return res
  },
  (error) => {
    console.error('Response error:', error)
    const message = error.response?.data?.msg || error.message || '请求失败'
    
    // 对于登录接口的账号不存在错误，不在这里显示消息，让store中的loginUser处理
    const isLoginError = error.config?.url?.includes('/auth/login')
    if (isLoginError) {
      // 登录错误统一交给 loginUser 捕获处理，避免重复提示
      return Promise.reject(error)
    }
    
    ElMessage.error(message)
    
    // 401未授权，清除token并跳转登录
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
    }
    
    return Promise.reject(error)
  }
)

export default service

