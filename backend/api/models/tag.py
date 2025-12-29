"""
标签相关模型
包括：Tag, PostTag
"""
from django.db import models
from .post import PostEntity


class Tag(models.Model):
    """标签表"""
    tag_id = models.AutoField(primary_key=True, verbose_name='标签号')
    name = models.CharField(max_length=255, verbose_name='标签名称')
    created_at = models.DateTimeField(verbose_name='创建时间')
    
    class Meta:
        db_table = 'Tag'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['tag_id']
    
    def __str__(self):
        return self.name


class PostTag(models.Model):
    """发布信息标签表"""
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        db_column='tag_id',
        verbose_name='标签ID'
    )
    
    class Meta:
        db_table = 'Post_tag'
        verbose_name = '发布信息标签'
        verbose_name_plural = '发布信息标签'
        unique_together = [['post', 'tag']]
        ordering = ['post', 'tag']
    
    def __str__(self):
        return f'Post {self.post.post_id} - Tag {self.tag.name}'

