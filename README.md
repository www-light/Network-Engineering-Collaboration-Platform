# 网络工程协作平台

基于Django和Vue3构建的现代化前后端分离协作平台。

## 项目结构

```
Network-Engineering-Collaboration-Platform/
├── backend/                 # Django后端项目
│   ├── config/             # Django配置文件
│   ├── api/                # API应用
│   ├── manage.py           # Django管理脚本
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue3前端项目
│   ├── src/                # 源代码目录
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   └── main.js         # 入口文件
│   ├── package.json        # Node.js依赖
│   └── vite.config.js      # Vite配置
└── README.md               # 项目说明文档
```

## 技术栈

### 后端
- Django 4.2
- Django REST Framework
- django-cors-headers (CORS支持)
- python-dotenv (环境变量管理)

### 前端
- Vue 3
- Vite
- Vue Router
- Pinia (状态管理)
- Axios (HTTP客户端)

## 快速开始

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
# 复制示例文件
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac

# 编辑.env文件，设置SECRET_KEY等
```

5. 运行数据库迁移：
```bash
python manage.py migrate
```

6. 创建超级用户（可选）：
```bash
python manage.py createsuperuser
```

7. 启动开发服务器：
```bash
python manage.py runserver
```

后端服务将在 `http://localhost:8000` 运行

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端服务将在 `http://localhost:5173` 运行

## API接口

### 健康检查
- **URL**: `/api/health/`
- **方法**: GET
- **响应**: 
```json
{
  "status": "success",
  "message": "Django后端服务运行正常"
}
```

## 开发说明

### 后端开发
- Django项目配置在 `backend/config/settings.py`
- API路由在 `backend/api/urls.py`
- API视图在 `backend/api/views.py`

### 前端开发
- 入口文件: `frontend/src/main.js`
- 路由配置: `frontend/src/router/index.js`
- 页面组件: `frontend/src/views/`

### CORS配置
后端已配置CORS，允许来自前端开发服务器的请求。如需修改，请编辑 `backend/config/settings.py` 中的 `CORS_ALLOWED_ORIGINS`。

### 代理配置
前端Vite配置了代理，将 `/api` 请求转发到后端服务器。配置在 `frontend/vite.config.js` 中。

## 构建生产版本

### 后端
```bash
cd backend
python manage.py collectstatic
```

### 前端
```bash
cd frontend
npm run build
```

构建产物将在 `frontend/dist/` 目录中。

## 许可证

MIT License

