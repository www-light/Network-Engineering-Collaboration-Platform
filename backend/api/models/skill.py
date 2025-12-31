"""
技能相关模型
包括：Skill, StudentSkill
"""
from django.db import models
from .user import StudentEntity
from .post import PostEntity

class Skill(models.Model):
    """技能表"""
    skill_id = models.AutoField(primary_key=True, verbose_name='技能ID')
    skill_name = models.CharField(max_length=255, unique=True, verbose_name='技能名称')
    
    class Meta:
        db_table = 'Skill'
        verbose_name = '技能'
        verbose_name_plural = '技能'
        ordering = ['skill_id']
    
    def __str__(self):
        return f'{self.skill_name} (ID: {self.skill_id})'


class StudentSkill(models.Model):
    """学生技能关联表"""
    id = models.AutoField(primary_key=True, verbose_name='关联ID')
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        db_column='skill_id',
        verbose_name='技能ID'
    )
    proficiency = models.IntegerField(verbose_name='熟练度', help_text='熟练度等级')
    
    class Meta:
        db_table = 'Stu_skill'
        verbose_name = '学生技能'
        verbose_name_plural = '学生技能'
        unique_together = [['post', 'skill']]
        ordering = ['id']
    
    def __str__(self):
        return f'Post {self.post_id} - 技能 {self.skill.skill_name} (熟练度: {self.proficiency})'
