from django.db import transaction, models
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models.post import PostEntity
from ..models.user import User
from ..models.interaction import Like, Favorite, Comment
from ..utils.auth import login_required, teacher_required, student_required

def ok():
    return Response({"code": 200}, status=status.HTTP_200_OK)


@api_view(["POST"])
@login_required
def like(request):
    post_id = request.data.get("post_id")
    user_id = request.data.get("user_id")

    if post_id is None or user_id is None:
        return Response({"code": 400, "msg": "post_id 和 user_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
        user = User.objects.get(user_id=user_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"code": 404, "msg": "user 不存在"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        created = False
        if not Like.objects.filter(post=post, user=user).exists():
            Like.objects.create(post=post, user=user, created_at=timezone.now())
            # 仅首次点赞时累计
            PostEntity.objects.filter(post_id=post.post_id).update(like_num=models.F("like_num") + 1)
            created = True

    return ok()


@api_view(["POST"])
@login_required
def favorite(request):
    post_id = request.data.get("post_id")
    user_id = request.data.get("user_id")

    if post_id is None or user_id is None:
        return Response({"code": 400, "msg": "post_id 和 user_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
        user = User.objects.get(user_id=user_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"code": 404, "msg": "user 不存在"}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        if not Favorite.objects.filter(post=post, user=user).exists():
            Favorite.objects.create(post=post, user=user, created_at=timezone.now())
            PostEntity.objects.filter(post_id=post.post_id).update(favorite_num=models.F("favorite_num") + 1)

    return ok()


@api_view(["POST"])
@login_required
def comment(request):
    post_id = request.data.get("post_id")
    user_id = request.data.get("user_id")
    comment_text = request.data.get("comment")

    if post_id is None or user_id is None or not comment_text:
        return Response({"code": 400, "msg": "post_id、user_id、comment 必填"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = PostEntity.objects.get(post_id=post_id)
        user = User.objects.get(user_id=user_id)
    except PostEntity.DoesNotExist:
        return Response({"code": 404, "msg": "post 不存在"}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"code": 404, "msg": "user 不存在"}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    with transaction.atomic():
        obj, created = Comment.objects.update_or_create(
            post=post,
            user=user,
            defaults={"comment_content": comment_text, "created_at": now},
        )
        if created:
            PostEntity.objects.filter(post_id=post.post_id).update(comment_num=models.F("comment_num") + 1)

    return ok()
