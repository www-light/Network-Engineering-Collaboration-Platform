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

// 发布项目
export const publishProject = (data) => {
  return request({
    url: '/project/publish',
    method: 'POST',
    data
  })
}

