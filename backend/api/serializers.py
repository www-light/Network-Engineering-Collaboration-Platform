"""
认证相关序列化器
"""
from rest_framework import serializers
from .models import User, StudentEntity, TeacherEntity


class RegisterSerializer(serializers.Serializer):
    """注册序列化器"""
    identity = serializers.IntegerField(help_text='身份: 0-学生, 1-教师')
    account = serializers.CharField(help_text='学号 or 教工号')
    name = serializers.CharField(help_text='姓名')
    password = serializers.CharField(write_only=True, help_text='密码')
    extra = serializers.DictField(help_text='额外信息: 学生需要grade, 教师需要title')
    
    def validate_identity(self, value):
        """验证身份值"""
        if value not in [0, 1]:
            raise serializers.ValidationError("identity 必须是 0（学生）或 1（教师）")
        return value
    
    def validate(self, attrs):
        """验证额外信息"""
        identity = attrs.get('identity')
        extra = attrs.get('extra', {})
        
        if identity == 0:  # 学生
            if 'grade' not in extra:
                raise serializers.ValidationError({"extra": "学生注册需要提供 grade 字段"})
            grade = extra['grade']
            try:
                grade = int(grade)
                if grade not in [1, 2, 3, 4]:
                    raise serializers.ValidationError({"extra": "grade 必须是 1-4 之间的整数"})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"extra": "grade 必须是有效的整数"})
        elif identity == 1:  # 教师
            if 'title' not in extra:
                raise serializers.ValidationError({"extra": "教师注册需要提供 title 字段"})
        
        return attrs
    
    def create(self, validated_data):
        """创建用户"""
        identity = validated_data['identity']
        account = validated_data['account']
        name = validated_data['name']
        password = validated_data['password']
        extra = validated_data['extra']
        
        # 将 account 转换为整数
        try:
            account_int = int(account)
        except (ValueError, TypeError):
            raise serializers.ValidationError({"account": "账号格式错误，必须是数字"})
        
        # 检查账号是否已存在
        if identity == 0:  # 学生
            if StudentEntity.objects.filter(student_id=account_int).exists():
                raise serializers.ValidationError({"account": "该学号已被注册"})
        else:  # 教师
            if TeacherEntity.objects.filter(teacher_id=account_int).exists():
                raise serializers.ValidationError({"account": "该教工号已被注册"})
        
        # 创建 User
        user = User(identity=identity, token='')  # 注册时token为空，登录时生成
        user.set_password(password)
        user.save()
        
        # 创建对应的实体
        if identity == 0:  # 学生
            StudentEntity.objects.create(
                student_id=account_int,
                user=user,
                student_name=name,
                grade=int(extra['grade'])
            )
        else:  # 教师
            TeacherEntity.objects.create(
                teacher_id=account_int,
                user=user,
                teacher_name=name,
                title=extra['title']
            )
        
        return user


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    identity = serializers.IntegerField(help_text='身份: 0-学生, 1-教师')
    account = serializers.CharField(help_text='学号 / 教工号')
    password = serializers.CharField(write_only=True, help_text='密码')
    
    def validate_identity(self, value):
        """验证身份值"""
        if value not in [0, 1]:
            raise serializers.ValidationError("identity 必须是 0（学生）或 1（教师）")
        return value
    
    def validate(self, attrs):
        """验证用户和密码"""
        identity = attrs.get('identity')
        account = attrs.get('account')
        password = attrs.get('password')
        
        # 将 account 转换为整数
        try:
            account_int = int(account)
        except (ValueError, TypeError):
            raise serializers.ValidationError({"account": "账号格式错误，必须是数字"})
        
        # 根据身份查找用户
        try:
            if identity == 0:  # 学生
                student = StudentEntity.objects.get(student_id=account_int)
                user = student.user
            else:  # 教师
                teacher = TeacherEntity.objects.get(teacher_id=account_int)
                user = teacher.user
            
            # 验证身份是否匹配
            if user.identity != identity:
                raise serializers.ValidationError("身份不匹配")
            
            # 验证密码
            if not user.check_password(password):
                raise serializers.ValidationError("密码错误")
            
            attrs['user'] = user
        except StudentEntity.DoesNotExist:
            raise serializers.ValidationError({"account": "学生账号不存在"})
        except TeacherEntity.DoesNotExist:
            raise serializers.ValidationError({"account": "教师账号不存在"})
        
        return attrs


class RegisterResponseSerializer(serializers.Serializer):
    """注册响应序列化器"""
    user_id = serializers.IntegerField()
    identity = serializers.IntegerField()


class LoginResponseSerializer(serializers.Serializer):
    """登录响应序列化器"""
    user_id = serializers.IntegerField()
    name=serializers.CharField()
    identity = serializers.IntegerField()
    token = serializers.CharField()


class ResearchPublishSerializer(serializers.Serializer):
    """科研项目发布序列化器"""
    post_id = serializers.IntegerField(required=False, allow_null=True, help_text='项目ID（可选，用于更新）')
    teacher_id = serializers.IntegerField(help_text='教师ID')
    research_name = serializers.CharField(help_text='科研项目名称')
    research_direction = serializers.CharField(help_text='研究方向')
    tech_stack = serializers.CharField(help_text='技术栈')
    recruit_quantity = serializers.IntegerField(help_text='招募数量')
    starttime = serializers.IntegerField(help_text='开始时间（Unix时间戳，毫秒）')
    endtime = serializers.IntegerField(help_text='结束时间（Unix时间戳，毫秒）')
    outcome = serializers.CharField(help_text='预期成果')
    contact = serializers.CharField(help_text='联系方式')
    visibility = serializers.IntegerField(required=False, default=0, help_text='可见权限: 0-公开, 1-仅教师可见, 2-仅学生可见')


class CompetitionPublishSerializer(serializers.Serializer):
    """竞赛项目发布序列化器"""
    post_id = serializers.IntegerField(required=False, allow_null=True, help_text='项目ID（可选，用于更新）')
    teacher_id = serializers.IntegerField(help_text='教师ID')
    competition_type = serializers.CharField(help_text='竞赛类型: IETP/AC/CC')
    competition_name = serializers.CharField(help_text='竞赛名称')
    deadline = serializers.IntegerField(help_text='截止时间（Unix时间戳，毫秒）')
    team_require = serializers.CharField(help_text='团队要求')
    guide_way = serializers.CharField(help_text='指导方式: online/offline')
    reward = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='奖励')
    visibility = serializers.IntegerField(required=False, default=0, help_text='可见权限: 0-公开, 1-仅教师可见, 2-仅学生可见')


class PersonalPublishSerializer(serializers.Serializer):
    """个人技能发布序列化器"""
    post_id = serializers.IntegerField(required=False, allow_null=True, help_text='项目ID（可选，用于更新）')
    student_id = serializers.IntegerField(help_text='学生ID')
    major = serializers.CharField(help_text='专业')
    skills = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        help_text='技能列表，每个技能包含skill_name和skill_degree'
    )
    project_experience = serializers.CharField(required=False, allow_blank=True, help_text='项目经验')
    experience_link = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='经验链接URL')
    habit_tag = serializers.CharField(required=False, allow_blank=True, help_text='习惯标签（字符串，如"人工智能"）')
    spend_time = serializers.CharField(help_text='可投入时间')
    expect_worktype = serializers.CharField(help_text='期望工作类型: research/competition/innovation')
    filter = serializers.CharField(help_text='筛选条件: all/cross/local')
    visibility = serializers.IntegerField(required=False, default=0, help_text='可见权限: 0-公开, 1-仅教师可见, 2-仅学生可见')