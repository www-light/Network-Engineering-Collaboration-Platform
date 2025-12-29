from django.urls import path
from .views import health_check, register, login, like, favorite, comment

urlpatterns = [
    path('health', health_check, name='health_check'),
    path('auth/register', register, name='register'),
    path('auth/login', login, name='login'),
    path('post/like', like, name='post_like'),
    path('post/favorite', favorite, name='post_favorite'),
    path('post/comment', comment, name='post_comment'),
]

