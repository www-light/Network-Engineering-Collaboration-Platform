import request from './request'

export const likePost = (data) => {
  return request({
    url: '/post/like',
    method: 'POST',
    data
  })
}

export const favoritePost = (data) => {
  return request({
    url: '/post/favorite',
    method: 'POST',
    data
  })
}

export const commentPost = (data) => {
  return request({
    url: '/post/comment',
    method: 'POST',
    data
  })
}
