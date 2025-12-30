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
from ..models.interaction import Like, Favorite, Comment
from ..serializers import ProjectPublishSerializer
from ..utils.auth import login_required, get_user_from_token


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


@api_view(['GET'])
def list_projects(request):
    """获取项目列表接口
    
    GET /project/list
    查询参数（可选）:
    - post_type: 项目类型筛选 (research/competition/personal)
    
    返回:
    {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {
                "post_id": 1,
                "post_type": "research",  # research/competition/personal
                "title": "项目名称",
                "publisher_name": "发布人姓名",
                "like_num": 10,
                "favorite_num": 5,
                "comment_num": 3,
                "create_time": "2024-01-01T00:00:00Z"
            },
            ...
        ]
    }
    """
    try:
        # 获取筛选参数
        post_type_filter = request.GET.get('post_type', None)
        
        # 类型映射：字符串 -> 整数
        post_type_map = {
            'research': 1,
            'competition': 2,
            'personal': 3
        }
        
        # 构建查询
        posts_query = PostEntity.objects.all().order_by('-create_time')
        
        # 如果有类型筛选，添加过滤条件
        if post_type_filter and post_type_filter in post_type_map:
            posts_query = posts_query.filter(post_type=post_type_map[post_type_filter])
        
        # 获取所有项目
        posts = list(posts_query)
        post_ids = [post.post_id for post in posts]
        
        # 按类型分组，批量查询以优化性能
        post_ids_by_type = {1: [], 2: [], 3: []}
        for post in posts:
            post_ids_by_type[post.post_type].append(post.post_id)
        
        # 批量查询各类项目
        research_dict = {}
        if post_ids_by_type[1]:
            research_list = ResearchProject.objects.filter(
                post_id__in=post_ids_by_type[1]
            ).select_related('teacher', 'post')
            research_dict = {r.post_id: r for r in research_list}
        
        competition_dict = {}
        if post_ids_by_type[2]:
            competition_list = CompetitionProject.objects.filter(
                post_id__in=post_ids_by_type[2]
            ).select_related('teacher', 'post')
            competition_dict = {c.post_id: c for c in competition_list}
        
        skill_dict = {}
        if post_ids_by_type[3]:
            skill_list = SkillInformation.objects.filter(
                post_id__in=post_ids_by_type[3]
            ).select_related('student', 'post')
            skill_dict = {s.post_id: s for s in skill_list}
        
        result = []
        
        for post in posts:
            # 根据项目类型获取项目信息和发布人信息
            post_type_str = None
            title = None
            publisher_name = None
            
            if post.post_type == 1:  # 科研项目
                research = research_dict.get(post.post_id)
                if not research:
                    continue
                post_type_str = 'research'
                title = research.research_name
                publisher_name = research.teacher.teacher_name
            
            elif post.post_type == 2:  # 竞赛项目
                competition = competition_dict.get(post.post_id)
                if not competition:
                    continue
                post_type_str = 'competition'
                title = competition.competition_name
                publisher_name = competition.teacher.teacher_name
            
            elif post.post_type == 3:  # 个人技能
                skill = skill_dict.get(post.post_id)
                if not skill:
                    continue
                post_type_str = 'personal'
                title = skill.major  # 个人技能使用专业方向作为标题
                publisher_name = skill.student.student_name
            
            # 如果无法获取项目信息，跳过
            if not title or not publisher_name:
                continue
            
            result.append({
                'post_id': post.post_id,
                'post_type': post_type_str,
                'title': title,
                'teacher_name': publisher_name,  # 对于个人项目，这里实际是学生姓名
                'like_num': post.like_num,
                'favorite_num': post.favorite_num,
                'comment_num': post.comment_num,
                'create_time': post.create_time.isoformat() if post.create_time else None
            })
        
        return Response(
            {
                'code': 200,
                'msg': '获取成功',
                'data': result
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'获取项目列表失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_project_detail(request, post_id):
    """获取项目详情接口
    
    GET /project/detail/<post_id>
    请求头（可选）:
    Authorization: Bearer <token>  # 如果提供，会返回当前用户的点赞、收藏状态
    
    返回:
    {
        "code": 200,
        "msg": "获取成功",
        "data": {
            "post_id": 1,
            "post_type": "research",  # research/competition/personal
            "like_num": 10,
            "favorite_num": 5,
            "comment_num": 3,
            "is_liked": false,  # 当前用户是否已点赞（需要登录）
            "is_favorited": false,  # 当前用户是否已收藏（需要登录）
            "create_time": "2024-01-01T00:00:00Z",
            # 根据项目类型返回不同的字段
            # 科研项目 (research):
            "research_name": "项目名称",
            "research_direction": "研究方向",
            "tech_stack": "技术栈",
            "recruit_quantity": 5,
            "starttime": "2024-01-01T00:00:00Z",
            "endtime": "2024-12-31T00:00:00Z",
            "outcome": "预期成果",
            "contact": "联系方式",
            "appendix": "附件URL",
            "teacher_name": "教师姓名",
            "teacher_id": 1,
            # 竞赛项目 (competition):
            "competition_name": "竞赛名称",
            "competition_type": "竞赛类型",
            "deadline": "2024-12-31T00:00:00Z",
            "team_require": "团队要求",
            "guide_way": "指导方式",
            "reward": "奖励",
            # 个人技能 (personal):
            "major": "专业",
            "skill": "技能",
            "skill_degree": "技能程度",
            "project_experience": "项目经验",
            "experience_link": "经验链接",
            "habit_tag": "习惯标签",
            "spend_time": "可投入时间",
            "expect_worktype": "期望工作类型",
            "filter": "筛选条件",
            "certification": "证书",
            "student_name": "学生姓名",
            "student_id": 1
        }
    }
    """
    try:
        # 获取项目基础信息
        try:
            post = PostEntity.objects.get(post_id=post_id)
        except PostEntity.DoesNotExist:
            return Response(
                {'code': 404, 'msg': '项目不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取当前用户（如果已登录）
        current_user = get_user_from_token(request)
        
        # 检查用户是否已点赞、收藏
        is_liked = False
        is_favorited = False
        if current_user:
            is_liked = Like.objects.filter(post=post, user=current_user).exists()
            is_favorited = Favorite.objects.filter(post=post, user=current_user).exists()
        
        # 根据项目类型获取详细信息
        result = {
            'post_id': post.post_id,
            'post_type': None,
            'like_num': post.like_num,
            'favorite_num': post.favorite_num,
            'comment_num': post.comment_num,
            'is_liked': is_liked,
            'is_favorited': is_favorited,
            'create_time': post.create_time.isoformat() if post.create_time else None
        }
        
        if post.post_type == 1:  # 科研项目
            try:
                research = ResearchProject.objects.select_related('teacher', 'post').get(post_id=post_id)
                result.update({
                    'post_type': 'research',
                    'research_name': research.research_name,
                    'research_direction': research.research_direction,
                    'tech_stack': research.tech_stack,
                    'recruit_quantity': research.recruit_quantity,
                    'starttime': research.starttime.isoformat() if research.starttime else None,
                    'endtime': research.endtime.isoformat() if research.endtime else None,
                    'outcome': research.outcome,
                    'contact': research.contact,
                    'appendix': research.appendix,
                    'teacher_name': research.teacher.teacher_name,
                    'teacher_id': research.teacher.teacher_id
                })
            except ResearchProject.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '科研项目信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif post.post_type == 2:  # 竞赛项目
            try:
                competition = CompetitionProject.objects.select_related('teacher', 'post').get(post_id=post_id)
                result.update({
                    'post_type': 'competition',
                    'competition_name': competition.competition_name,
                    'competition_type': competition.competition_type,
                    'deadline': competition.deadline.isoformat() if competition.deadline else None,
                    'team_require': competition.team_require,
                    'guide_way': competition.guide_way,
                    'reward': competition.reward,
                    'appendix': competition.appendix,
                    'teacher_name': competition.teacher.teacher_name,
                    'teacher_id': competition.teacher.teacher_id
                })
            except CompetitionProject.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '竞赛项目信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif post.post_type == 3:  # 个人技能
            try:
                skill = SkillInformation.objects.select_related('student', 'post').get(post_id=post_id)
                result.update({
                    'post_type': 'personal',
                    'major': skill.major,
                    'skill': skill.skill,
                    'skill_degree': skill.skill_degree,
                    'project_experience': skill.project_experience,
                    'experience_link': skill.experience_link,
                    'habit_tag': skill.habit_tag,
                    'spend_time': skill.spend_time,
                    'expect_worktype': skill.expect_worktype,
                    'filter': skill.filter,
                    'certification': skill.certification,
                    'student_name': skill.student.student_name,
                    'student_id': skill.student.student_id
                })
            except SkillInformation.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '个人技能信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(
            {
                'code': 200,
                'msg': '获取成功',
                'data': result
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'获取项目详情失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )