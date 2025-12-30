from django.urls import path
from .views import (
    health_check, register, login, like, favorite, comment,
    create_conversation, list_conversations, close_conversation,
    send_message, list_messages
)

urlpatterns = [
    path('health', health_check, name='health_check'),
    path('auth/register', register, name='register'),
    path('auth/login', login, name='login'),
    path('post/like', like, name='post_like'),
    path('post/favorite', favorite, name='post_favorite'),
    path('post/comment', comment, name='post_comment'),
    
    # 站内私信
    path('conversations', create_conversation, name='create_conversation'),
    path('conversations/lists', list_conversations, name='list_conversations'),
    path('conversations/<int:conversation_id>/close', close_conversation, name='close_conversation'),
    path('conversations/<int:conversation_id>/messages', send_message, name='send_message'),
    path('conversations/<int:conversation_id>/messages/lists', list_messages, name='list_messages'),
]

