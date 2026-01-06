from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..serializers import (
    RegisterSerializer,
    LoginSerializer,
    RegisterResponseSerializer,
    LoginResponseSerializer
)
from ..models import StudentEntity, TeacherEntity, User
from ..models import PostEntity, SkillInformation
from ..models import Skill, StudentSkill
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
                return Response({
                    'code': 200,
                    'data': {
                        'user_id': user.user_id,
                        'identity': user.identity,
                        'name': teacher.teacher_name,
                        'account': teacher.teacher_id,
                        'title': teacher.title,
                        'past_achievements': teacher.past_achievements or '',
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
                
                return Response({
                    'code': 200,
                    'msg': '更新成功',
                    'data': {
                        'user_id': user.user_id,
                        'identity': user.identity,
                        'name': teacher.teacher_name,
                        'account': teacher.teacher_id,
                        'title': teacher.title,
                        'past_achievements': teacher.past_achievements or ''
                    }
                }, status=status.HTTP_200_OK)
            except TeacherEntity.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '教师实体不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )


@api_view(['GET'])
def get_user_info(request, user_id):
    """获取指定用户的基本信息接口
    
    GET /auth/user/<user_id>
    不需要登录，用于查看其他用户的基本信息
    如果已登录，会根据当前用户身份返回额外信息：
    - 学生查看教师：返回组队成功率
    - 教师查看学生：返回最近一次技能项目的技能评分和技能列表
    
    返回:
    {
        "code": 200,
        "data": {
            "identity": 1,  # 0-学生, 1-教师
            "name": "教师姓名",
            "account": "教工号或学号",
            "grade": 2,  # 仅学生有
            "title": "教授",  # 仅教师有
            "past_achievements": "往期指导成果",  # 仅教师有
            "teacher_success_rate": 85.5,  # 仅学生查看教师时有
            "teacher_total_cooperations": 20,  # 仅学生查看教师时有
            "teacher_approved_cooperations": 17,  # 仅学生查看教师时有
            "skill_score": 85.5,  # 仅教师查看学生时有
            "latest_skills": [  # 仅教师查看学生时有
                {"skill_name": "Python", "skill_degree": "skillful"},
                {"skill_name": "Java", "skill_degree": "known"}
            ]
        }
    }
    """
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response(
            {'code': 404, 'msg': '用户不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # 获取当前用户（如果已登录）
    current_user = get_user_from_token(request)
    current_user_identity = current_user.identity if current_user else None
    
    if user.identity == 0:  # 学生
        try:
            student = StudentEntity.objects.get(user_id=user_id)
            data = {
                'identity': user.identity,
                'name': student.student_name,
                'account': student.student_id,
                'grade': student.grade
            }
            
            # 如果当前用户是教师，添加学生最近一次技能项目的技能评分
            if current_user_identity == 1:
                try:
                    # 获取该学生最近一次发布的技能项目
                    latest_skill_info = SkillInformation.objects.filter(
                        student_id=student.student_id
                    ).select_related('post').order_by('-post__create_time').first()
                    
                    if latest_skill_info:
                        # 获取该项目的技能列表
                        student_skills = StudentSkill.objects.filter(
                            post=latest_skill_info.post
                        ).select_related('skill')
                        
                        # 构建技能列表
                        skills_list = [
                            {
                                'skill_name': ss.skill.skill_name,
                                'skill_degree': 'skillful' if ss.proficiency == 0 else 'known'
                            }
                            for ss in student_skills
                        ]
                        data['latest_skills'] = skills_list
                        
                        # 计算技能评分（需要导入相关函数）
                        from ..views.project import calculate_skill_score
                        score_payload = calculate_skill_score(
                            latest_skill_info.project_experience,
                            student_skills
                        )
                        data['skill_score'] = score_payload['total_score']
                except Exception as e:
                    # 如果获取技能评分失败，不添加该字段
                    pass
            
            return Response({
                'code': 200,
                'data': data
            }, status=status.HTTP_200_OK)
        except StudentEntity.DoesNotExist:
            return Response(
                {'code': 404, 'msg': '学生实体不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:  # 教师
        try:
            teacher = TeacherEntity.objects.get(user_id=user_id)
            data = {
                'identity': user.identity,
                'name': teacher.teacher_name,
                'account': teacher.teacher_id,
                'title': teacher.title,
                'past_achievements': teacher.past_achievements or ''
            }
            
            # 如果当前用户是学生，添加教师的组队成功率
            if current_user_identity == 0:
                from ..views.project import get_teacher_success_stats
                success_stats = get_teacher_success_stats(teacher.teacher_id)
                data.update(success_stats)
            
            return Response({
                'code': 200,
                'data': data
            }, status=status.HTTP_200_OK)
        except TeacherEntity.DoesNotExist:
            return Response(
                {'code': 404, 'msg': '教师实体不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
