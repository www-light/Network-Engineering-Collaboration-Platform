import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const token = ref('')

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isTeacher = computed(() => userInfo.value?.identity === 1)
  const isStudent = computed(() => userInfo.value?.identity === 0)

  // 登录
  const loginUser = async (data) => {
    try {
      const response = await login(data)
      token.value = response.token
      userInfo.value = {
        user_id: response.user_id,
        identity: response.identity,
        account: data.account,
        name: response.name,
        token: response.token
      }
      // 保存到localStorage
      localStorage.setItem('token', response.token)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      ElMessage.success('登录成功')
      return response
    } catch (error) {
      const errData = error.response?.data || {}
      const status = error.response?.status

      // 优先读取后端的错误提示（serializer.errors可能返回对象或数组）
      const nonFieldError = Array.isArray(errData.non_field_errors) ? errData.non_field_errors[0] : null
      const accountError = Array.isArray(errData.account) ? errData.account[0] : null
      const msg = errData.msg || nonFieldError || accountError || errData.detail || error.message || ''

      if (status === 400) {
        // 账号不存在或密码错误等登录失败场景
        ElMessage.error(msg || '账号不存在或密码错误')
      } else {
        ElMessage.error(msg || '登录失败')
      }
      throw error
    }
  }

  // 注册
  const registerUser = async (data) => {
    try {
      const response = await register(data)
      userInfo.value = {
        user_id: response.user_id,
        identity: response.identity,
        account: data.account,
        name: data.name
      }
      ElMessage.success('注册成功，请登录')
      return response
    } catch (error) {
      ElMessage.error('注册失败')
      throw error
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    ElMessage.success('已退出登录')
  }

  // 初始化（从localStorage恢复）
  const init = () => {
    const savedToken = localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('userInfo')
    if (savedToken && savedUserInfo) {
      token.value = savedToken
      userInfo.value = JSON.parse(savedUserInfo)
    }
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    isTeacher,
    isStudent,
    loginUser,
    registerUser,
    logout,
    init
  }
})

