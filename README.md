# Star Office UI - GitHub Collaboration Platform

> 一个基于 Flask + Vue.js 的实时协作办公平台，支持多 Agent 协同工作

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 构建并运行
docker-compose up -d

# 访问界面
http://localhost:5000
```

### 本地开发

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 启动服务
python main.py

# 访问界面
http://localhost:5000
```

## 📁 项目结构

```
github-collab-officeUI/
├── backend/
│   ├── api/              # API 路由层
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑
│   ├── utils/            # 工具函数
│   ├── config/           # 配置管理
│   ├── tests/            # 单元测试
│   ├── assets/           # 静态资源
│   ├── main.py           # 主入口
│   ├── optimizations.py  # 性能优化
│   └── locustfile.py     # 性能测试
├── frontend/
│   └── index.html        # Vue.js 前端
├── .github/workflows/    # CI/CD 流水线
├── Dockerfile            # Docker 镜像
├── docker-compose.yml    # 容器编排
├── SECURITY.md           # 安全策略
├── CONTRIBUTING.md       # 贡献指南
└── README.md            # 项目文档
```

## 🌟 核心功能

### 1. 多 Agent 协作
- 实时状态同步
- 任务分配与跟踪
- 消息传递机制

### 2. 任务管理
- 创建/更新/删除任务
- 任务状态跟踪
- 任务分配给 Agent

### 3. 实时通信
- WebSocket 支持
- 状态轮询备份
- 即时消息通知

### 4. 性能优化
- LRU 缓存
- 数据库连接池
- 异步任务队列
- 性能监控

## 📊 API 端点

### Agents
- `GET /api/agents` - 获取所有 Agent
- `POST /api/agents` - 创建 Agent
- `PUT /api/agents/<id>` - 更新 Agent
- `DELETE /api/agents/<id>` - 删除 Agent

### Tasks
- `GET /api/tasks` - 获取所有任务
- `POST /api/tasks` - 创建任务
- `PUT /api/tasks/<id>` - 更新任务
- `DELETE /api/tasks/<id>` - 删除任务

### State
- `GET /api/state` - 获取系统状态
- `POST /api/state/sync` - 同步状态

### Assets
- `GET /api/assets/avatars` - 获取头像列表
- `GET /api/assets/themes` - 获取主题列表
- `GET /api/assets/locations` - 获取位置列表

### Config
- `GET /api/config` - 获取系统配置
- `PUT /api/config` - 更新系统配置

## 🧪 测试

### 单元测试
```bash
cd backend
pytest tests/ -v
```

### 性能测试
```bash
cd backend
locust -f locustfile.py
```

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t star-office-ui .

# 运行容器
docker run -d \
  --name star-office-ui \
  -p 5000:5000 \
  -e DATABASE_PATH=/data/github-collab.db \
  --restart unless-stopped \
  star-office-ui
```

## 🔄 CI/CD

项目包含完整的 CI/CD 流水线：
- 代码质量检查（flake8, black, mypy）
- 单元测试（pytest + coverage）
- 性能测试（locust）
- Docker 镜像构建
- 自动部署

## 📝 贡献

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## 🔒 安全

发现安全漏洞？请阅读 [SECURITY.md](SECURITY.md) 了解如何报告。

## 📄 许可证

MIT License

## 🤝 社区

- GitHub Issues: [报告问题](https://github.com/wljmmx/star-office-ui/issues)
- 讨论：[加入讨论](https://github.com/wljmmx/star-office-ui/discussions)

---

Made with ❤️ by Star Team
