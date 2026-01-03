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
from ..models.user import User,StudentEntity,TeacherEntity
from ..models.post import PostEntity
from ..utils.auth import login_required, check_conversation_permission


@api_view(['POST'])
@login_required
def create_conversation(request):
    """发起会话
    
    POST /conversations/post
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
        # 若已存在且关闭，则重新开启并更新时间
        if existing.status == 0:
            existing.status = 1
            existing.last_message_at = timezone.now()
            existing.save(update_fields=['status', 'last_message_at'])
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
        stu=StudentEntity.objects.filter(user_id=conv.user1_id).first()
        if stu:
            user1_name=stu.student_name
        else:
            tea=TeacherEntity.objects.filter(user_id=conv.user1_id).first()
            user1_name=tea.teacher_name if tea else "未知用户"
        stu1=StudentEntity.objects.filter(user_id=conv.user2_id).first()
        if stu1:
            user2_name=stu1.student_name
        else:
            tea1=TeacherEntity.objects.filter(user_id=conv.user2_id).first()
            user2_name=tea1.teacher_name if tea1 else "未知用户"    
        unread_count = Message.objects.filter(
            conversation=conv,
            is_read=False
        ).exclude(sender_id=user.user_id).count()

        result.append({
            'conversation_id': conv.conversation_id,
            'user1_id': conv.user1_id,#会话发起者
            'user2_id': conv.user2_id,
            'status': str(conv.status),
            'last_message_at': conv.last_message_at.isoformat(),
            'user1_name': user1_name,
            'user2_name': user2_name,
            'unread_count': unread_count
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
    created_messages = []
    with transaction.atomic():
        user_msg = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content_type=content_type,
            content=content,
            is_read=False,
            create_time=now
        )
        created_messages.append(user_msg)

        # 检查接收者的自动回复设置
        recipient = conversation.user2 if conversation.user1 == sender else conversation.user1
        if recipient.auto_reply_enabled and recipient.auto_reply_message:
            auto_msg = Message.objects.create(
                conversation=conversation,
                sender=recipient,
                content_type=0,  # text type
                content=recipient.auto_reply_message,
                is_read=False,
                create_time=now
            )
            created_messages.append(auto_msg)

        # 更新会话的最后消息时间
        conversation.last_message_at = now
        conversation.save(update_fields=['last_message_at'])
    
    # 返回本次产生的消息，便于前端即时渲染
    return Response(
        {
            'messages': [
                {
                    'message_id': m.message_id,
                    'conversation_id': m.conversation_id,
                    'sender_id': m.sender_id,
                    'content_type': str(m.content_type),
                    'content': m.content,
                    'is_read': m.is_read,
                    'create_time': m.create_time.isoformat()
                }
                for m in created_messages
            ]
        },
        status=status.HTTP_200_OK
    )


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

    # 标记当前用户收到的未读消息为已读
    unread_ids = list(
        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender_id=request.user.user_id).values_list('message_id', flat=True)
    )
    if unread_ids:
        Message.objects.filter(message_id__in=unread_ids).update(is_read=True)
    
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
        # 如果刚刚被标记为已读，更新返回值
        if msg.message_id in unread_ids:
            msg.is_read = True
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


@api_view(['GET', 'PATCH'])
@login_required
def auto_reply_settings(request):
    """获取或更新用户的自动回复设置
    
    GET /conversations/auto_reply/settings
    请求头:
    Authorization: Bearer <token>
    
    返回:
    {
        "auto_reply_enabled": true,
        "auto_reply_message": "我现在有点忙，稍后回复您"
    }
    
    PATCH /conversations/auto_reply/settings
    请求头:
    Authorization: Bearer <token>
    
    请求体:
    {
        "auto_reply_enabled": true,
        "auto_reply_message": "我现在有点忙，稍后回复您"
    }
    
    返回: {}
    """
    user = request.user
    
    if request.method == 'GET':
        return Response({
            'auto_reply_enabled': user.auto_reply_enabled,
            'auto_reply_message': user.auto_reply_message or ''
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        auto_reply_enabled = request.data.get('auto_reply_enabled')
        auto_reply_message = request.data.get('auto_reply_message')
        
        if auto_reply_enabled is not None:
            user.auto_reply_enabled = auto_reply_enabled
        if auto_reply_message is not None:
            user.auto_reply_message = auto_reply_message
        
        user.save(update_fields=['auto_reply_enabled', 'auto_reply_message'])
        return Response({}, status=status.HTTP_200_OK)

