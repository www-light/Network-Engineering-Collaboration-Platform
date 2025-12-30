from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import Tag


@api_view(['GET', 'POST'])
def tags(request):
    """标签列表 / 创建标签"""
    if request.method == 'GET':
        tag_list = [
            {'tag_id': tag.tag_id, 'name': tag.name}
            for tag in Tag.objects.all().order_by('tag_id')
        ]
        return Response({'code': 200, 'data': tag_list, 'msg': '获取成功'}, status=status.HTTP_200_OK)

    # POST 创建标签
    name = (request.data.get('name') or '').strip()
    if not name:
        return Response({'code': 400, 'msg': '标签名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    existing = Tag.objects.filter(name=name).first()
    if existing:
        return Response(
            {'code': 200, 'data': {'tag_id': existing.tag_id, 'name': existing.name}, 'msg': '标签已存在'},
            status=status.HTTP_200_OK,
        )

    tag = Tag.objects.create(name=name, created_at=timezone.now())
    return Response(
        {'code': 201, 'data': {'tag_id': tag.tag_id, 'name': tag.name}, 'msg': '创建成功'},
        status=status.HTTP_201_CREATED,
    )

