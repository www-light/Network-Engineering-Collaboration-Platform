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
    
    // 如果返回的code不是200，则视为错误
    if (res.code !== undefined && res.code !== 200) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    
    // 如果有code且为200，返回data字段
    if (res.code === 200 && res.data !== undefined) {
      return res.data
    }
    
    // 如果直接返回数据（没有code字段），直接返回
    return res
  },
  (error) => {
    console.error('Response error:', error)
    const message = error.response?.data?.msg || error.message || '请求失败'
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

