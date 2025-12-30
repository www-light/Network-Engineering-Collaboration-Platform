from django.db import transaction, models
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models.post import PostEntity
from ..models.user import User, StudentEntity, TeacherEntity
from ..models.interaction import Like, Favorite, Comment
from ..utils.auth import login_required

def ok():
    return Response({"code": 200}, status=status.HTTP_200_OK)


@api_view(["POST"])
@login_required
def like(request):
    post_id = request.data.get("post_id")
    user = request.user  # 从装饰器获取当前用户

    if post_id is None:
        return Response({"code": 400, "msg": "post_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        like_obj, created = Like.objects.get_or_create(
            post=post,
            user=user,
            defaults={'created_at': timezone.now()}
        )
        if created:
            # 仅首次点赞时累计
            PostEntity.objects.filter(post_id=post.post_id).update(like_num=models.F("like_num") + 1)

    return Response({"code": 200, "msg": "点赞成功", "data": {"is_liked": True}}, status=status.HTTP_200_OK)


@api_view(["POST"])
@login_required
def unlike(request):
    """取消点赞接口"""
    post_id = request.data.get("post_id")
    user = request.user

    if post_id is None:
        return Response({"code": 400, "msg": "post_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        deleted = Like.objects.filter(post=post, user=user).delete()[0]
        if deleted > 0:
            # 减少点赞数
            PostEntity.objects.filter(post_id=post.post_id).update(like_num=models.F("like_num") - 1)

    return Response({"code": 200, "msg": "取消点赞成功", "data": {"is_liked": False}}, status=status.HTTP_200_OK)


@api_view(["POST"])
@login_required
def favorite(request):
    post_id = request.data.get("post_id")
    user = request.user  # 从装饰器获取当前用户

    if post_id is None:
        return Response({"code": 400, "msg": "post_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        favorite_obj, created = Favorite.objects.get_or_create(
            post=post,
            user=user,
            defaults={'created_at': timezone.now()}
        )
        if created:
            PostEntity.objects.filter(post_id=post.post_id).update(favorite_num=models.F("favorite_num") + 1)

    return Response({"code": 200, "msg": "收藏成功", "data": {"is_favorited": True}}, status=status.HTTP_200_OK)


@api_view(["POST"])
@login_required
def unfavorite(request):
    """取消收藏接口"""
    post_id = request.data.get("post_id")
    user = request.user

    if post_id is None:
        return Response({"code": 400, "msg": "post_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        deleted = Favorite.objects.filter(post=post, user=user).delete()[0]
        if deleted > 0:
            # 减少收藏数
            PostEntity.objects.filter(post_id=post.post_id).update(favorite_num=models.F("favorite_num") - 1)

    return Response({"code": 200, "msg": "取消收藏成功", "data": {"is_favorited": False}}, status=status.HTTP_200_OK)


@api_view(["POST"])
@login_required
def comment(request):
    post_id = request.data.get("post_id")
    comment_text = request.data.get("comment")
    user = request.user  # 从装饰器获取当前用户

    if post_id is None or not comment_text:
        return Response({"code": 400, "msg": "post_id、comment 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    with transaction.atomic():
        # 创建新评论（允许多条评论）
        Comment.objects.create(
            post=post,
            user=user,
            comment_content=comment_text,
            created_at=now
        )
        # 更新评论数
        PostEntity.objects.filter(post_id=post.post_id).update(comment_num=models.F("comment_num") + 1)

    return Response({"code": 200, "msg": "评论成功"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def list_comments(request, post_id):
    """获取评论列表接口
    
    GET /post/comment/<post_id>
    
    返回:
    {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {
                "user_id": 1,
                "user_name": "用户名",
                "comment_content": "评论内容",
                "created_at": "2024-01-01T00:00:00Z"
            },
            ...
        ]
    }
    """
    try:
        post = PostEntity.objects.get(post_id=post_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    comments = Comment.objects.filter(post=post).select_related('user').order_by('-created_at')
    
    result = []
    for comment_obj in comments:
        # 获取用户名称
        user_name = "未知用户"
        try:
            if comment_obj.user.identity == 0:  # 学生
                student = StudentEntity.objects.get(user=comment_obj.user)
                user_name = student.student_name
            elif comment_obj.user.identity == 1:  # 教师
                teacher = TeacherEntity.objects.get(user=comment_obj.user)
                user_name = teacher.teacher_name
        except Exception:
            pass
        
        result.append({
            'comment_id': comment_obj.id,  # 使用id作为comment_id
            'user_id': comment_obj.user.user_id,
            'user_name': user_name,
            'comment_content': comment_obj.comment_content,
            'created_at': comment_obj.created_at.isoformat() if comment_obj.created_at else None
        })
    
    return Response({
        "code": 200,
        "msg": "获取成功",
        "data": result
    }, status=status.HTTP_200_OK)
