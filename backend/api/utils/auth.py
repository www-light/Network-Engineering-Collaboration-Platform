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


def teacher_required(view_func):
    """教师权限验证装饰器
    
    仅允许身份为教师(identity=1)的用户访问
    需要先通过 @login_required
    
    使用方式:
    @api_view(['POST'])
    @login_required
    @teacher_required
    def my_view(request):
        user = request.user  # 已验证的教师用户
        ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        
        if not user:
            return Response(
                {'code': 401, 'msg': '未登录'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if user.identity != 1:  # 1 = 教师
            return Response(
                {'code': 403, 'msg': '该操作仅限教师执行'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def student_required(view_func):
    """学生权限验证装饰器
    
    仅允许身份为学生(identity=0)的用户访问
    需要先通过 @login_required
    
    使用方式:
    @api_view(['POST'])
    @login_required
    @student_required
    def my_view(request):
        user = request.user  # 已验证的学生用户
        ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        
        if not user:
            return Response(
                {'code': 401, 'msg': '未登录'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if user.identity != 0:  # 0 = 学生
            return Response(
                {'code': 403, 'msg': '该操作仅限学生执行'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
