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
    
    注意：原 SQL 中使用 (post_id, user_id) 作为主键，意味着每个用户对每个帖子只能有一条评论。
    Django 不支持复合主键，这里使用 unique_together 来保持唯一性约束。
    如果需要允许多条评论，建议后续添加 comment_id 作为主键。
    """
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
        # 原 SQL 中使用 (post_id, user_id) 作为主键，这里用 unique_together 模拟
        unique_together = [['post', 'user']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comment: User {self.user.user_id} on Post {self.post.post_id}'

