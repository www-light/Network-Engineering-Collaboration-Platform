"""
站内私信相关视图
"""
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models.message import Conversation, Message
from ..models.user import User
from ..models.post import PostEntity
from ..utils.auth import login_required, check_conversation_permission


@api_view(['POST'])
@login_required
def create_conversation(request):
    """发起会话
    
    POST /conversations
    请求头:
    Authorization: Bearer <token>
    
    请求体:
    {
        "post_id": 123,
        "receiver_id": 456
    }
    
    返回:
    {
        "conversation_id": 1
    }
    """
    post_id = request.data.get('post_id')
    receiver_id = request.data.get('receiver_id')
    
    # 从装饰器中获取当前用户
    sender = request.user
    
    if not all([post_id, receiver_id]):
        return Response(
            {'code': 400, 'msg': 'post_id, receiver_id 必填'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        post = PostEntity.objects.get(post_id=post_id)
        receiver = User.objects.get(user_id=receiver_id)
    except PostEntity.DoesNotExist:
        return Response({'code': 404, 'msg': 'post 不存在'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'code': 404, 'msg': 'receiver 不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 检查是否已存在会话（双向查找）
    existing = Conversation.objects.filter(
        Q(user1=sender, user2=receiver) | Q(user1=receiver, user2=sender)
    ).first()
    
    if existing:
        return Response({'conversation_id': existing.conversation_id}, status=status.HTTP_200_OK)
    
    # 创建新会话
    now = timezone.now()
    conversation = Conversation.objects.create(
        user1=sender,
        user2=receiver,
        status=1,
        created_at=now,
        last_message_at=now
    )
    
    return Response({'conversation_id': conversation.conversation_id}, status=status.HTTP_200_OK)


@api_view(['GET'])
@login_required
def list_conversations(request):
    """拉取会话列表
    
    GET /conversations/lists?cursor=xxx&limit=20
    请求头:
    Authorization: Bearer <token>
    
    返回:
    [
        {
            "conversation_id": 1,
            "user1_id": 1,
            "user2_id": 2,
            "status": "1",
            "last_message_at": "2025-12-25T15:49:11.502Z"
        }
    ]
    """
    # 从装饰器中获取当前用户
    user = request.user
    
    cursor = request.query_params.get('cursor')
    limit = int(request.query_params.get('limit', 20))
    
    # 查询用户相关的所有会话
    conversations = Conversation.objects.filter(
        Q(user1_id=user.user_id) | Q(user2_id=user.user_id)
    )
    
    # cursor分页（基于conversation_id）
    if cursor:
        conversations = conversations.filter(conversation_id__lt=int(cursor))
    
    conversations = conversations.order_by('-last_message_at')[:limit]
    
    result = []
    for conv in conversations:
        result.append({
            'conversation_id': conv.conversation_id,
            'user1_id': conv.user1_id,
            'user2_id': conv.user2_id,
            'status': str(conv.status),
            'last_message_at': conv.last_message_at.isoformat()
        })
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@login_required
def close_conversation(request, conversation_id):
    """关闭会话
    
    PATCH /conversations/{conversation_id}/close
    请求头:
    Authorization: Bearer <token>
    
    返回: {}
    """
    try:
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        
        # 权限检查：只有会话参与者才能关闭会话
        if not check_conversation_permission(request.user, conversation):
            return Response(
                {'code': 403, 'msg': '无权操作此会话'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        conversation.status = 0
        conversation.save(update_fields=['status'])
        return Response({}, status=status.HTTP_200_OK)
    except Conversation.DoesNotExist:
        return Response({'code': 404, 'msg': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def send_message(request, conversation_id):
    """发送消息
    
    POST /conversations/{conversation_id}/messages
    请求头:
    Authorization: Bearer <token>
    
    请求体:
    {
        "type": "text",  # text/file/link 或 0/1/2
        "content": "老师您好"
    }
    
    返回: {}
    """
    msg_type = request.data.get('type')
    content = request.data.get('content')
    
    # 从装饰器中获取当前用户
    sender = request.user
    
    if not all([msg_type, content]):
        return Response(
            {'code': 400, 'msg': 'type, content 必填'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 转换type为数字
    type_map = {'text': 0, 'file': 1, 'link': 2}
    if msg_type in type_map:
        content_type = type_map[msg_type]
    else:
        try:
            content_type = int(msg_type)
        except ValueError:
            return Response({'code': 400, 'msg': 'type 必须是 text/file/link 或 0/1/2'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        
        # 权限检查：只有会话参与者才能发送消息
        if not check_conversation_permission(sender, conversation):
            return Response(
                {'code': 403, 'msg': '无权操作此会话'},
                status=status.HTTP_403_FORBIDDEN
            )
        
    except Conversation.DoesNotExist:
        return Response({'code': 404, 'msg': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    now = timezone.now()
    with transaction.atomic():
        Message.objects.create(
            conversation=conversation,
            sender=sender,
            content_type=content_type,
            content=content,
            is_read=False,
            create_time=now
        )
        # 更新会话的最后消息时间
        conversation.last_message_at = now
        conversation.save(update_fields=['last_message_at'])
    
    return Response({}, status=status.HTTP_200_OK)


@api_view(['GET'])
@login_required
def list_messages(request, conversation_id):
    """拉取消息列表
    
    GET /conversations/{conversation_id}/messages?cursor=xxx&limit=20
    请求头:
    Authorization: Bearer <token>
    
    返回:
    {
        "conversation_id": 1,
        "page": 1,
        "page_size": 20,
        "has_more": true,
        "messages": [...]
    }
    """
    try:
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        
        # 权限检查：只有会话参与者才能查看消息
        if not check_conversation_permission(request.user, conversation):
            return Response(
                {'code': 403, 'msg': '无权访问此会话'},
                status=status.HTTP_403_FORBIDDEN
            )
        
    except Conversation.DoesNotExist:
        return Response({'code': 404, 'msg': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    cursor = request.query_params.get('cursor')
    limit = int(request.query_params.get('limit', 20))
    
    messages = Message.objects.filter(conversation=conversation)
    
    # cursor分页（基于message_id）
    if cursor:
        messages = messages.filter(message_id__lt=int(cursor))
    
    messages = messages.order_by('-create_time')[:limit + 1]
    message_list = list(messages)
    
    has_more = len(message_list) > limit
    if has_more:
        message_list = message_list[:limit]
    
    result = {
        'conversation_id': conversation.conversation_id,
        'page': 1,  # 简化处理，实际可根据cursor计算
        'page_size': limit,
        'has_more': has_more,
        'messages': []
    }
    
    for msg in message_list:
        result['messages'].append({
            'message_id': msg.message_id,
            'conversation_id': msg.conversation_id,
            'sender_id': msg.sender_id,
            'content_type': str(msg.content_type),
            'content': msg.content,
            'is_read': msg.is_read,
            'create_time': msg.create_time.isoformat()
        })
    
    return Response(result, status=status.HTTP_200_OK)
