"""
互动相关模型
包括：Like, Favorite, Comment
"""
from django.db import models
from .post import PostEntity
from .user import User


class Like(models.Model):
    """点赞表（注意: Like 是 SQL 关键字）"""
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='用户ID'
    )
    created_at = models.DateTimeField(verbose_name='创建时间')
    
    class Meta:
        db_table = 'Like'
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        unique_together = [['post', 'user']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Like: User {self.user.user_id} -> Post {self.post.post_id}'


class Favorite(models.Model):
    """收藏表"""
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='用户ID'
    )
    created_at = models.DateTimeField(verbose_name='创建时间')
    
    class Meta:
        db_table = 'Favorite'
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = [['post', 'user']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Favorite: User {self.user.user_id} -> Post {self.post.post_id}'


class Comment(models.Model):
    """评论表
    
    允许同一用户对同一帖子发表多条评论
    """
    # 使用id作为主键（Django默认），comment_id作为唯一标识字段
    # 如果数据库已有id字段，这样可以避免迁移冲突
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        verbose_name='用户ID'
    )
    comment_content = models.CharField(max_length=255, verbose_name='评论内容')
    created_at = models.DateTimeField(verbose_name='创建时间')
    
    class Meta:
        db_table = 'Comment'
        verbose_name = '评论'
        verbose_name_plural = '评论'
        # 移除 unique_together 约束，允许多条评论
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comment {self.id}: User {self.user.user_id} on Post {self.post.post_id}'

