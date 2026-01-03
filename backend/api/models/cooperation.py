"""
合作关系模型
包括：TeacherStudentCooperation
"""
from django.db import models
from .user import TeacherEntity, StudentEntity
from .post import PostEntity


class TeacherStudentCooperation(models.Model):
    """合作关系表"""
    STATUS_CHOICES = [
        (2, 'pending'),
        (3, 'confirmed'),
        (4, 'rejected'),
        (5, 'canceled'),
    ]
    cooperation_id = models.AutoField(primary_key=True, verbose_name='合作关系ID')
    teacher = models.ForeignKey(
        TeacherEntity,
        on_delete=models.CASCADE,
        db_column='teacher_id',
        verbose_name='教师ID'
    )
    student = models.ForeignKey(
        StudentEntity,
        on_delete=models.CASCADE,
        db_column='student_id',
        verbose_name='学生ID'
    )
    post = models.ForeignKey(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        verbose_name='发布信息ID'
    )
    role = models.BooleanField(verbose_name='角色')
    status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        verbose_name='状态',
        help_text='状态: 2-待双方确认, 3-已确认, 4-已拒绝,5-已取消'
    )
    created_at = models.DateTimeField(verbose_name='创建时间')
    updated_at = models.DateTimeField(verbose_name='更新时间')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='确认时间')
    
    class Meta:
        db_table = 'Teacher_student_cooperation'
        verbose_name = '师生合作关系'
        verbose_name_plural = '师生合作关系'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Cooperation {self.cooperation_id}: Teacher {self.teacher.teacher_id} - Student {self.student.student_id}'

