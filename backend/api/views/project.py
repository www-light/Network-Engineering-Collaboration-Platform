"""
项目相关视图
"""
import json
import os
import re
import math
from datetime import datetime
from functools import lru_cache

from django.db import transaction, models
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import PostEntity, ResearchProject, CompetitionProject, SkillInformation
from ..models import TeacherEntity, StudentEntity, Tag, PostTag,User
from ..models import Skill, StudentSkill
from ..models import TeacherStudentCooperation
from ..models.attachment import PostAttachment
from ..models.direction import PostDirection, PostStack, TechStack, Direction
from ..models.direction import Direction, PostDirection
from ..models.interaction import Like, Favorite, Comment
from ..serializers import ResearchPublishSerializer, CompetitionPublishSerializer, PersonalPublishSerializer
from ..utils.auth import login_required, get_user_from_token


# 技能评分权重配置
WORD_WEIGHT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'word_weight.txt')
PROFICIENCY_WEIGHT_MAP = {0: 2, 1: 1}  # 0=skillful -> 熟练(2); 1=known -> 了解(1)
ALPHA_WEIGHT = 0.6  # 关键词得分占比
BETA_WEIGHT = 0.4   # 技术熟练度占比


def _strip_json_comments(content: str) -> str:
    """移除简单的 /* ... */ 注释，便于解析为 JSON。"""
    return re.sub(r'/\*.*?\*/', '', content, flags=re.S)


@lru_cache(maxsize=1)
def load_word_weights():
    """读取关键词权重配置，读取失败时返回空列表。"""
    try:
        with open(WORD_WEIGHT_FILE, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        cleaned = _strip_json_comments(raw_content)
        return json.loads(cleaned)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def calculate_keyword_score(project_experience: str) -> float:
    """根据项目经历文本匹配关键词得分。"""
    if not project_experience:
        return 0.0
    text_lower = project_experience.lower()
    score = 0.0
    for item in load_word_weights():
        names = [item.get('name', '')]
        aliases = item.get('aliases') or []
        keywords = [kw for kw in names + aliases if kw]
        for keyword in keywords:
            if keyword.lower() in text_lower:
                score += float(item.get('base_weight', 0))
                break  # 同一组命中一次即可
    return score


def calculate_proficiency_score(skills_data) -> float:
    """根据技能熟练度累加得分。"""
    total = 0.0
    for skill_item in skills_data:
        proficiency = None
        if isinstance(skill_item, dict):
            proficiency = skill_item.get('proficiency')
            if proficiency is None:
                degree_str = (skill_item.get('skill_degree') or '').strip().lower()
                if degree_str == 'skillful':
                    proficiency = 0
                elif degree_str == 'known':
                    proficiency = 1
        else:
            proficiency = getattr(skill_item, 'proficiency', None)
        total += PROFICIENCY_WEIGHT_MAP.get(proficiency, 0)
    return total


def calculate_skill_score(project_experience: str, skills_data) -> dict:
    """综合关键词与熟练度，返回总分及分项。"""
    keyword_score = calculate_keyword_score(project_experience)
    proficiency_score = calculate_proficiency_score(skills_data)
    total_score = keyword_score * ALPHA_WEIGHT + proficiency_score * BETA_WEIGHT
    return {
        'total_score': round(total_score, 2),
        'keyword_score': round(keyword_score, 2),
        'proficiency_score': round(proficiency_score, 2)
    }


# ===================== 可投入时间匹配 =====================
SHORT_PROJECT_HOURS = 10  # ≤4周
MID_PROJECT_HOURS = 8     # 5-12周
LONG_PROJECT_HOURS = 6    # >12周


def parse_hours_per_week(text: str) -> tuple[float, bool]:
    """从文本解析每周投入小时数，返回 (hours, parsed_success)。"""
    if not text:
        return 0.0, False
    t = text.strip().lower()
    # 区间: 10-15h, 10~15h, 10到15小时
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-~到至]\s*(\d+(?:\.\d+)?)[^\d]*(?:h|小时)', t)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        return max((low + high) / 2.0, 0.0), True
    # 单值: 10h, 每周10小时, 8h/week
    single_match = re.search(r'(\d+(?:\.\d+)?)[^\d]*(?:h|小时)', t)
    if single_match:
        val = float(single_match.group(1))
        return max(val, 0.0), True
    return 0.0, False


def calc_project_hours_per_week(start_time, end_time):
    """根据项目起止时间计算周期和每周标准工时。无法计算时返回 None。"""
    if not start_time or not end_time:
        return None, None
    try:
        duration_days = (end_time - start_time).days
        if duration_days <= 0:
            return None, None
        duration_weeks = math.ceil(duration_days / 7)
        if duration_weeks <= 4:
            hours = SHORT_PROJECT_HOURS
        elif duration_weeks <= 12:
            hours = MID_PROJECT_HOURS
        else:
            hours = LONG_PROJECT_HOURS
        return duration_weeks, hours
    except Exception:
        return None, None


def classify_match(student_hours: float, project_hours: float):
    """计算匹配度及分档。失败返回(None, 'unknown', None)。"""
    if project_hours is None or project_hours <= 0 or student_hours is None or student_hours < 0:
        return None, 'unknown', None
    if project_hours == 0:
        return None, 'unknown', None
    ratio = student_hours / project_hours
    return round(ratio, 2)


