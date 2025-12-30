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
    identity = serializers.IntegerField()
    token = serializers.CharField()


class ProjectPublishSerializer(serializers.Serializer):
    """项目发布序列化器"""
    post_type = serializers.CharField(help_text='项目类型: research-科研项目, competition-竞赛项目, personal-个人技能')
    
    # 科研项目字段
    research_name = serializers.CharField(required=False, allow_blank=True)
    research_direction = serializers.CharField(required=False, allow_blank=True)
    tech_stack = serializers.CharField(required=False, allow_blank=True)
    recruit_quantity = serializers.IntegerField(required=False)
    starttime = serializers.CharField(required=False, allow_blank=True)
    endtime = serializers.CharField(required=False, allow_blank=True)
    outcome = serializers.CharField(required=False, allow_blank=True)
    contact = serializers.CharField(required=False, allow_blank=True)
    
    # 竞赛项目字段
    competition_name = serializers.CharField(required=False, allow_blank=True)
    competition_type = serializers.CharField(required=False, allow_blank=True)
    deadline = serializers.CharField(required=False, allow_blank=True)
    team_require = serializers.CharField(required=False, allow_blank=True)
    guide_way = serializers.CharField(required=False, allow_blank=True)
    reward = serializers.CharField(required=False, allow_blank=True)
    
    # 个人技能字段
    major = serializers.CharField(required=False, allow_blank=True)
    skill = serializers.CharField(required=False, allow_blank=True)
    skill_degree = serializers.CharField(required=False, allow_blank=True)
    project_experience = serializers.CharField(required=False, allow_blank=True)
    experience_link = serializers.CharField(required=False, allow_blank=True)
    habit_tag = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    spend_time = serializers.CharField(required=False, allow_blank=True)
    expect_worktype = serializers.CharField(required=False, allow_blank=True)
    filter = serializers.CharField(required=False, allow_blank=True)
    
    # 通用字段
    appendix = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate_post_type(self, value):
        """验证项目类型"""
        if value not in ['research', 'competition', 'personal']:
            raise serializers.ValidationError("post_type 必须是 research、competition 或 personal")
        return value
    
    def validate(self, attrs):
        """根据项目类型验证必填字段"""
        post_type = attrs.get('post_type')
        
        if post_type == 'research':
            required_fields = ['research_name', 'research_direction', 'tech_stack', 
                             'recruit_quantity', 'starttime', 'endtime', 'outcome', 'contact']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"{field} 是必填字段"})
        
        elif post_type == 'competition':
            required_fields = ['competition_name', 'competition_type', 'deadline', 
                             'team_require', 'guide_way']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"{field} 是必填字段"})
        
        elif post_type == 'personal':
            required_fields = ['major', 'skill', 'skill_degree', 'spend_time', 
                             'expect_worktype', 'filter']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"{field} 是必填字段"})
        
        return attrs
