import request from './request'

export const likePost = (data) => {
  return request({
    url: '/post/like',
    method: 'POST',
    data
  })
}

export const unlikePost = (data) => {
  return request({
    url: '/post/unlike',
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

export const unfavoritePost = (data) => {
  return request({
    url: '/post/unfavorite',
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

export const getComments = (postId) => {
  return request({
    url: `/post/comment/${postId}`,
    method: 'GET'
  })
}
