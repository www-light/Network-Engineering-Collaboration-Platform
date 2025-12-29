"""
用户相关模型
包括：User, StudentEntity, TeacherEntity
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import secrets


class User(models.Model):
    """用户表"""
    IDENTITY_CHOICES = [
        (0, '学生'),
        (1, '教师'),
        (2, '管理员'),
    ]
    
    user_id = models.AutoField(primary_key=True, verbose_name='用户ID')
    identity = models.SmallIntegerField(
        choices=IDENTITY_CHOICES,
        verbose_name='身份',
        help_text='身份: 0-学生, 1-教师, 2-管理员'
    )
    password = models.CharField(max_length=128, verbose_name='密码')
    token = models.CharField(max_length=64, blank=True, null=True, verbose_name='认证令牌')
    
    class Meta:
        db_table = 'User'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['user_id']
    
    def set_password(self, raw_password):
        """设置密码（加密）"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """验证密码"""
        return check_password(raw_password, self.password)
    
    def generate_token(self):
        """生成并保存 token"""
        self.token = secrets.token_urlsafe(32)
        self.save(update_fields=['token'])
        return self.token
    
    def __str__(self):
        return f'User {self.user_id} (身份: {self.get_identity_display()})'


class StudentEntity(models.Model):
    """学生实体表"""
    GRADE_CHOICES = [
        (1, '大一'),
        (2, '大二'),
        (3, '大三'),
        (4, '大四'),
    ]
    
    student_id = models.IntegerField(primary_key=True, verbose_name='学号')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        unique=True,
        verbose_name='用户ID'
    )
    student_name = models.CharField(max_length=255, verbose_name='学生姓名')
    grade = models.SmallIntegerField(
        choices=GRADE_CHOICES,
        verbose_name='年级',
        help_text='年级: 1-大一, 2-大二, 3-大三, 4-大四'
    )
    
    class Meta:
        db_table = 'Student_entity'
        verbose_name = '学生实体'
        verbose_name_plural = '学生实体'
        ordering = ['student_id']
    
    def __str__(self):
        return f'{self.student_name} (学号: {self.student_id})'


class TeacherEntity(models.Model):
    """教师实体表"""
    teacher_id = models.IntegerField(primary_key=True, verbose_name='教工号')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        unique=True,
        verbose_name='用户ID'
    )
    teacher_name = models.CharField(max_length=255, verbose_name='教师姓名')
    title = models.CharField(max_length=255, verbose_name='职称')
    
    class Meta:
        db_table = 'Teacher_entity'
        verbose_name = '教师实体'
        verbose_name_plural = '教师实体'
        ordering = ['teacher_id']
    
    def __str__(self):
        return f'{self.teacher_name} (教工号: {self.teacher_id})'

