"""
认证相关工具函数
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from ..models.user import User


def get_user_from_token(request):
    """从请求头中提取token并获取用户
    
    期望的请求头格式：
    Authorization: Bearer <token>
    或
    Authorization: <token>
    
    返回:
        User对象 或 None
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header:
        return None
    
    # 支持 "Bearer token" 和直接 "token" 两种格式
    token = auth_header.replace('Bearer ', '').strip()
    
    if not token:
        return None
    
    try:
        user = User.objects.get(token=token)
        return user
    except User.DoesNotExist:
        return None


def login_required(view_func):
    """登录验证装饰器
    
    使用方式:
    @login_required
    def my_view(request):
        user = request.user  # 已认证的用户对象
        ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_user_from_token(request)
        
        if not user:
            return Response(
                {'code': 401, 'msg': '未登录或token无效'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 将用户对象附加到request上
        request.user = user
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_conversation_permission(user, conversation):
    """检查用户是否有权限访问该会话
    
    Args:
        user: User对象
        conversation: Conversation对象
    
    Returns:
        bool: 有权限返回True，否则False
    """
    return (conversation.user1_id == user.user_id or 
            conversation.user2_id == user.user_id)
