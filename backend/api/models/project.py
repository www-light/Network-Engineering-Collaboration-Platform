"""
项目相关模型
包括：ResearchProject, CompetitionProject, SkillInformation
"""
from django.db import models
from .post import PostEntity
from .user import TeacherEntity, StudentEntity


class ResearchProject(models.Model):
    """科研项目表"""
    post = models.OneToOneField(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        primary_key=True,
        verbose_name='发布信息ID'
    )
    teacher = models.ForeignKey(
        TeacherEntity,
        on_delete=models.CASCADE,
        db_column='teacher_id',
        verbose_name='教师ID'
    )
    research_name = models.CharField(max_length=255, verbose_name='科研项目名称')
    recruit_quantity = models.IntegerField(verbose_name='招募数量')
    starttime = models.DateTimeField(verbose_name='开始时间')
    endtime = models.DateTimeField(verbose_name='结束时间')
    outcome = models.CharField(max_length=255, verbose_name='预期成果')
    contact = models.CharField(max_length=255, verbose_name='联系方式')
    
    class Meta:
        db_table = 'Research_project'
        verbose_name = '科研项目'
        verbose_name_plural = '科研项目'
        ordering = ['-post__create_time']
    
    def __str__(self):
        return self.research_name


class CompetitionProject(models.Model):
    """竞赛项目表"""
    post = models.OneToOneField(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        primary_key=True,
        verbose_name='发布信息ID'
    )
    teacher = models.ForeignKey(
        TeacherEntity,
        on_delete=models.CASCADE,
        db_column='teacher_id',
        verbose_name='教师ID'
    )
    
    competition_type = models.SmallIntegerField(
        choices=[
            (0, 'IETP'),
            (1, 'AC'),
            (2, 'CC')
        ],
        default=0,
        verbose_name='竞赛类型',
        help_text='IETP-- 大创项目, AC-- 学科竞赛, CC-- 企业合作竞赛'
    )
    competition_name = models.CharField(max_length=255, verbose_name='竞赛名称')
    deadline = models.DateTimeField(verbose_name='截止时间')
    team_require = models.CharField(max_length=255, verbose_name='团队要求')
    guide_way = models.SmallIntegerField(
        choices=[
            (0, 'online'),
            (1, 'offline')
        ],
        default=0,
        verbose_name='指导方式'
    )
    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name='奖励')
    
    class Meta:
        db_table = 'Competition_project'
        verbose_name = '竞赛项目'
        verbose_name_plural = '竞赛项目'
        ordering = ['-post__create_time']
    
    def __str__(self):
        return self.competition_name


class SkillInformation(models.Model):
    """学生技能发布表"""
    post = models.OneToOneField(
        PostEntity,
        on_delete=models.CASCADE,
        db_column='post_id',
        primary_key=True,
        verbose_name='发布信息ID'
    )
    student = models.ForeignKey(
        StudentEntity,
        on_delete=models.CASCADE,
        db_column='student_id',
        verbose_name='学生ID'
    )
    project_experience = models.CharField(max_length=255, verbose_name='项目经验')
    experience_link = models.CharField(max_length=255, blank=True, null=True, verbose_name='经验链接')
    habit_tag = models.CharField(max_length=255, verbose_name='习惯标签')
    spend_time = models.CharField(max_length=255, verbose_name='可投入时间')
    expect_worktype = models.CharField(max_length=255, verbose_name='期望工作类型')
    filter = models.CharField(max_length=255, verbose_name='筛选条件')
    class Meta:
        db_table = 'Skill_information'
        verbose_name = '学生技能发布'
        verbose_name_plural = '学生技能发布'
        ordering = ['-post__create_time']
    
    def __str__(self):
        return f'{self.student.student_name} 的技能信息'

