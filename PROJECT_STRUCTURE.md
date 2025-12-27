# 项目目录结构

```
frontend/
├── public/                          # 静态资源
├── src/
│   ├── api/                        # API接口封装
│   │   ├── auth.js                 # 登录注册接口
│   │   ├── project.js              # 项目相关接口
│   │   ├── cooperation.js          # 合作流程接口
│   │   ├── conversation.js         # 站内私信接口
│   │   ├── index.js                # API统一导出
│   │   └── request.js              # Axios请求封装
│   ├── components/                 # 公共组件
│   │   ├── ProjectCard.vue        # 项目卡片组件
│   │   ├── ProjectDetail.vue      # 项目详情组件
│   │   └── ...
│   ├── pages/                      # 页面组件
│   │   ├── Login.vue               # 登录页
│   │   ├── Register.vue            # 注册页
│   │   ├── Home.vue                # 主页面（消息推送）
│   │   ├── ProjectList.vue         # 项目列表页（双栏）
│   │   ├── ProjectDetail.vue       # 项目详情页
│   │   ├── ProjectPublish.vue      # 项目发布页
│   │   ├── Profile.vue             # 个人中心页
│   │   ├── Cooperation.vue         # 合作流程页
│   │   ├── Message.vue             # 站内私信列表页
│   │   └── MessageDetail.vue       # 站内私信详情页
│   ├── router/                     # 路由配置
│   │   └── index.js
│   ├── store/                      # Pinia状态管理
│   │   ├── user.js                 # 用户状态
│   │   ├── project.js              # 项目状态
│   │   └── index.js
│   ├── utils/                     # 工具函数
│   │   └── index.js
│   ├── App.vue                     # 根组件
│   ├── main.js                     # 入口文件
│   └── style.css                   # 全局样式
├── index.html
├── package.json
├── vite.config.js                  # Vite配置
└── README.md
```

