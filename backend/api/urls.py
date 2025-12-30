from django.urls import path
from .views import (
    health_check, register, login, like, unlike, favorite, unfavorite, comment, list_comments,
    create_conversation, list_conversations, close_conversation,
    send_message, list_messages,
    tags,
    publish_project, list_projects, get_project_detail
)

urlpatterns = [
    path('health', health_check, name='health_check'),
    path('auth/register', register, name='register'),
    path('auth/login', login, name='login'),
    path('post/like', like, name='post_like'),
    path('post/unlike', unlike, name='post_unlike'),
    path('post/favorite', favorite, name='post_favorite'),
    path('post/unfavorite', unfavorite, name='post_unfavorite'),
    path('post/comment', comment, name='post_comment'),
    path('post/comment/<int:post_id>', list_comments, name='list_comments'),
    
    # 站内私信
    path('conversations', create_conversation, name='create_conversation'),
    path('conversations/lists', list_conversations, name='list_conversations'),
    path('conversations/<int:conversation_id>/close', close_conversation, name='close_conversation'),
    path('conversations/<int:conversation_id>/messages', send_message, name='send_message'),
    path('conversations/<int:conversation_id>/messages/lists', list_messages, name='list_messages'),
    
    # 标签
    path('tags/', tags, name='tags'),
    
    # 项目发布
    path('project/publish', publish_project, name='publish_project'),
    # 项目列表
    path('project/list', list_projects, name='list_projects'),
    # 项目详情
    path('project/detail/<int:post_id>', get_project_detail, name='get_project_detail'),
]

