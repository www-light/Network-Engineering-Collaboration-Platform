import request from './request'

// 发起邀请/申请
export const applyAndInvite = (data) => {
  return request({
    url: '/cooperation/apply_and_invite',
    method: 'POST',
    data
  })
}

// 确认合作
export const confirmCooperation = (coId) => {
  return request({
    url: `/cooperations/${coId}/confirm`,
    method: 'POST'
  })
}

// 拒绝申请/邀请
export const rejectCooperation = (coId) => {
  return request({
    url: `/cooperations/${coId}/reject`,
    method: 'POST'
  })
}

// 检查是否有未完成流程
export const checkUnfinished = () => {
  return request({
    url: '/cooperations/check-unfinished',
    method: 'GET'
  })
}

