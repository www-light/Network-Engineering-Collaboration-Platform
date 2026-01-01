import request from './request'

// 获取项目列表
export const getProjects = (params) => {
  return request({
    url: '/project/list',
    method: 'GET',
    params
  })
}

// 获取项目详情（统一接口）
export const getProjectDetail = (postId) => {
  return request({
    url: `/project/detail/${postId}`,
    method: 'GET'
  })
}

// 获取科研项目详情（保留兼容性）
export const getResearchDetail = (postId) => {
  return getProjectDetail(postId)
}

// 获取大创/竞赛详情（保留兼容性）
export const getCompetitionDetail = (postId) => {
  return getProjectDetail(postId)
}

// 获取项目点赞收藏评论数
export const getProjectStats = (postId) => {
  return request({
    url: '/',
    method: 'GET',
    params: { post_id: postId }
  })
}

// 下载文件
export const downloadFile = (fileUrl) => {
  return request({
    url: '/files/download',
    method: 'GET',
    params: { file_url: fileUrl },
    responseType: 'blob'
  })
}

// 发布科研项目
export const publishResearch = (data) => {
  return request({
    url: '/publish/research',
    method: 'POST',
    data
  })
}

// 发布竞赛项目
export const publishCompetition = (data) => {
  return request({
    url: '/publish/competition',
    method: 'POST',
    data
  })
}

// 发布个人技能
export const publishPersonal = (data) => {
  return request({
    url: '/publish/personal',
    method: 'POST',
    data
  })
}

// 上传附件
export const uploadAttachment = (postId, file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('post_id', postId)
  return request({
    url: '/attachments/upload',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

