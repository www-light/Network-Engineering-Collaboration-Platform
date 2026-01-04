from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..serializers import (
    RegisterSerializer,
    LoginSerializer,
    RegisterResponseSerializer,
    LoginResponseSerializer
)
from ..models import StudentEntity, TeacherEntity, User, TeacherStudentCooperation
from ..utils.auth import login_required, get_user_from_token
from django.db.models import Q, Count

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


@api_view(['GET', 'PUT'])
@login_required
def user_profile(request):
    """获取/更新用户资料接口
    
    GET /auth/profile
    返回当前用户的资料信息
    
    PUT /auth/profile
    更新当前用户的资料信息
    {
        "past_achievements": "xxx"  # 仅教师可编辑
    }
    """
    user = get_user_from_token(request)
    
    if request.method == 'GET':
        # 获取用户资料
        if user.identity == 0:  # 学生
            try:
                student = StudentEntity.objects.get(user_id=user.user_id)
                return Response({
                    'code': 200,
                    'data': {
                        'user_id': user.user_id,
                        'identity': user.identity,
                        'name': student.student_name,
                        'account': student.student_id,
                        'grade': student.grade,
                        'extra': {'grade': student.grade}
                    }
                }, status=status.HTTP_200_OK)
            except StudentEntity.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '学生实体不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:  # 教师
            try:
                teacher = TeacherEntity.objects.get(user_id=user.user_id)
                # 计算组队成功率：该教师参与的所有协作中，已确认(status=3)的占比
                total_cooperations = TeacherStudentCooperation.objects.filter(
                    teacher_id=teacher.teacher_id
                ).count()
                
                # 同意的合作（status=3）
                approved_cooperations = TeacherStudentCooperation.objects.filter(
                    teacher_id=teacher.teacher_id,
                    status=3
                ).count()
                
                success_rate = 0.0
                if total_cooperations > 0:
                    success_rate = round(approved_cooperations / total_cooperations * 100, 2)
                
                return Response({
                    'code': 200,
                    'data': {
                        'user_id': user.user_id,
                        'identity': user.identity,
                        'name': teacher.teacher_name,
                        'account': teacher.teacher_id,
                        'title': teacher.title,
                        'past_achievements': teacher.past_achievements or '',
                        'success_rate': success_rate,
                        'total_cooperations': total_cooperations,
                        'approved_cooperations': approved_cooperations,
                        'extra': {'title': teacher.title}
                    }
                }, status=status.HTTP_200_OK)
            except TeacherEntity.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '教师实体不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    elif request.method == 'PUT':
        # 更新用户资料
        if user.identity == 0:  # 学生不能通过该接口更新
            return Response(
                {'code': 403, 'msg': '学生不能通过该接口更新资料'},
                status=status.HTTP_403_FORBIDDEN
            )
        else:  # 教师
            try:
                teacher = TeacherEntity.objects.get(user_id=user.user_id)
                # 只能更新past_achievements字段
                if 'past_achievements' in request.data:
                    teacher.past_achievements = request.data.get('past_achievements', '')
                    teacher.save()
                
                # 计算组队成功率
                total_cooperations = TeacherStudentCooperation.objects.filter(
                    teacher_id=teacher.teacher_id
                ).count()
                approved_cooperations = TeacherStudentCooperation.objects.filter(
                    teacher_id=teacher.teacher_id,
                    status=3
                ).count()
                
                success_rate = 0.0
                if total_cooperations > 0:
                    success_rate = round(approved_cooperations / total_cooperations * 100, 2)
                
                return Response({
                    'code': 200,
                    'msg': '更新成功',
                    'data': {
                        'user_id': user.user_id,
                        'identity': user.identity,
                        'name': teacher.teacher_name,
                        'account': teacher.teacher_id,
                        'title': teacher.title,
                        'past_achievements': teacher.past_achievements or '',
                        'success_rate': success_rate,
                        'total_cooperations': total_cooperations,
                        'approved_cooperations': approved_cooperations
                    }
                }, status=status.HTTP_200_OK)
            except TeacherEntity.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '教师实体不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

