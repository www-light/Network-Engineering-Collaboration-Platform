# 权限验证系统实现完成

## ✅ 已完成的实现

### 1. 权限装饰器 (3个)
位置: `api/utils/auth.py`

- ✅ `@login_required` - 登录验证（原有）
- ✅ `@teacher_required` - 仅教师可操作（新增）
- ✅ `@student_required` - 仅学生可操作（新增）

### 2. 合作流程API模块
位置: `api/views/cooperation.py` （新创建）

| 操作 | 端点 | 方法 | 权限 | 说明 |
|------|------|------|------|------|
| 申请加入 | /cooperation/apply | POST | `@student_required` | 学生申请加入项目 |
| 查看申请 | /cooperation/applications | GET | `@teacher_required` | 教师查看收到的申请 |
| 批准申请 | /cooperation/approve | POST | `@teacher_required` | 教师批准申请 |
| 拒绝申请 | /cooperation/reject | POST | `@teacher_required` | 教师拒绝申请 |
| 取消申请 | /cooperation/cancel | POST | `@student_required` | 学生取消自己的申请 |

### 3. 路由注册
位置: `api/urls.py` （已更新）

在 urlpatterns 中添加了 5 条合作流程相关路由。

### 4. 导入更新
位置: `api/views/post.py` （已更新）

导入了 `teacher_required` 和 `student_required` 装饰器，为未来的教师发布功能准备。

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

## 💻 使用示例

### 学生申请加入项目
```python
# api/views/cooperation.py
@api_view(['POST'])
@login_required
@student_required
def apply_cooperation(request):
    user = request.user  # 已确认为学生
    post_id = request.data.get('post_id')
    # 创建申请...
    return Response({'code': 200, 'msg': '申请已提交'})
```

### 教师批准申请
```python
# api/views/cooperation.py
@api_view(['POST'])
@login_required
@teacher_required
def approve_application(request):
    user = request.user  # 已确认为教师
    application_id = request.data.get('application_id')
    # 批准申请...
    return Response({'code': 200, 'msg': '已批准申请'})
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

❌ **错误的顺序**：
```python
@api_view(['POST'])
@teacher_required            # ❌ 身份检查不能在登录检查前
@login_required
def create_post(request):
    pass
```

## 🎯 测试权限

### 学生调用教师API（应返回403）
```bash
curl -X POST http://127.0.0.1:8000/api/cooperation/approve \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{"application_id": 1}'
```

### 教师调用学生API（应返回403）
```bash
curl -X POST http://127.0.0.1:8000/api/cooperation/apply \
  -H "Authorization: Bearer <teacher_token>" \
  -H "Content-Type: application/json" \
  -d '{"post_id": 123}'
```

### 未登录用户（应返回401）
```bash
curl -X POST http://127.0.0.1:8000/api/cooperation/apply \
  -H "Content-Type: application/json" \
  -d '{"post_id": 123}'
```

## 🔄 后续实现清单

以下接口仍需要完整实现（目前有TODO注释）：

### 1. 创建Application模型
定义合作申请表，用于存储学生的申请信息

### 2. 合作流程API完成实现
- [ ] `apply_cooperation` - 实现申请记录创建和重复检查
- [ ] `list_applications` - 实现申请列表查询
- [ ] `approve_application` - 实现申请批准逻辑
- [ ] `reject_application` - 实现申请拒绝逻辑
- [ ] `cancel_application` - 实现申请取消逻辑

### 3. 教师发布API（可选）
- [ ] `create_post` - 教师创建发布（@teacher_required）
- [ ] `update_post` - 教师更新发布（@teacher_required）
- [ ] `delete_post` - 教师删除发布（@teacher_required）

## 📚 文件对应关系

| 文件 | 修改内容 |
|------|--------|
| api/utils/auth.py | 添加 @teacher_required 和 @student_required 装饰器 |
| api/views/cooperation.py | 创建合作流程API模块（5个端点） |
| api/views/post.py | 导入权限装饰器 |
| api/urls.py | 注册合作流程路由 |

## 🚀 下一步建议

1. **创建Application模型** - 定义数据库表结构
2. **完成合作流程实现** - 实现具体的业务逻辑
3. **添加教师发布功能** - 创建、更新、删除发布
4. **集成测试** - 验证权限控制是否正常工作

---

**日期**: 2026年1月1日  
**分支**: cooperation  
**状态**: ✅ 权限框架完成，待数据模型实现