@api_view(['GET'])
def list_projects(request):
    """获取项目列表接口（支持分页和关键词搜索）
    
    GET /project/list
    查询参数（可选）:
    - post_type: 项目类型筛选 (research/competition/personal)
    - user_id: 用户ID筛选，只返回该用户发布的项目
    - search: 关键词搜索，在多个字段中进行模糊搜索
    - page: 页码，从1开始（默认：1）
    - page_size: 每页数量（默认：20）
    
    搜索范围：competition_name, team_require, reward, post_direction, 
    post_stack, research_name, outcome, project_name, habit_tag, stu_skill
    
    返回:
    {
        "code": 200,
        "msg": "获取成功",
        "data": {
            "items": [
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
            ],
            "total": 100,  # 总记录数
            "page": 1,     # 当前页码
            "page_size": 20,  # 每页数量
            "total_pages": 5  # 总页数
        }
    }
    """
    try:
        # 获取筛选参数
        post_type_filter = request.GET.get('post_type', None)
        user_id_filter = request.GET.get('user_id', None)
        search_keyword = request.GET.get('search', None)
        
        # 获取分页参数
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        
        # 确保分页参数有效
        page = max(1, page)
        page_size = max(1, min(100, page_size))  # 限制每页最多100条
        
        # 类型映射：字符串 -> 整数
        post_type_map = {
            'research': 1,
            'competition': 2,
            'personal': 3
        }
        
        # 获取当前用户（如果已登录）
        current_user = get_user_from_token(request)
        current_user_identity = None
        if current_user:
            current_user_identity = current_user.identity  # 0=学生, 1=教师
        
        # 构建查询
        posts_query = PostEntity.objects.all().order_by('-create_time')
        
        # 根据可见权限过滤
        # visibility: 0=公开（所有人可见）, 1=仅教师可见, 2=仅学生可见
        if current_user_identity is not None:
            # 如果用户已登录，根据身份和可见权限过滤
            if current_user_identity == 0:  # 学生
                # 学生可以看到：公开(0)和仅学生可见(2)的项目
                posts_query = posts_query.filter(visibility__in=[0, 2])
            elif current_user_identity == 1:  # 教师
                # 教师可以看到：公开(0)和仅教师可见(1)的项目
                posts_query = posts_query.filter(visibility__in=[0, 1])
        else:
            # 未登录用户只能看到公开的项目
            posts_query = posts_query.filter(visibility=0)
        
        # 如果有类型筛选，添加过滤条件
        if post_type_filter and post_type_filter in post_type_map:
            posts_query = posts_query.filter(post_type=post_type_map[post_type_filter])
        
        # 如果有用户ID筛选，添加过滤条件
        if user_id_filter:
            try:
                user_id_int = int(user_id_filter)
                # 获取该用户发布的所有项目post_id
                # 对于科研项目和竞赛项目，通过TeacherEntity关联
                # 对于个人技能项目，通过StudentEntity关联
                teacher = TeacherEntity.objects.filter(user_id=user_id_int).first()
                student = StudentEntity.objects.filter(user_id=user_id_int).first()
                
                user_post_ids = []
                
                if teacher:
                    # 获取该教师发布的科研项目和竞赛项目
                    research_posts = ResearchProject.objects.filter(teacher=teacher).values_list('post_id', flat=True)
                    competition_posts = CompetitionProject.objects.filter(teacher=teacher).values_list('post_id', flat=True)
                    user_post_ids.extend(research_posts)
                    user_post_ids.extend(competition_posts)
                
                if student:
                    # 获取该学生发布的个人技能项目
                    skill_posts = SkillInformation.objects.filter(student=student).values_list('post_id', flat=True)
                    user_post_ids.extend(skill_posts)
                
                # 如果用户没有发布任何项目，返回空结果
                if not user_post_ids:
                    return Response(
                        {
                            'code': 200,
                            'msg': '获取成功',
                            'data': {
                                'items': [],
                                'total': 0,
                                'page': page,
                                'page_size': page_size,
                                'total_pages': 0
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                
                # 筛选该用户发布的项目
                posts_query = posts_query.filter(post_id__in=user_post_ids)
            except (ValueError, TypeError):
                # user_id无效，忽略该筛选条件
                pass
        
        # 如果有关键词搜索，进行多字段模糊搜索
        if search_keyword and search_keyword.strip():
            search_term = search_keyword.strip()
            # 构建Q对象进行OR查询，在多个字段中搜索
            search_query = Q()
            
            # 搜索科研项目字段
            search_query |= Q(researchproject__research_name__icontains=search_term)
            search_query |= Q(researchproject__outcome__icontains=search_term)
            
            # 搜索竞赛项目字段
            search_query |= Q(competitionproject__competition_name__icontains=search_term)
            search_query |= Q(competitionproject__team_require__icontains=search_term)
            search_query |= Q(competitionproject__reward__icontains=search_term)
            
            # 搜索个人技能字段
            search_query |= Q(skillinformation__project_experience__icontains=search_term)
            
            # 搜索方向和技术栈字段
            search_query |= Q(postdirection__direction__direction_name__icontains=search_term)
            search_query |= Q(poststack__stack__tech_stack__icontains=search_term)
            
            # 搜索标签字段
            search_query |= Q(posttag__tag__name__icontains=search_term)
            
            # 搜索技能字段
            
            # 应用搜索过滤，并使用distinct去重，因为多个关联可能返回重复的post
            posts_query = posts_query.filter(search_query).distinct()
        
        # 计算总数
        total = posts_query.count()
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        # 分页查询
        offset = (page - 1) * page_size
        posts = list(posts_query[offset:offset + page_size])
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
        
        # 批量查询方向关联（用于个人技能和科研项目）
        post_directions_dict = {}
        post_directions_list = PostDirection.objects.filter(
            post_id__in=post_ids
        ).select_related('direction', 'post')
        for pd in post_directions_list:
            if pd.post_id not in post_directions_dict:
                post_directions_dict[pd.post_id] = []
            post_directions_dict[pd.post_id].append(pd.direction.direction_name)
        
        # 批量查询技术栈关联（用于科研项目，每个post只有一个技术栈字符串）
        post_stacks_dict = {}
        post_stacks_list = PostStack.objects.filter(
            post_id__in=post_ids
        ).select_related('stack', 'post')
        for ps in post_stacks_list:
            # 每个post只保存一个技术栈字符串（如果已有则覆盖，确保唯一）
            post_stacks_dict[ps.post_id] = ps.stack.tech_stack
        
        # 批量查询技能关联（用于个人技能）
        student_skills_dict = {}
        student_skills_list = StudentSkill.objects.filter(
            post_id__in=post_ids
        ).select_related('skill', 'post')
        for ss in student_skills_list:
            if ss.post_id not in student_skills_dict:
                student_skills_dict[ss.post_id] = []
            student_skills_dict[ss.post_id].append({
                'skill_name': ss.skill.skill_name,
                'proficiency': ss.proficiency,  # 0=skillful, 1=known
                'skill_degree': 'skillful' if ss.proficiency == 0 else 'known'
            })
        
        # 批量查询附件
        attachments_dict = {}
        attachments_list = PostAttachment.objects.filter(
            post_id__in=post_ids,
            is_active=True
        ).order_by('-created_at')
        for att in attachments_list:
            if att.post_id not in attachments_dict:
                attachments_dict[att.post_id] = []
            attachments_dict[att.post_id].append({
                'attachment_id': str(att.id),
                'original_filename': att.original_filename,
                'file_size': att.file_size,
                'formatted_size': att.formatted_size,
                'mime_type': att.mime_type,
                'file_type': att.file_type,
                'download_url': att.download_url,
                'created_at': att.created_at.isoformat() if att.created_at else None
            })
        
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
                
                # 获取技术栈（完整字符串）
                tech_stack = post_stacks_dict.get(post.post_id, '')
                
                # 构建项目数据
                project_data = {
                    'post_id': post.post_id,
                    'post_type': post_type_str,
                    'title': title,
                    'teacher_name': publisher_name,
                    'like_num': post.like_num,
                    'favorite_num': post.favorite_num,
                    'comment_num': post.comment_num,
                    'create_time': post.create_time.isoformat() if post.create_time else None,
                    'tech_stack': tech_stack,  # 技术栈字符串
                    'attachments': attachments_dict.get(post.post_id, [])  # 附件列表
                }
            
            elif post.post_type == 2:  # 竞赛项目
                competition = competition_dict.get(post.post_id)
                if not competition:
                    continue
                post_type_str = 'competition'
                title = competition.competition_name
                publisher_name = competition.teacher.teacher_name
                
                # 构建项目数据
                project_data = {
                    'post_id': post.post_id,
                    'post_type': post_type_str,
                    'title': title,
                    'teacher_name': publisher_name,
                    'like_num': post.like_num,
                    'favorite_num': post.favorite_num,
                    'comment_num': post.comment_num,
                    'create_time': post.create_time.isoformat() if post.create_time else None,
                    'attachments': attachments_dict.get(post.post_id, [])  # 附件列表
                }
            
            elif post.post_type == 3:  # 个人技能
                skill = skill_dict.get(post.post_id)
                if not skill:
                    continue
                post_type_str = 'personal'
                # 个人技能使用专业方向作为标题，如果有方向则使用第一个，否则使用学生姓名
                directions = post_directions_dict.get(post.post_id, [])
                title = directions[0] if directions else skill.student.student_name
                publisher_name = skill.student.student_name
                
                # 获取技能列表
                skills = student_skills_dict.get(post.post_id, [])

                # 计算技能评分
                score_payload = calculate_skill_score(skill.project_experience, skills)
                
                # 构建项目数据
                project_data = {
                    'post_id': post.post_id,
                    'post_type': post_type_str,
                    'title': title,
                    'teacher_name': publisher_name,  # 对于个人项目，这里实际是学生姓名
                    'like_num': post.like_num,
                    'favorite_num': post.favorite_num,
                    'comment_num': post.comment_num,
                    'create_time': post.create_time.isoformat() if post.create_time else None,
                    'major': directions,  # 专业方向列表
                    'skills': skills,  # 技能列表（包含技能名和熟练度）
                    'skill_score': score_payload['total_score'],
                    'attachments': attachments_dict.get(post.post_id, [])  # 附件列表
                }
            
            # 如果无法获取项目信息，跳过
            if not title or not publisher_name:
                continue
            
            result.append(project_data)
        
        return Response(
            {
                'code': 200,
                'msg': '获取成功',
                'data': {
                    'items': result,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages
                }
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
            "teacher_user_id": 1,
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
            "student_user_id": 1
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
                
                # 从关联表中获取research_direction和tech_stack
                post_directions = PostDirection.objects.filter(post=post).select_related('direction')
                research_directions = [pd.direction.direction_name for pd in post_directions]
                
                post_stacks = PostStack.objects.filter(post=post).select_related('stack').first()
                # 技术栈完整保存为字符串，每个post只有一个技术栈
                tech_stack = post_stacks.stack.tech_stack if post_stacks else ''
                
                result.update({
                    'post_type': 'research',
                    'research_name': research.research_name,
                    'research_direction': research_directions,  # 改为数组形式
                    'tech_stack': tech_stack,
                    'recruit_quantity': research.recruit_quantity,
                    'starttime': research.starttime.isoformat() if research.starttime else None,
                    'endtime': research.endtime.isoformat() if research.endtime else None,
                    'outcome': research.outcome,
                    'contact': research.contact,
                    'teacher_name': research.teacher.teacher_name,
                    'teacher_user_id': TeacherEntity.objects.get(teacher_id=research.teacher_id).user_id
                })
            except ResearchProject.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '科研项目信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif post.post_type == 2:  # 竞赛项目
            try:
                competition = CompetitionProject.objects.select_related('teacher', 'post').get(post_id=post_id)
                
                # 将 competition_type 整数转换为字符串
                competition_type_map = {0: 'IETP', 1: 'AC', 2: 'CC'}
                competition_type_str = competition_type_map.get(competition.competition_type, 'unknown')
                
                # 将 guide_way 整数转换为字符串
                guide_way_map = {0: 'online', 1: 'offline'}
                guide_way_str = guide_way_map.get(competition.guide_way, 'unknown')
                
                result.update({
                    'post_type': 'competition',
                    'competition_name': competition.competition_name,
                    'competition_type': competition_type_str,
                    'deadline': competition.deadline.isoformat() if competition.deadline else None,
                    'team_require': competition.team_require,
                    'guide_way': guide_way_str,
                    'reward': competition.reward,
                    'teacher_name': competition.teacher.teacher_name,
                    'teacher_user_id': TeacherEntity.objects.get(teacher_id=competition.teacher_id).user_id
                })
            except CompetitionProject.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '竞赛项目信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif post.post_type == 3:  # 个人技能
            try:
                skill = SkillInformation.objects.select_related('student', 'post').get(post_id=post_id)
                
                # 从关联表中获取major（专业方向）
                post_directions = PostDirection.objects.filter(post=post).select_related('direction')
                major_directions = [pd.direction.direction_name for pd in post_directions]
                major = ', '.join(major_directions) if major_directions else ''
                
                # 获取该项目的标签
                post_tags = PostTag.objects.filter(post=post).select_related('tag')
                tags_list = [
                    {'tag_id': pt.tag.tag_id, 'name': pt.tag.name}
                    for pt in post_tags
                ]
                
                # 获取该项目的技能
                student_skills = StudentSkill.objects.filter(post=post).select_related('skill')
                score_payload = calculate_skill_score(skill.project_experience, student_skills)
                skills_list = [
                    {
                        'skill_name': ss.skill.skill_name,
                        'skill_degree': 'skillful' if ss.proficiency == 0 else 'known'
                    }
                    for ss in student_skills
                ]
                
                result.update({
                    'post_type': 'personal',
                    'major': major,
                    'skills': skills_list,
                    'project_experience': skill.project_experience,
                    'experience_link': skill.experience_link,
                    'habit_tag': skill.habit_tag,
                    'spend_time': skill.spend_time,
                    'expect_worktype': skill.expect_worktype,
                    'filter': skill.filter,
                    'student_name': skill.student.student_name,
                    'student_user_id': StudentEntity.objects.get(student_id=skill.student_id).user_id,
                    'tags': tags_list,  # 添加标签列表
                    'skill_score': score_payload['total_score'],
                    'skill_score_detail': {
                        'keyword_score': score_payload['keyword_score'],
                        'proficiency_score': score_payload['proficiency_score'],
                        'alpha': ALPHA_WEIGHT,
                        'beta': BETA_WEIGHT
                    }
                })
            except SkillInformation.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '个人技能信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # 获取项目的附件列表
        attachments = PostAttachment.objects.filter(
            post=post,
            is_active=True
        ).order_by('-created_at')
        
        attachments_list = [
            {
                'attachment_id': str(att.id),
                'original_filename': att.original_filename,
                'file_size': att.file_size,
                'formatted_size': att.formatted_size,
                'mime_type': att.mime_type,
                'file_type': att.file_type,
                'download_url': att.download_url,
                'created_at': att.created_at.isoformat() if att.created_at else None
            }
            for att in attachments
        ]
        
        # 将附件列表添加到结果中
        result['attachments'] = attachments_list
        
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


@api_view(['GET'])
@login_required
def time_match_overview(request):
    """学生-教师项目的可投入时间匹配度概览。

    GET /project/time-match
    查询参数:
    - post_id :学生发布的技能信息的 post_id （必填）

    返回学生与该教师所有科研/竞赛项目的匹配度。
    """
    user = get_user_from_token(request)
    post_id = request.GET.get('post_id', None)
    if not post_id:
        return Response({'code': 400, 'msg': '缺少必要参数 post_id'}, status=status.HTTP_400_BAD_REQUEST)
    # 身份校验：教师只能查看自己的项目
    if user.identity == 0:
        return Response({'code': 403, 'msg': '无权查看时间匹配度'}, status=status.HTTP_403_FORBIDDEN)
    
    # 获取实体
    try:
        teacher = TeacherEntity.objects.get(user_id=user.user_id)
    except TeacherEntity.DoesNotExist:
        return Response({'code': 404, 'msg': '教师不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 学生可投入时间，取最近发布的个人技能记录
    skill_info = SkillInformation.objects.filter(post_id=post_id).select_related('post').order_by('-post__create_time').first()
    student_hours, parsed = parse_hours_per_week(skill_info.spend_time if skill_info else '')
    if not parsed:
        student_hours = None

    projects = []

    # 科研项目
    research_list = ResearchProject.objects.filter(teacher_id=teacher.teacher_id).select_related('post')
    for rp in research_list:
        duration_weeks, project_hours = calc_project_hours_per_week(rp.starttime, rp.endtime)
        match_ratio = classify_match(student_hours, project_hours)
        projects.append({
            'post_id': rp.post_id,
            'title': rp.research_name,
            'project_hours_per_week': project_hours,
            'match_ratio': match_ratio
        })

    return Response(
        {
            'code': 200,
            'msg': 'ok',
            'data': {
                'student_hours_per_week': student_hours,
                'parsed': parsed,
                'projects': projects
            }
        },
        status=status.HTTP_200_OK
    )


def timestamp_to_datetime(timestamp_ms):
    """将Unix时间戳（毫秒）转换为timezone-aware datetime"""
    try:
        # 判断是毫秒还是秒时间戳（毫秒时间戳通常是13位数字，秒时间戳是10位）
        # 如果大于1e12（12位数），认为是毫秒时间戳
        if timestamp_ms > 1e12:
            timestamp_sec = timestamp_ms / 1000.0
        else:
            timestamp_sec = float(timestamp_ms)
        dt = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
    except (ValueError, OSError, TypeError) as e:
        raise ValueError(f'时间戳转换失败: {str(e)}')


def get_or_create_direction(direction_name):
    """获取或创建方向记录
    
    Args:
        direction_name: 方向名称
        
    Returns:
        Direction对象，如果direction_name为空则返回None
    """
    if not direction_name or not direction_name.strip():
        return None
    
    direction_name = direction_name.strip()
    direction, _ = Direction.objects.get_or_create(
        direction_name=direction_name
    )
    return direction


def sync_post_directions(post, direction_names):
    """同步post的方向关联
    
    Args:
        post: PostEntity对象
        direction_names: 方向名称列表（可以是字符串或列表）
    """
    # 如果direction_names是字符串，转换为列表
    if isinstance(direction_names, str):
        # 如果包含斜杠，按斜杠分割；如果包含逗号，按逗号分割；否则作为单个方向
        if '/' in direction_names:
            direction_names = [name.strip() for name in direction_names.split('/') if name.strip()]
        elif ',' in direction_names:
            direction_names = [name.strip() for name in direction_names.split(',') if name.strip()]
        else:
            direction_names = [direction_names.strip()] if direction_names.strip() else []
    
    # 删除该post的所有旧方向关联
    PostDirection.objects.filter(post=post).delete()
    
    # 创建新的方向关联
    for direction_name in direction_names:
        if not direction_name or not direction_name.strip():
            continue
        direction = get_or_create_direction(direction_name)
        if direction:
            PostDirection.objects.get_or_create(
                post=post,
                direction=direction
            )


def get_or_create_tech_stack(stack_name):
    """获取或创建技术栈记录
    
    Args:
        stack_name: 技术栈名称
        
    Returns:
        TechStack对象，如果stack_name为空则返回None
    """
    if not stack_name or not stack_name.strip():
        return None
    
    stack_name = stack_name.strip()
    tech_stack, _ = TechStack.objects.get_or_create(
        tech_stack=stack_name
    )
    return tech_stack


def sync_post_stacks(post, stack_names):
    """同步post的技术栈关联
    
    Args:
        post: PostEntity对象
        stack_names: 技术栈名称字符串（完整保存，不分割，每个post只有一个技术栈）
    """
    # 删除该post的所有旧技术栈关联
    PostStack.objects.filter(post=post).delete()
    
    # 如果stack_names是字符串且不为空，将整个字符串作为一个技术栈保存
    if isinstance(stack_names, str) and stack_names.strip():
        stack_name = stack_names.strip()
        tech_stack = get_or_create_tech_stack(stack_name)
        if tech_stack:
            PostStack.objects.get_or_create(
                post=post,
                stack=tech_stack
            )


def sync_post_skills(post, skills_data):
    """同步post的技能关联
    
    Args:
        post: PostEntity对象
        skills_data: 技能列表，每个技能是字典，包含skill_name和skill_degree
    """
    # 技能程度映射：skillful=0, known=1
    skill_degree_map = {
        'skillful': 0,
        'known': 1
    }
    
    # 删除该post的所有旧技能关联
    StudentSkill.objects.filter(post=post).delete()
    
    # 处理每个技能
    for skill_item in skills_data:
        skill_name = skill_item.get('skill_name', '').strip()
        skill_degree_str = skill_item.get('skill_degree', '').strip()
        
        if not skill_name:
            continue
        
        # 验证skill_degree
        proficiency = skill_degree_map.get(skill_degree_str)
        if proficiency is None:
            continue  # 跳过无效的技能程度
        
        # 获取或创建Skill
        skill, created = Skill.objects.get_or_create(
            skill_name=skill_name,
            defaults={'skill_name': skill_name}
        )
        
        # 创建或更新StudentSkill关联
        student_skill, created = StudentSkill.objects.get_or_create(
            post=post,
            skill=skill,
            defaults={'proficiency': proficiency}
        )
        if not created:
            # 如果已存在，更新熟练度
            student_skill.proficiency = proficiency
            student_skill.save()


@api_view(['POST'])
@login_required
def publish_research(request):
    """发布科研项目接口
    
    POST /publish/research
    请求头:
    Authorization: Bearer <token>
    
    请求体:
    {
        "post_id": 123,  # 可选
        "teacher_id": 123,
        "research_name": "小型目标检测",
        "research_direction": "人工智能",
        "tech_stack": "python",
        "recruit_quantity": 5,
        "starttime": 1735128927575,  # Unix时间戳（毫秒）
        "endtime": 1735128927575,    # Unix时间戳（毫秒）
        "outcome": "copyright",
        "contact": "17833321110"
    }
    
    返回:
    {
        "code": 200,
        "msg": "发布成功",
        "data": {
            "post_id": 1
        }
    }
    """
    user = request.user
    
    # 检查用户是否有未完成的合作流程
    teacher = TeacherEntity.objects.filter(user_id=user.user_id).first()
    student = StudentEntity.objects.filter(user_id=user.user_id).first()
    
    q_objects = models.Q()
    if teacher:
        q_objects |= models.Q(teacher_id=teacher.teacher_id)
    if student:
        q_objects |= models.Q(student_id=student.student_id)
    
    if (teacher or student) and TeacherStudentCooperation.objects.filter(status=2).filter(q_objects).exists():
        return Response(
            {'code': 403, 'msg': '存在未完成的合作流程，请先完成后再发布'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ResearchPublishSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'code': 400, 'msg': '数据验证失败', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    user = request.user
    
    # 验证用户必须是教师
    if user.identity != 1:
        return Response(
            {'code': 403, 'msg': '只有教师可以发布科研项目'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        with transaction.atomic():
            # 获取教师实体
            try:
                teacher = TeacherEntity.objects.get(teacher_id=validated_data['teacher_id'])
            except TeacherEntity.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '教师信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 验证教师ID是否匹配当前用户
            if teacher.user != user:
                return Response(
                    {'code': 403, 'msg': '无权操作其他教师的项目'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 处理post_id：如果提供则更新，否则创建
            post_id = validated_data.get('post_id')
            if post_id:
                try:
                    post = PostEntity.objects.get(post_id=post_id, post_type=1)
                    # 验证post是否属于该教师
                    try:
                        existing_research = ResearchProject.objects.get(post=post)
                        if existing_research.teacher != teacher:
                            return Response(
                                {'code': 403, 'msg': '无权修改其他教师的项目'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                        # 更新现有项目
                        existing_research.research_name = validated_data['research_name']
                        existing_research.recruit_quantity = validated_data['recruit_quantity']
                        existing_research.starttime = timestamp_to_datetime(validated_data['starttime'])
                        existing_research.endtime = timestamp_to_datetime(validated_data['endtime'])
                        existing_research.outcome = validated_data['outcome']
                        existing_research.contact = validated_data['contact']
                        existing_research.save()
                        
                        # 更新可见权限
                        visibility = validated_data.get('visibility', post.visibility)
                        if visibility in [0, 1, 2]:
                            post.visibility = visibility
                            post.save(update_fields=['visibility'])
                        
                        # 处理方向和技术栈关联
                        sync_post_directions(post, validated_data.get('research_direction', ''))
                        sync_post_stacks(post, validated_data.get('tech_stack', ''))
                        
                        return Response(
                            {
                                'code': 200,
                                'msg': '更新成功',
                                'data': {'post_id': post.post_id}
                            },
                            status=status.HTTP_200_OK
                        )
                    except ResearchProject.DoesNotExist:
                        # post存在但不是research类型，创建新的research项目
                        pass
                except PostEntity.DoesNotExist:
                    # post不存在，创建新的
                    pass
            
            # 获取可见权限，默认为0（公开）
            visibility = validated_data.get('visibility', 0)
            if visibility not in [0, 1, 2]:
                visibility = 0  # 如果值无效，默认公开
            
            # 创建新的PostEntity
            post = PostEntity.objects.create(
                post_type=1,  # 科研项目
                create_time=timezone.now(),
                like_num=0,
                favorite_num=0,
                comment_num=0,
                visibility=visibility
            )
            
            # 创建ResearchProject
            ResearchProject.objects.create(
                post=post,
                teacher=teacher,
                research_name=validated_data['research_name'],
                recruit_quantity=validated_data['recruit_quantity'],
                starttime=timestamp_to_datetime(validated_data['starttime']),
                endtime=timestamp_to_datetime(validated_data['endtime']),
                outcome=validated_data['outcome'],
                contact=validated_data['contact']
            )
            
            # 处理方向和技术栈关联
            sync_post_directions(post, validated_data.get('research_direction', ''))
            sync_post_stacks(post, validated_data.get('tech_stack', ''))
            
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
            {'code': 400, 'msg': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'发布失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@login_required
def publish_competition(request):
    """发布竞赛项目接口
    
    POST /publish/competition
    请求头:
    Authorization: Bearer <token>
    
    请求体:
    {
        "post_id": 122,  # 可选
        "teacher_id": 123,
        "competition_type": "IETP",
        "competition_name": "城市车辆碰撞检测",
        "deadline": 1735129477303,  # Unix时间戳（毫秒）
        "team_require": "一名开发和一名算法",
        "guide_way": "online",
        "reward": "500刀",
        "appendix": "https://xxx.xxx.com/uploads/competition/appendix_123/uuid.pdf"
    }
    
    返回:
    {
        "code": 200,
        "msg": "发布成功",
        "data": {
            "post_id": 1
        }
    }
    """
    user = request.user
    
    # 检查用户是否有未完成的合作流程
    teacher = TeacherEntity.objects.filter(user_id=user.user_id).first()
    student = StudentEntity.objects.filter(user_id=user.user_id).first()
    
    q_objects = models.Q()
    if teacher:
        q_objects |= models.Q(teacher_id=teacher.teacher_id)
    if student:
        q_objects |= models.Q(student_id=student.student_id)
    
    if (teacher or student) and TeacherStudentCooperation.objects.filter(status=2).filter(q_objects).exists():
        return Response(
            {'code': 403, 'msg': '存在未完成的合作流程，请先完成后再发布'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = CompetitionPublishSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'code': 400, 'msg': '数据验证失败', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    user = request.user
    
    # 验证用户必须是教师
    if user.identity != 1:
        return Response(
            {'code': 403, 'msg': '只有教师可以发布竞赛项目'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        with transaction.atomic():
            # 获取教师实体
            try:
                teacher = TeacherEntity.objects.get(teacher_id=validated_data['teacher_id'])
            except TeacherEntity.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '教师信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 验证教师ID是否匹配当前用户
            if teacher.user != user:
                return Response(
                    {'code': 403, 'msg': '无权操作其他教师的项目'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 处理 competition_type：将前端字符串转换为后端整数
            competition_type_str = validated_data['competition_type']
            competition_type_map = {
                'IETP': 0,
                'AC': 1,
                'CC': 2
            }
            competition_type_int = competition_type_map.get(competition_type_str)
            if competition_type_int is None:
                return Response(
                    {'code': 400, 'msg': f'competition_type 值无效: {competition_type_str}，应为 IETP、AC 或 CC'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 处理 guide_way：将前端字符串转换为后端整数
            guide_way_str = validated_data['guide_way']
            guide_way_map = {
                'online': 0,
                'offline': 1
            }
            guide_way_int = guide_way_map.get(guide_way_str)
            if guide_way_int is None:
                return Response(
                    {'code': 400, 'msg': f'guide_way 值无效: {guide_way_str}，应为 online 或 offline'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 处理post_id：如果提供则更新，否则创建
            post_id = validated_data.get('post_id')
            if post_id:
                try:
                    post = PostEntity.objects.get(post_id=post_id, post_type=2)
                    # 验证post是否属于该教师
                    try:
                        existing_competition = CompetitionProject.objects.get(post=post)
                        if existing_competition.teacher != teacher:
                            return Response(
                                {'code': 403, 'msg': '无权修改其他教师的项目'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                        # 更新现有项目
                        existing_competition.competition_type = competition_type_int
                        existing_competition.competition_name = validated_data['competition_name']
                        existing_competition.deadline = timestamp_to_datetime(validated_data['deadline'])
                        existing_competition.team_require = validated_data['team_require']
                        existing_competition.guide_way = guide_way_int
                        existing_competition.reward = validated_data.get('reward') or None
                        existing_competition.save()
                        
                        # 更新可见权限
                        visibility = validated_data.get('visibility', post.visibility)
                        if visibility in [0, 1, 2]:
                            post.visibility = visibility
                            post.save(update_fields=['visibility'])
                        
                        return Response(
                            {
                                'code': 200,
                                'msg': '更新成功',
                                'data': {'post_id': post.post_id}
                            },
                            status=status.HTTP_200_OK
                        )
                    except CompetitionProject.DoesNotExist:
                        # post存在但不是competition类型，创建新的competition项目
                        pass
                except PostEntity.DoesNotExist:
                    # post不存在，创建新的
                    pass
            
            # 获取可见权限，默认为0（公开）
            visibility = validated_data.get('visibility', 0)
            if visibility not in [0, 1, 2]:
                visibility = 0  # 如果值无效，默认公开
            
            # 创建新的PostEntity
            post = PostEntity.objects.create(
                post_type=2,  # 竞赛项目
                create_time=timezone.now(),
                like_num=0,
                favorite_num=0,
                comment_num=0,
                visibility=visibility
            )
            
            # 创建CompetitionProject
            CompetitionProject.objects.create(
                post=post,
                teacher=teacher,
                competition_type=competition_type_int,
                competition_name=validated_data['competition_name'],
                deadline=timestamp_to_datetime(validated_data['deadline']),
                team_require=validated_data['team_require'],
                guide_way=guide_way_int,
                reward=validated_data.get('reward') or None
            )
            
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
            {'code': 400, 'msg': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'发布失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@login_required
def publish_personal(request):
    """发布个人技能接口
    
    POST /publish/personal
    请求头:
    Authorization: Bearer <token>
    
    请求体:
    {
        "post_id": 124,  # 可选
        "student_id": 124,
        "major": "网络工程",
        "skills": [
            {
                "skill_name": "C/C++",
                "skill_degree": "skillful"
            },
            {
                "skill_name": "Python",
                "skill_degree": "known"
            }
        ],
        "project_experience": "能独立开发驱动",
        "experience_file": "https://xxx.xxx.com/uploads/student/student_123/experience/uuid.pdf",
        "habit_tag": "人工智能",
        "spend_time": "每周168h",
        "expect_worktype": "research",
        "filter": "all",
        "certification": "https://xxx.xxx.com/uploads/student/student_123/certification/uuid.pdf"
    }
    
    返回:
    {
        "code": 200,
        "msg": "发布成功",
        "data": {
            "post_id": 1
        }
    }
    """
    user = request.user
    
    # 检查用户是否有未完成的合作流程
    teacher = TeacherEntity.objects.filter(user_id=user.user_id).first()
    student = StudentEntity.objects.filter(user_id=user.user_id).first()
    
    q_objects = models.Q()
    if teacher:
        q_objects |= models.Q(teacher_id=teacher.teacher_id)
    if student:
        q_objects |= models.Q(student_id=student.student_id)
    
    if (teacher or student) and TeacherStudentCooperation.objects.filter(status=2).filter(q_objects).exists():
        return Response(
            {'code': 403, 'msg': '存在未完成的合作流程，请先完成后再发布'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = PersonalPublishSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'code': 400, 'msg': '数据验证失败', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    user = request.user
    
    # 验证用户必须是学生
    if user.identity != 0:
        return Response(
            {'code': 403, 'msg': '只有学生可以发布个人技能'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        with transaction.atomic():
            # 获取学生实体
            try:
                student = StudentEntity.objects.get(student_id=validated_data['student_id'])
            except StudentEntity.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '学生信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 验证学生ID是否匹配当前用户
            if student.user != user:
                return Response(
                    {'code': 403, 'msg': '无权操作其他学生的项目'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 验证技能数组
            skills_data = validated_data.get('skills', [])
            if not skills_data or not isinstance(skills_data, list):
                return Response(
                    {'code': 400, 'msg': '技能列表不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 验证每个技能的数据格式
            for skill_item in skills_data:
                if not isinstance(skill_item, dict):
                    return Response(
                        {'code': 400, 'msg': '技能数据格式错误'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                skill_name = skill_item.get('skill_name', '').strip()
                skill_degree = skill_item.get('skill_degree', '').strip()
                if not skill_name:
                    return Response(
                        {'code': 400, 'msg': '技能名称不能为空'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if skill_degree not in ['skillful', 'known']:
                    return Response(
                        {'code': 400, 'msg': f'技能程度值无效: {skill_degree}，应为 skillful 或 known'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 处理 expect_worktype：验证字符串值
            expect_worktype_str = validated_data['expect_worktype']
            valid_expect_worktypes = ['research', 'competition', 'innovation']
            if expect_worktype_str not in valid_expect_worktypes:
                return Response(
                    {'code': 400, 'msg': f'expect_worktype 值无效: {expect_worktype_str}，应为 research、competition 或 innovation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 处理 filter：验证字符串值
            filter_str = validated_data['filter']
            valid_filters = ['all', 'cross', 'local']
            if filter_str not in valid_filters:
                return Response(
                    {'code': 400, 'msg': f'filter 值无效: {filter_str}，应为 all、cross 或 local'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 处理 habit_tag：前端发送的是字符串，需要转换为逗号分隔的字符串
            habit_tag_str = validated_data.get('habit_tag', '') or ''
            
            # 处理post_id：如果提供则更新，否则创建
            post_id = validated_data.get('post_id')
            if post_id:
                try:
                    post = PostEntity.objects.get(post_id=post_id, post_type=3)
                    # 验证post是否属于该学生
                    try:
                        existing_skill = SkillInformation.objects.get(post=post)
                        if existing_skill.student != student:
                            return Response(
                                {'code': 403, 'msg': '无权修改其他学生的项目'},
                                status=status.HTTP_403_FORBIDDEN
                            )
                        # 更新现有项目
                        existing_skill.project_experience = validated_data.get('project_experience', '')
                        existing_skill.experience_link = validated_data.get('experience_link') or None
                        existing_skill.habit_tag = habit_tag_str
                        existing_skill.spend_time = validated_data['spend_time']
                        existing_skill.expect_worktype = expect_worktype_str
                        existing_skill.filter = filter_str
                        existing_skill.save()
                        
                        # 更新可见权限
                        visibility = validated_data.get('visibility', post.visibility)
                        if visibility in [0, 1, 2]:
                            post.visibility = visibility
                            post.save(update_fields=['visibility'])
                        
                        # 处理方向关联
                        sync_post_directions(post, validated_data.get('major', ''))
                        
                        # 处理技能关联
                        sync_post_skills(post, skills_data)
                        
                        return Response(
                            {
                                'code': 200,
                                'msg': '更新成功',
                                'data': {'post_id': post.post_id}
                            },
                            status=status.HTTP_200_OK
                        )
                    except SkillInformation.DoesNotExist:
                        # post存在但不是personal类型，创建新的personal项目
                        pass
                except PostEntity.DoesNotExist:
                    # post不存在，创建新的
                    pass
            
            # 获取可见权限，默认为0（公开）
            visibility = validated_data.get('visibility', 0)
            if visibility not in [0, 1, 2]:
                visibility = 0  # 如果值无效，默认公开
            
            # 创建新的PostEntity
            post = PostEntity.objects.create(
                post_type=3,  # 个人技能
                create_time=timezone.now(),
                like_num=0,
                favorite_num=0,
                comment_num=0,
                visibility=visibility
            )
            
            # 创建SkillInformation
            SkillInformation.objects.create(
                post=post,
                student=student,
                project_experience=validated_data.get('project_experience', ''),
                experience_link=validated_data.get('experience_link') or None,
                habit_tag=habit_tag_str,
                spend_time=validated_data['spend_time'],
                expect_worktype=expect_worktype_str,
                filter=filter_str
            )
            
            # 处理方向关联
            sync_post_directions(post, validated_data.get('major', ''))
            
            # 处理技能关联
            sync_post_skills(post, skills_data)
            
            return Response(
                {
                    'code': 200,
                    'msg': '发布成功',
                    'data': {'post_id': post.post_id}
                },
                status=status.HTTP_200_OK
            )
    
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'发布失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )