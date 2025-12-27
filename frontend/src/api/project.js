import request from './request'

// 获取项目列表
export const getProjects = (params) => {
  return request({
    url: '/projects',
    method: 'GET',
    params
  })
}

// 获取科研项目详情
export const getResearchDetail = (postId) => {
  return request({
    url: `/posts/${postId}/detail/research`,
    method: 'GET'
  })
}

// 获取大创/竞赛详情
export const getCompetitionDetail = (postId) => {
  return request({
    url: `/posts/${postId}/competition`,
    method: 'GET'
  })
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

