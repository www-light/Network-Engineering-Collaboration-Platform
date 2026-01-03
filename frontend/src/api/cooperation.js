import request from './request'

// 学生申请
export const applyCooperation = (data) => {
  return request({
    url: '/cooperation/apply',
    method: 'POST',
    data
  })
}

// 教师邀请
export const inviteStudent = (data) => {
  return request({
    url: '/cooperation/invite',
    method: 'POST',
    data
  })
}

// 兼容旧接口：根据role自动分发
export const applyAndInvite = (data) => {
  const { role, ...rest } = data
  if (role === 0) {
    // 申请（学生）
    console.log('applyCooperation called with', rest)
    return applyCooperation(rest)
  } else if (role === 1) {
    // 邀请（教师）
    return inviteStudent(rest)
  }
  return Promise.reject(new Error('Invalid role'))
}

// 教师同意申请
export const approveApplication = (data) => {
  return request({
    url: '/cooperation/approve',
    method: 'POST',
    data
  })
}

// 教师拒绝申请
export const rejectApplication = (data) => {
  return request({
    url: '/cooperation/apply/reject',
    method: 'POST',
    data
  })
}

// 学生拒绝邀请
export const rejectInvitation = (data) => {
  return request({
    url: '/cooperation/invite/reject',
    method: 'POST',
    data
  })
}

// 学生取消申请
export const cancelApply = (data) => {
  return request({
    url: '/cooperation/apply/cancel',
    method: 'POST',
    data
  })
}

// 教师取消邀请
export const cancelInvite = (data) => {
  return request({
    url: '/cooperation/invite/cancel',
    method: 'POST',
    data
  })
}

// 学生同意邀请
export const agreeInvite = (data) => {
  return request({
    url: '/cooperation/agree',
    method: 'POST',
    data
  })
}

// 获取合作列表（支持分页）
export const listCooperations = (page = 1, pageSize = 10) => {
  return request({
    url: '/cooperation/list',
    method: 'GET',
    params: {
      page,
      page_size: pageSize
    }
  })
}

// 检查未完成的合作请求
export const checkUnfinished = () => {
  return request({
    url: '/cooperation/check-unfinished',
    method: 'GET'
  })
}

