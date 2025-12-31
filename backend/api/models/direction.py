"""
方向和技术栈相关模型
包括：TechStack, Direction, PostStack, PostDirection
"""
from django.db import models
from .post import PostEntity


class TechStack(models.Model):
    """技术栈表"""
    stack_id = models.AutoField(primary_key=True, verbose_name='技术栈ID')
    tech_stack = models.CharField(max_length=255, unique=True, verbose_name='技术栈名称')
    
    class Meta:
        db_table = 'Tech_stack'
        verbose_name = '技术栈'
        verbose_name_plural = '技术栈'
        ordering = ['stack_id']
    
    def __str__(self):
        return f'{self.tech_stack} (ID: {self.stack_id})'


class Direction(models.Model):
    """方向表"""
    direction_id = models.AutoField(primary_key=True, verbose_name='方向ID')
    direction_name = models.CharField(max_length=255, unique=True, verbose_name='方向名称')
    
    class Meta:
        db_table = 'Direction'
        verbose_name = '方向'
        verbose_name_plural = '方向'
        ordering = ['direction_id']
    
    def __str__(self):
        return f'{self.direction_name} (ID: {self.direction_id})'


class PostStack(models.Model):
    """技术栈关联表（Post与TechStack的关联）"""
    id = models.AutoField(primary_key=True, verbose_name='关联ID')
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    stack = models.ForeignKey(
        TechStack,
        on_delete=models.CASCADE,
        db_column='stack_id',
        verbose_name='技术栈ID'
    )
    
    class Meta:
        db_table = 'Post_stack'
        verbose_name = '技术栈'
        verbose_name_plural = '技术栈'
        unique_together = [['post', 'stack']]
        ordering = ['id']
    
    def __str__(self):
        return f'Post {self.post} - Stack {self.stack.tech_stack}'


class PostDirection(models.Model):
    """发布的方向关联表（Post与Direction的关联）"""
    id = models.AutoField(primary_key=True, verbose_name='关联ID')
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        db_column='direction_id',
        verbose_name='方向ID'
    )
    
    class Meta:
        db_table = 'Post_direction'
        verbose_name = '发布方向'
        verbose_name_plural = '发布方向'
        unique_together = [['post', 'direction']]
        ordering = ['id']
    
    def __str__(self):
        return f'Post {self.post} - Direction {self.direction.direction_name}'
