from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..serializers import (
    RegisterSerializer,
    LoginSerializer,
    RegisterResponseSerializer,
    LoginResponseSerializer
)
from ..models import StudentEntity, TeacherEntity

@api_view(['POST'])
def register(request):
    """用户注册接口
    
    POST /auth/register
    请求参数:
    {
        "identity": 0,  # 0-学生, 1-教师
        "account": "675979030",  # 学号 or 教工号
        "name": "普梓豪",
        "password": "123456",
        "extra": {
            "grade": 2  # 学生需要
            # 或 "title": "教授"  # 教师需要
        }
    }
    
    返回:
    {
        "user_id": 6,
        "identity": 0
    }
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        response_serializer = RegisterResponseSerializer({
            'user_id': user.user_id,
            'identity': user.identity
        })
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    """用户登录接口
    
    POST /auth/login
    请求参数:
    {
        "identity": 0,  # 0-学生, 1-教师
        "account": "675979030",  # 学号 / 教工号
        "password": "123456"
    }
    
    返回:
    {
        "user_id": 6,
        "name:  "普梓豪",
        "identity": 0,
        "token": "xxxxx"
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        # 生成新的 token
        token = user.generate_token()
        
        response_serializer = LoginResponseSerializer({
            'user_id': user.user_id,
            'name': StudentEntity.objects.get(user_id=user.user_id).student_name if user.identity == 0 else TeacherEntity.objects.get(user_id=user.user_id).teacher_name,
            'identity': user.identity,
            'token': token
        })
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
