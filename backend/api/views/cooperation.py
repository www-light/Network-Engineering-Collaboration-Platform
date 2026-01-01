from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models
from api.models import TeacherStudentCooperation as Cooperation, User, PostEntity
from api.models.project import ResearchProject, CompetitionProject, SkillInformation
from api.models.user import TeacherEntity, StudentEntity
from api.utils.auth import login_required, teacher_required, student_required,get_user_from_token

def get_post_author_id(post):
    """获取post的作者ID
    
    Args:
        post: PostEntity对象
    
    Returns:
        author_id (int) 或 None
    """
    post_type = post.post_type
    
    if post_type == 1:  # 科研项目
        try:
            research = ResearchProject.objects.get(post_id=post.post_id)
            return research.teacher_id
        except ResearchProject.DoesNotExist:
            return None
    elif post_type == 2:  # 竞赛项目
        try:
            competition = CompetitionProject.objects.get(post_id=post.post_id)
            return competition.teacher_id
        except CompetitionProject.DoesNotExist:
            return None
    elif post_type == 3:  # 学生技能
        try:
            skill = SkillInformation.objects.get(post_id=post.post_id)
            return skill.student_id
        except SkillInformation.DoesNotExist:
            return None
    
    return None
def cancel_cooperation(request):
    try:
        cooperation_id = request.data.get('cooperation_id')
        
        if not cooperation_id:
            return Response(
                {"error": "缺少 cooperation_id 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取合作记录
        try:
            cooperation = Cooperation.objects.get(cooperation_id=cooperation_id)
        except Cooperation.DoesNotExist:
            return Response(
                {"error": "合作记录不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        if cooperation.role==1:  # 申请
        # 检查权限（必须是记录的学生）
            if cooperation.student_id != StudentEntity.objects.get(user_id=get_user_from_token(request)).student_id:
                return Response(
                    {"error": "您没有权限取消此申请"},
                    status=status.HTTP_403_FORBIDDEN
                )
            if cooperation.status != 2:
                return Response(
                    {"error": "只能取消待处理的申请"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif cooperation.role==0:  # 邀请
            if cooperation.teacher_id != TeacherEntity.objects.get(user_id=get_user_from_token(request)).teacher_id:
                return Response(
                    {"error": "您没有权限取消此邀请"},
                    status=status.HTTP_403_FORBIDDEN
                )
            if cooperation.status != 2:
                return Response(
                    {"error": "只能取消待处理的邀请"},
                    status=status.HTTP_400_BAD_REQUEST
                )      
        # 更新状态
        cooperation.status = 5
        cooperation.updated_at = timezone.now()
        cooperation.save()
        return Response(
            {
                "message": "取消成功",
                "cooperation_id": cooperation.cooperation_id,
                "status": cooperation.status
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
def reject_cooperation(request):
    try:
        cooperation_id = request.data.get('cooperation_id')
        
        if not cooperation_id:
            return Response(
                {"error": "缺少 cooperation_id 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取合作记录
        try:
            cooperation = Cooperation.objects.get(cooperation_id=cooperation_id)
        except Cooperation.DoesNotExist:
            return Response(
                {"error": "合作记录不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        if cooperation.role==1:  # 申请
            # 检查权限（必须是记录的教师）
            if cooperation.teacher_id != TeacherEntity.objects.get(user_id=get_user_from_token(request)).teacher_id:
                return Response(
                    {"error": "您没有权限拒绝此申请"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 检查状态（只能拒绝待处理的申请）
            if cooperation.status != 2:
                return Response(
                    {"error": "只能拒绝待处理的申请/邀请"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif cooperation.role==0:  # 邀请
            # 检查权限（必须是被邀请者）
            if cooperation.student_id != StudentEntity.objects.get(user_id=get_user_from_token(request)).student_id:
                return Response(
                    {"error": "您没有权限拒绝此邀请"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 检查状态（只能拒绝待处理的邀请）
            if cooperation.status != 2:
                return Response(
                    {"error": "只能拒绝待处理的申请/邀请"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 更新状态
        cooperation.status = 4
        cooperation.updated_at = timezone.now()
        cooperation.save()
        
        return Response(
            {
                "message": "拒绝成功",
                "cooperation_id": cooperation.cooperation_id,
                "status": cooperation.status
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['POST'])
@login_required
@student_required
def apply_cooperation(request):
    """
    学生申请加入项目
    
    Request:
        {
            "post_id": int
        }
    
    Response (201):
        {
            "message": "申请成功",
            "cooperation_id": int,
            "status": 2
        }
    """
    try:
        post_id = request.data.get('post_id')
        
        if not post_id:
            return Response(
                {"error": "缺少 post_id 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查项目是否存在
        try:
            post = PostEntity.objects.get(post_id=post_id)
        except PostEntity.DoesNotExist:
            return Response(
                {"error": "项目不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取post的作者ID
        author_id = get_post_author_id(post)
        if not author_id:
            return Response(
                {"error": "项目作者信息不完整"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 检查是否已经申请过
        existing = Cooperation.objects.filter(
            student_id=StudentEntity.objects.get(user_id=request.user.user_id).student_id,
            post_id=post_id,
            role=1,
            status=2
        ).first()
        
        if existing:
            return Response(
                {"error": "已经申请过此项目，请勿重复申请"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建合作记录
        cooperation = Cooperation.objects.create(
            teacher_id=author_id,
            student_id=StudentEntity.objects.get(user_id=request.user.user_id).student_id,
            post_id=post_id,
            role=1,
            status=2,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        return Response(
            {
                "message": "申请成功",
                "cooperation_id": cooperation.cooperation_id,
                "status": cooperation.status
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@login_required
@teacher_required
def approve_application(request):
    """
    教师批准学生申请
    
    Request:
        {
            "cooperation_id": int
        }
    
    Response (200):
        {
            "message": "批准成功",
            "cooperation_id": int,
            "status": 2
        }
    """
    try:
        cooperation_id = request.data.get('cooperation_id')
        
        if not cooperation_id:
            return Response(
                {"error": "缺少 cooperation_id 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取合作记录
        try:
            cooperation = Cooperation.objects.get(cooperation_id=cooperation_id)
        except Cooperation.DoesNotExist:
            return Response(
                {"error": "合作记录不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限（必须是记录的教师）
        if cooperation.teacher_id != TeacherEntity.objects.get(user_id=request.user.user_id).teacher_id:
            return Response(
                {"error": "您没有权限批准此申请"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查状态（只能批准待处理的申请）
        if cooperation.status != 2:
            return Response(
                {"error": "只能批准待处理的申请"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新状态
        cooperation.status = 3
        cooperation.updated_at = timezone.now()
        cooperation.confirmed_at = timezone.now()
        cooperation.save()
        
        return Response(
            {
                "message": "批准成功",
                "cooperation_id": cooperation.cooperation_id,
                "status": cooperation.status
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@login_required
@teacher_required
def reject_application(request):
    """
    教师拒绝学生申请
    
    Request:
        {
            "cooperation_id": int
        }
    
    Response (200):
        {
            "message": "拒绝成功",
            "cooperation_id": int,
            "status": 4
        }
    """
    return reject_cooperation(request)


@api_view(['POST'])
@login_required
@student_required
def reject_invitation(request):
    """
    学生拒绝教师邀请
    
    Request:
        {
            "cooperation_id": int
        }
    
    Response (200):
        {
            "message": "拒绝成功",
            "cooperation_id": int,
            "status": 4
        }
    """
    return reject_cooperation(request)

@api_view(['POST'])
@login_required
@student_required
def cancel_apply(request):
    """
    学生取消申请或邀请接受前的操作
    
    Request:
        {
            "cooperation_id": int
        }
    
    Response (200):
        {
            "message": "取消成功",
            "cooperation_id": int,
            "status": 3
        }
    """
    return cancel_cooperation(request)


@api_view(['POST'])
@login_required
@teacher_required
def invite_student(request):
    """
    教师邀请学生加入项目
    
    Request:
        {
            "post_id": int,
        }
    
    Response (201):
        {
            "message": "邀请成功",
            "cooperation_id": int,
            "status": 2
        }
    """
    try:
        post_id = request.data.get('post_id')
        student_id = SkillInformation.objects.get(post_id=post_id).student_id
        teacher_id=TeacherEntity.objects.get(user_id=get_user_from_token(request)).teacher_id
        if not post_id:
            return Response(
                {"error": "缺少 post_id 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查项目是否存在
        try:
            post = PostEntity.objects.get(post_id=post_id)
        except PostEntity.DoesNotExist:
            return Response(
                {"error": "项目不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取post的作者ID
        author_id = get_post_author_id(post)
        if not author_id:
            return Response(
                {"error": "项目作者信息不完整"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )       
        
        # 检查学生是否存在
        try:
            student = User.objects.get(user_id=StudentEntity.objects.get(student_id=student_id).user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "学生不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查是否已经邀请过
        existing = Cooperation.objects.filter(
            teacher_id=teacher_id,
            student_id=student_id,
            post_id=post_id,
            role=0,
            status=2
        ).first()
        
        if existing:
            return Response(
                {"error": "已经邀请过此学生，请勿重复邀请"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建邀请记录
        cooperation = Cooperation.objects.create(
            teacher_id=teacher_id,
            student_id=student_id,
            post_id=post_id,
            role=0,
            status=2,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        return Response(
            {
                "message": "邀请成功",
                "cooperation_id": cooperation.cooperation_id,
                "status": cooperation.status
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@login_required
@teacher_required
def cancel_invite(request):
    """
    教师取消邀请
    
    Request:
        {
            "cooperation_id": int
        }
    
    Response (200):
        {
            "message": "取消邀请成功",
            "cooperation_id": int,
            "status": 3
        }
    """
    return cancel_cooperation(request)


@api_view(['POST'])
@login_required
@student_required
def agree_invite(request):
    """
    学生同意邀请
    
    Request:
        {
            "cooperation_id": int
        }
    
    Response (200):
        {
            "message": "同意成功",
            "cooperation_id": int,
            "status": 4
        }
    """
    try:
        cooperation_id = request.data.get('cooperation_id')
        if not cooperation_id:
            return Response(
                {"error": "缺少 cooperation_id 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取邀请记录
        try:
            cooperation = Cooperation.objects.get(cooperation_id=cooperation_id)
        except Cooperation.DoesNotExist:
            return Response(
                {"error": "邀请记录不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限（必须是被邀请者）
        if cooperation.student_id != StudentEntity.objects.get(user_id=get_user_from_token(request)).student_id:
            return Response(
                {"error": "您没有权限同意此邀请"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查是否是邀请（role=True）
        if not cooperation.role:
            return Response(
                {"error": "此记录不是邀请"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查状态（只能接受待处理的邀请）
        if cooperation.status != 2:
            return Response(
                {"error": "只能接受待处理的邀请"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新状态
        cooperation.status = 3
        cooperation.updated_at = timezone.now()
        cooperation.confirmed_at = timezone.now()
        cooperation.save()
        
        return Response(
            {
                "message": "同意成功",
                "cooperation_id": cooperation.cooperation_id,
                "status": cooperation.status
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@login_required
def check_unfinished(request):
    """
    检查用户是否有未完成的合作（待处理状态）
    
    Response (200):
        {
            "has_unfinished": boolean
        }
    """
    try:
        # 查询当前用户是否有待处理的合作(0=邀请, 1=申请, 2=待确认)

        user_id = get_user_from_token(request)
        
        teacher = TeacherEntity.objects.filter(user_id=user_id).first()
        student = StudentEntity.objects.filter(user_id=user_id).first()

        # 构建动态查询条件
        q_objects = models.Q()
        if teacher:
            q_objects |= models.Q(teacher_id=teacher.teacher_id)
        if student:
            q_objects |= models.Q(student_id=student.student_id)

        # 执行查询
        if teacher or student:
            unfinished = Cooperation.objects.filter(status=2).filter(q_objects).exists()
        else:
            unfinished = False
        
        return Response(
            {"has_unfinished": unfinished},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
