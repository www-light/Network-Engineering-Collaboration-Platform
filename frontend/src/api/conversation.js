import request from './request'

// 发起会话
export const createConversation = (data) => {
  return request({
    url: '/conversations/post',
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

// 获取自动回复设置
export const getAutoReplySettings = () => {
  return request({
    url: '/conversations/auto_reply/settings',
    method: 'GET'
  })
}

// 更新自动回复设置
export const updateAutoReplySettings = (data) => {
  return request({
    url: '/conversations/auto_reply/settings',
    method: 'PATCH',
    data
  })
}

// 上传会话文件
export const uploadConversationFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('post_id', -1)  // -1 表示会话中的文件
  return request({
    url: '/attachments/upload',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
