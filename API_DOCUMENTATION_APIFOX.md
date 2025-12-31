# API 文档 - Apifox 测试

## 1. 发布项目接口

### 接口信息
- **URL**: `/api/project/publish`
- **方法**: `POST`
- **需要认证**: 是

### 请求头
```
Authorization: Bearer <token>
Content-Type: application/json
```

### 请求参数

根据 `post_type` 的不同，请求参数也不同：

#### 1.1 科研项目 (post_type: "research")

**请求体 JSON**:
```json
{
  "post_type": "research",
  "research_name": "深度学习在网络安全中的应用研究",
  "research_direction": "网络安全",
  "tech_stack": "Python, TensorFlow, PyTorch",
  "recruit_quantity": 3,
  "starttime": "2024-01-01",
  "endtime": "2024-12-31",
  "outcome": "发表论文1篇，申请专利1项",
  "contact": "teacher@example.com",
  "appendix": ""
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "发布成功",
  "data": {
    "post_id": 1
  }
}
```

**失败响应 (400)**:
```json
{
  "code": 400,
  "msg": "数据验证失败",
  "errors": {
    "research_name": ["该字段是必填字段"]
  }
}
```

#### 1.2 竞赛项目 (post_type: "competition")

**请求体 JSON**:
```json
{
  "post_type": "competition",
  "competition_name": "全国大学生网络安全竞赛",
  "competition_type": "AC",
  "deadline": "2024-06-30",
  "team_require": "需1名算法 + 2名开发",
  "guide_way": "online",
  "reward": "一等奖奖金5000元",
  "appendix": ""
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "发布成功",
  "data": {
    "post_id": 2
  }
}
```

**失败响应 (400)**:
```json
{
  "code": 400,
  "msg": "数据验证失败",
  "errors": {
    "competition_name": ["该字段是必填字段"]
  }
}
```

#### 1.3 个人技能 (post_type: "personal")

**请求体 JSON**:
```json
{
  "post_type": "personal",
  "major": "网络工程",
  "skill": "python",
  "skill_degree": "skillful",
  "project_experience": "参加过一次大创项目",
  "experience_link": "https://github.com/www-light/Network-Engineering-Collaboration-Platform",
  "habit_tag": [1, 2, 3],
  "spend_time": "每周15小时",
  "expect_worktype": "research",
  "filter": "all",
  "appendix": ""
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "发布成功",
  "data": {
    "post_id": 3
  }
}
```

**失败响应 (400)**:
```json
{
  "code": 400,
  "msg": "数据验证失败",
  "errors": {
    "major": ["该字段是必填字段"]
  }
}
```

**未授权响应 (401)**:
```json
{
  "code": 401,
  "msg": "未登录或token无效"
}
```

**权限不足响应 (403)**:
```json
{
  "code": 403,
  "msg": "只有教师可以发布科研项目"
}
```

---

## 2. 获取项目列表接口

### 接口信息
- **URL**: `/api/project/list`
- **方法**: `GET`
- **需要认证**: 否

### 请求头
```
Content-Type: application/json
```

### 查询参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| post_type | string | 否 | 项目类型筛选: research/competition/personal | research |
| page | integer | 否 | 页码，从1开始（默认：1） | 1 |
| page_size | integer | 否 | 每页数量（默认：20，最多100） | 20 |

### 请求示例

#### 2.1 获取所有项目（第一页）
```
GET /api/project/list
```

#### 2.2 获取科研项目（第二页，每页10条）
```
GET /api/project/list?post_type=research&page=2&page_size=10
```

#### 2.3 获取竞赛项目
```
GET /api/project/list?post_type=competition
```

#### 2.4 获取个人技能项目
```
GET /api/project/list?post_type=personal&page=1&page_size=50
```

### 成功响应 (200)

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "items": [
      {
        "post_id": 1,
        "post_type": "research",
        "title": "深度学习在网络安全中的应用研究",
        "teacher_name": "张教授",
        "like_num": 10,
        "favorite_num": 5,
        "comment_num": 3,
        "create_time": "2024-01-01T10:00:00Z"
      },
      {
        "post_id": 2,
        "post_type": "competition",
        "title": "全国大学生网络安全竞赛",
        "teacher_name": "李老师",
        "like_num": 8,
        "favorite_num": 4,
        "comment_num": 2,
        "create_time": "2024-01-02T14:30:00Z"
      },
      {
        "post_id": 3,
        "post_type": "personal",
        "title": "网络工程",
        "teacher_name": "林",
        "like_num": 0,
        "favorite_num": 0,
        "comment_num": 1,
        "create_time": "2024-12-30T08:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 空列表响应 (200)

```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20,
    "total_pages": 0
  }
}
```

### 错误响应 (500)

```json
{
  "code": 500,
  "msg": "获取项目列表失败: <错误详情>"
}
```

---

## 字段说明

### post_type 字段值
- `research`: 科研项目（教师发布）
- `competition`: 竞赛项目（教师发布）
- `personal`: 个人技能（学生发布）

### competition_type 字段值
- `IETP`: 大创项目
- `AC`: 学科竞赛
- `CC`: 企业合作竞赛

### guide_way 字段值
- `online`: 线上
- `offline`: 线下

### skill_degree 字段值
- `skillful`: 熟练
- `known`: 了解

### expect_worktype 字段值
- `research`: 科研
- `competition`: 大创
- `innovation`: 竞赛

### filter 字段值
- `all`: 所有项目
- `cross`: 可接受跨方向合作
- `local`: 优先本地项目

---

## Apifox 测试步骤

### 测试发布项目接口

1. **前置条件**: 先调用登录接口获取 token
   ```
   POST /api/auth/login
   {
     "identity": 0,  // 0-学生, 1-教师
     "account": "675979030",
     "password": "123456"
   }
   ```

2. **设置环境变量**: 将登录返回的 token 保存为环境变量 `token`

3. **设置请求头**: 
   - `Authorization`: `Bearer {{token}}`
   - `Content-Type`: `application/json`

4. **选择项目类型**: 根据要测试的类型，选择对应的请求体 JSON

5. **发送请求**: 点击发送，查看响应

### 测试获取项目列表接口

1. **设置请求方法**: GET

2. **设置查询参数**（可选）:
   - `post_type`: research/competition/personal
   - `page`: 1
   - `page_size`: 20

3. **发送请求**: 点击发送，查看响应

---

## 注意事项

1. **认证**: 发布项目接口需要登录，请先获取 token
2. **权限**: 
   - 科研项目和竞赛项目只能由教师发布
   - 个人技能只能由学生发布
3. **日期格式**: 日期字段使用 `YYYY-MM-DD` 格式
4. **分页**: 列表接口支持分页，默认每页20条，最多100条
5. **标签**: 个人技能的 `habit_tag` 是标签ID数组，最多3个

