"""
项目相关视图
"""
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import PostEntity, ResearchProject, CompetitionProject, SkillInformation
from ..models import TeacherEntity, StudentEntity, Tag, PostTag
from ..serializers import ProjectPublishSerializer
from ..utils.auth import login_required


@api_view(['POST'])
@login_required
def publish_project(request):
    """发布项目接口
    
    POST /project/publish
    请求头:
    Authorization: Bearer <token>
    
    请求参数根据 post_type 不同而不同:
    - research: 科研项目
    - competition: 竞赛项目
    - personal: 个人技能
    
    返回:
    {
        "code": 200,
        "msg": "发布成功",
        "data": {
            "post_id": 1
        }
    }
    """
    serializer = ProjectPublishSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'code': 400, 'msg': '数据验证失败', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    post_type_str = validated_data['post_type']
    user = request.user
    
    # 映射前端字符串类型到后端整数类型
    post_type_map = {
        'research': 1,      # 科研项目
        'competition': 2,   # 竞赛项目
        'personal': 3       # 学生技能
    }
    post_type = post_type_map[post_type_str]
    
    try:
        with transaction.atomic():
            # 创建 PostEntity
            post = PostEntity.objects.create(
                post_type=post_type,
                create_time=timezone.now(),
                like_num=0,
                favorite_num=0,
                comment_num=0,
                visibility=0  # 默认公开
            )
            
            # 根据项目类型创建对应的项目记录
            if post_type_str == 'research':
                # 验证用户必须是教师
                if user.identity != 1:
                    return Response(
                        {'code': 403, 'msg': '只有教师可以发布科研项目'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                try:
                    teacher = TeacherEntity.objects.get(user=user)
                except TeacherEntity.DoesNotExist:
                    return Response(
                        {'code': 404, 'msg': '教师信息不存在'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # 解析日期时间（转换为 timezone-aware datetime）
                starttime = timezone.make_aware(
                    datetime.strptime(validated_data['starttime'], '%Y-%m-%d')
                )
                endtime = timezone.make_aware(
                    datetime.strptime(validated_data['endtime'], '%Y-%m-%d')
                )
                
                ResearchProject.objects.create(
                    post=post,
                    teacher=teacher,
                    research_name=validated_data['research_name'],
                    research_direction=validated_data['research_direction'],
                    tech_stack=validated_data['tech_stack'],
                    recruit_quantity=validated_data['recruit_quantity'],
                    starttime=starttime,
                    endtime=endtime,
                    outcome=validated_data['outcome'],
                    contact=validated_data['contact'],
                    appendix=validated_data.get('appendix', '') or None
                )
            
            elif post_type_str == 'competition':
                # 验证用户必须是教师
                if user.identity != 1:
                    return Response(
                        {'code': 403, 'msg': '只有教师可以发布竞赛项目'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                try:
                    teacher = TeacherEntity.objects.get(user=user)
                except TeacherEntity.DoesNotExist:
                    return Response(
                        {'code': 404, 'msg': '教师信息不存在'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # 解析日期时间（转换为 timezone-aware datetime）
                deadline = timezone.make_aware(
                    datetime.strptime(validated_data['deadline'], '%Y-%m-%d')
                )
                
                CompetitionProject.objects.create(
                    post=post,
                    teacher=teacher,
                    competition_type=validated_data['competition_type'],
                    competition_name=validated_data['competition_name'],
                    deadline=deadline,
                    team_require=validated_data['team_require'],
                    guide_way=validated_data['guide_way'],
                    reward=validated_data.get('reward', '') or None,
                    appendix=validated_data.get('appendix', '') or None
                )
            
            elif post_type_str == 'personal':
                # 验证用户必须是学生
                if user.identity != 0:
                    return Response(
                        {'code': 403, 'msg': '只有学生可以发布个人技能'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                try:
                    student = StudentEntity.objects.get(user=user)
                except StudentEntity.DoesNotExist:
                    return Response(
                        {'code': 404, 'msg': '学生信息不存在'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # 处理标签：将标签ID列表转换为逗号分隔的字符串
                habit_tag_ids = validated_data.get('habit_tag', [])
                habit_tag_str = ','.join(map(str, habit_tag_ids)) if habit_tag_ids else ''
                
                SkillInformation.objects.create(
                    post=post,
                    student=student,
                    major=validated_data['major'],
                    skill=validated_data['skill'],
                    skill_degree=validated_data['skill_degree'],
                    project_experience=validated_data.get('project_experience', ''),
                    experience_link=validated_data.get('experience_link', '') or None,
                    habit_tag=habit_tag_str,
                    spend_time=validated_data['spend_time'],
                    expect_worktype=validated_data['expect_worktype'],
                    filter=validated_data['filter'],
                    certification=validated_data.get('appendix', '') or None
                )
                
                # 创建 PostTag 关联
                for tag_id in habit_tag_ids:
                    try:
                        tag = Tag.objects.get(tag_id=tag_id)
                        PostTag.objects.get_or_create(post=post, tag=tag)
                    except Tag.DoesNotExist:
                        # 如果标签不存在，跳过
                        continue
            
            return Response(
                {
                    'code': 200,
                    'msg': '发布成功',
                    'data': {'post_id': post.post_id}
                },
                status=status.HTTP_200_OK
            )
    
    except ValueError as e:
        return Response(
            {'code': 400, 'msg': f'日期格式错误: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'发布失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

