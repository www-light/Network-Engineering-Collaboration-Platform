import request from './request'

// 登录
export const login = (data) => {
  return request({
    url: '/auth/login',
    method: 'POST',
    data
  })
}

// 注册
export const register = (data) => {
  return request({
    url: '/auth/register',
    method: 'POST',
    data
  })
}

// 获取用户资料
export const getUserProfile = () => {
  return request({
    url: '/auth/profile',
    method: 'GET'
  })
}

// 更新用户资料
export const updateUserProfile = (data) => {
  return request({
    url: '/auth/profile',
    method: 'PUT',
    data
  })
}
