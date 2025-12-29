from django.urls import path
from .views import health_check, register, login

urlpatterns = [
    path('health', health_check, name='health_check'),
    path('auth/register', register, name='register'),
    path('auth/login', login, name='login'),
]

