# 权限验证系统

### 1. 权限装饰器 (3个)
位置: `api/utils/auth.py`

- ✅ `@login_required` - 登录验证（原有）
- ✅ `@teacher_required` - 仅教师可操作（新增）
- ✅ `@student_required` - 仅学生可操作（新增）

## 📋 权限模型

```
学生 (identity=0)              教师 (identity=1)
├─ @student_required          ├─ @teacher_required
│  ├─ apply_cooperation       │  ├─ list_applications
│  └─ cancel_application      │  ├─ approve_application
└─ @login_required            │  ├─ reject_application
   ├─ like/comment/favorite   │  └─ @login_required
   ├─ upload_file             │     ├─ like/comment
   └─ private_message         │     └─ private_message
```

## 🔐 错误响应标准

### 401 - 未登录
```json
{
    "code": 401,
    "msg": "未登录或token无效"
}
```

### 403 - 权限不足（非教师）
```json
{
    "code": 403,
    "msg": "该操作仅限教师执行"
}
```

### 403 - 权限不足（非学生）
```json
{
    "code": 403,
    "msg": "该操作仅限学生执行"
}
```

## 📝 装饰器堆叠规则

✅ **正确的顺序**：
```python
@api_view(['POST'])          # 1. HTTP方法
@login_required              # 2. 验证登录
@teacher_required            # 3. 验证身份
def create_post(request):
    user = request.user
```






