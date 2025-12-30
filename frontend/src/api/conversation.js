import request from './request'

// 发起会话
export const createConversation = (data) => {
  return request({
    url: '/convsersations',
    method: 'POST',
    data
  })
}

// 获取会话列表
export const getConversations = () => {
  return request({
    url: '/conversations/lists',
    method: 'GET'
  })
}

// 发送消息
export const sendMessage = (conversationId, data) => {
  return request({
    url: `/conversations/${conversationId}/messages`,
    method: 'POST',
    data
  })
}

// 获取消息列表
export const getMessages = (conversationId, params) => {
  return request({
    url: `/conversations/${conversationId}/messages/lists`,
    method: 'GET',
    params
  })
}

// 关闭对话
export const closeConversation = (conversationId) => {
  return request({
    url: `/conversations/${conversationId}/close`,
    method: 'PATCH'
  })
}

