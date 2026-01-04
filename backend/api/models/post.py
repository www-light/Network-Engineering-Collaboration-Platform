"""
发布实体模型
包括：PostEntity
"""
from django.db import models


class PostEntity(models.Model):
    """发布实体表"""
    POST_TYPE_CHOICES = [
        (1, '科研项目'),
        (2, '竞赛项目'),
        (3, '学生技能'),
    ]
    
    post_id = models.AutoField(primary_key=True, verbose_name='发布信息ID')
    post_type = models.SmallIntegerField(
        choices=POST_TYPE_CHOICES,
        verbose_name='发布类型',
        help_text='发布类型: 1-科研项目, 2-竞赛项目, 3-学生技能'
    )
    create_time = models.DateTimeField(verbose_name='发布时间')
    like_num = models.IntegerField(default=0, verbose_name='点赞数')
    favorite_num = models.IntegerField(default=0, verbose_name='收藏数')
    comment_num = models.IntegerField(default=0, verbose_name='评论数')
    visibility = models.SmallIntegerField(
        choices=[
            (0, '公开'),
            (1, '仅教师可见'),
            (2, '仅学生可见'),
        ],
        default=0
    )
    recruit_status = models.SmallIntegerField(
        choices=[
            (0, '正在招募'),
            (1, '招募截止'),
        ],
        default=0,
        verbose_name='招募状态',
        help_text='招募状态: 0-正在招募, 1-招募截止'
    )
    class Meta:
        db_table = 'Post_entity'
        verbose_name = '发布实体'
        verbose_name_plural = '发布实体'
        ordering = ['-create_time']
    
    def __str__(self):
        return f'Post {self.post_id} ({self.get_post_type_display()})'

