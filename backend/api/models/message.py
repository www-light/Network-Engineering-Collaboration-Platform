"""
消息相关模型
包括：Conversation, Message
"""
from django.db import models
from .user import User


class Conversation(models.Model):
    """会话表"""
    STATUS_CHOICES = [
        (0, '已关闭'),
        (1, '活跃'),
    ]
    
    conversation_id = models.AutoField(primary_key=True, verbose_name='会话ID')
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_as_user1',
        db_column='user1_id',
        verbose_name='发起者用户ID'
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_as_user2',
        db_column='user2_id',
        verbose_name='接收者用户ID'
    )
    status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=1,
        verbose_name='状态',
        help_text='状态: 0-closed, 1-active'
    )
    created_at = models.DateTimeField(verbose_name='创建时间')
    last_message_at = models.DateTimeField(verbose_name='最后消息时间')
    
    class Meta:
        db_table = 'Conversation'
        verbose_name = '会话'
        verbose_name_plural = '会话'
        ordering = ['-last_message_at']
    
    def __str__(self):
        return f'Conversation {self.conversation_id}: User {self.user1.user_id} <-> User {self.user2.user_id}'


class Message(models.Model):
    """消息表"""
    CONTENT_TYPE_CHOICES = [
        (0, '文字'),
        (1, '图片'),
        (2, '文件'),
    ]
    
    message_id = models.AutoField(primary_key=True, verbose_name='消息ID')
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        db_column='conversation_id',
        verbose_name='会话ID'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='sender_id',
        verbose_name='发送者ID'
    )
    content_type = models.SmallIntegerField(
        choices=CONTENT_TYPE_CHOICES,
        verbose_name='内容类型',
        help_text='内容类型: 0-文字, 1-图片, 2-文件'
    )
    content = models.CharField(max_length=255, verbose_name='内容')
    is_read = models.BooleanField(verbose_name='阅读状态数据')
    create_time = models.DateTimeField(verbose_name='创建时间')
    
    class Meta:
        db_table = 'Message'
        verbose_name = '消息'
        verbose_name_plural = '消息'
        ordering = ['create_time']
    
    def __str__(self):
        return f'Message {self.message_id} from User {self.sender.user_id}'
    
