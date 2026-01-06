# Redis + SSE 实时消息功能 - 使用指南

## 后端改动总结

### 1. 新增文件
- `backend/api/utils/redis_client.py` - Redis 客户端工具，提供发布订阅功能

### 2. 修改文件
- `backend/requirements.txt` - 添加 redis>=5.0.0 依赖
- `backend/config/settings.py` - 添加 REDIS_URL 配置
- `backend/api/utils/auth.py` - 添加 verify_token() 函数
- `backend/api/views/conversation.py` - 发送消息时发布到 Redis，新增 SSE 推流接口
- `backend/api/urls.py` - 新增路由 `/conversations/<id>/stream`

### 3. 核心改动
- **发送消息时**: 保存到数据库后立即 PUBLISH 到 Redis 频道 `conversation:{id}`
- **SSE 接口**: 客户端通过 EventSource 连接 `/conversations/{id}/stream?token=xxx`，实时接收消息

## 前端改动总结

### 修改文件
- `frontend/src/pages/Message.vue` - 添加 SSE 连接逻辑

### 核心改动
1. **建立 SSE 连接**: 选中会话时自动连接 SSE
2. **实时接收消息**: 通过 EventSource.onmessage 接收新消息
3. **自动重连**: SSE 连接断开后 5 秒自动重连
4. **生命周期管理**: 切换会话或组件销毁时关闭旧连接

## 部署步骤

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 确认 Redis 运行
```bash
# Windows 检查 Redis 是否运行
redis-cli ping
# 应返回 PONG

# 如果未运行，启动 Redis（根据你的安装方式）
redis-server
```

### 3. 配置环境变量（可选）
如果 Redis 不在 localhost:6379，在 `.env` 文件中设置：
```
REDIS_URL=redis://your-redis-host:6379/0
```

### 4. 启动后端
```bash
cd backend
python manage.py runserver
```

### 5. 启动前端
```bash
cd frontend
npm run dev
```

## 测试步骤

### 功能测试
1. 打开两个不同浏览器（或一个浏览器 + 一个隐私窗口）
2. 分别登录两个不同用户（A 和 B）
3. A 用户给 B 用户发起会话并发送消息
4. B 用户进入"会话"页面，**无需刷新**即可实时看到 A 的消息
5. B 回复消息，A 也能**实时看到**

### 技术验证
打开浏览器开发者工具 -> Network 标签：
- 查看是否有 `/conversations/{id}/stream` 的 EventSource 连接
- 类型应显示为 `eventsource`
- 状态应为 `pending`（保持连接）
- 查看 Console 应有 "SSE 连接已建立" 日志

## 工作原理

```
用户A发送消息
    ↓
POST /conversations/{id}/messages
    ↓
保存到 MySQL 数据库
    ↓
Redis PUBLISH conversation:{id}
    ↓
所有订阅该频道的 SSE 连接收到消息
    ↓
用户B的浏览器实时显示
```

## 优势
- ✅ 无需 WebSocket，沿用 HTTP 服务器（WSGI）
- ✅ 实时性好（1-2秒延迟）
- ✅ Redis 天然支持多进程/多服务器
- ✅ 自动重连机制
- ✅ 浏览器原生支持 EventSource

## 注意事项
- SSE 连接是单向的（服务器→客户端），发送消息仍用 HTTP POST
- EventSource 不支持自定义请求头，token 通过 URL 参数传递
- 确保 Redis 正常运行，否则消息无法实时推送
- 生产环境建议使用 Redis Sentinel 或 Redis Cluster 保证高可用

## 故障排查

### 1. 消息无法实时收到
- 检查 Redis 是否运行: `redis-cli ping`
- 查看浏览器 Console 是否有 SSE 连接错误
- 查看 Network 中 stream 请求的状态

### 2. SSE 连接一直重连
- 检查 token 是否有效
- 查看后端日志是否有权限错误
- 确认 CORS 配置是否正确

### 3. 发送消息失败
- 检查后端日志
- 确认 Redis 连接正常
- 查看数据库是否正常保存消息
