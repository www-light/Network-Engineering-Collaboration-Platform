"""
文件和附件相关模型
包括：PostAttachment
"""
from django.db import models
import uuid
from .post import PostEntity


class PostAttachment(models.Model):
    """发布附件表"""
    FILE_TYPES = (
        (1, '科研材料'),
        (2, '大创或竞赛'),
        (3, '个人项目经历'),
        (4, '个人证书简历'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='附件ID')
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        related_name='attachments',
        verbose_name='发布信息ID'
    )
    original_filename = models.CharField(max_length=255, verbose_name='原始文件名')
    storage_path = models.CharField(max_length=255, verbose_name='存储路径')
    file_size = models.IntegerField(verbose_name='文件大小', help_text='单位：字节')
    mime_type = models.CharField(max_length=100, verbose_name='MIME类型')
    file_type = models.SmallIntegerField(
        choices=FILE_TYPES,
        default=4,
        verbose_name='文件类型'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    download_url = models.URLField(max_length=500, verbose_name='下载URL', blank=True, null=True)
    formatted_size = models.CharField(max_length=50, verbose_name='格式化文件大小', help_text='如: 1.5MB', blank=True, null=True)
    
    class Meta:
        db_table = 'Post_attachment'
        verbose_name = '发布附件'
        verbose_name_plural = '发布附件'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.original_filename} (Post {self.post})'
