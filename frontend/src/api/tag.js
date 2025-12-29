import request from './request'

// 获取所有标签
export const getTags = () => {
  return request({
    url: '/api/tags/',
    method: 'GET'
  })
}

// 创建自定义标签
export const createTag = (name) => {
  return request({
    url: '/api/tags/',
    method: 'POST',
    data: { name }
  })
}

