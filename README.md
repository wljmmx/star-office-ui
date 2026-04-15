# Star Office UI - GitHub 协作机器人界面

> 一个现代化的 AI 代理协作管理界面，用于监控和管理 GitHub 协作机器人的状态、任务和资源配置。

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [安装和运行](#安装和运行)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [贡献指南](#贡献指南)

---

## 项目简介

Star Office UI 是一个专为 GitHub 协作机器人设计的可视化管理系统。它提供了一个直观的界面来监控和管理多个 AI 代理的状态、任务分配和环境配置。

### 核心目标

- **实时监控**：通过 WebSocket 实现代理状态的实时同步
- **任务管理**：支持任务列表、优先级分配和进度跟踪
- **环境配置**：灵活的环境主题和布局配置
- **头像系统**：支持多种风格的代理头像展示

### 适用场景

- AI 编程团队协作管理
- 多代理任务分配和监控
- 自动化工作流程可视化
- 开发团队状态看板

---

## 功能特性

### 1. 代理管理

实时监控和管理所有 AI 代理的状态：

- **状态追踪**：支持 `idle`、`writing`、`researching`、`executing`、`syncing`、`error` 等多种状态
- **区域映射**：自动将代理分配到不同区域（休息区、工作区、错误区）
- **任务关联**：显示代理当前处理的任务详情
- **实时同步**：通过 WebSocket 实现状态实时更新

```python
# 代理状态示例
{
    "agentId": "123",
    "name": "CodeAgent",
    "type": "dev",
    "state": "writing",
    "detail": "正在处理：优化数据库查询",
    "area": "writing",
    "task_id": "task-456",
    "task_name": "优化数据库查询"
}
```

### 2. 任务管理

完整的任务生命周期管理：

- **任务列表**：支持多列表管理（待处理、进行中、已完成）
- **任务分配**：将任务分配给特定代理
- **优先级设置**：1-10 级优先级
- **清单功能**：支持任务子项清单
- **进度跟踪**：实时更新任务状态

```python
# 任务示例
{
    "taskId": "task-456",
    "name": "优化数据库查询",
    "description": "优化慢查询，提升性能",
    "status": "in_progress",
    "assigned_agent": "agent-123",
    "priority": 8,
    "list_id": "in_progress",
    "checklist": [
        {"id": "item-1", "name": "分析慢查询", "completed": True},
        {"id": "item-2", "name": "添加索引", "completed": False}
    ]
}
```

### 3. 环境配置

灵活的环境和主题配置：

- **多主题支持**：默认主题、暗色主题、亮色主题等
- **背景定制**：支持自定义背景图片
- **布局配置**：JSON 格式的布局配置
- **工位管理**：为代理分配虚拟工位

```python
# 环境配置示例
{
    "id": "default",
    "name": "默认环境",
    "theme": "default",
    "background_image": "/static/bg-office.jpg",
    "layout_config": {
        "columns": 3,
        "card_size": "medium"
    },
    "settings": {
        "auto_refresh": true,
        "refresh_interval": 5
    }
}
```

### 4. 头像系统

多种风格的代理头像：

- **像素风格**：简单像素化角色
- **表情符号**：使用 emoji 作为头像
- **图片头像**：自定义图片
- **3D 模型**：3D 角色模型（预留）

```python
# 头像配置示例
{
    "avatar_type": "pixel",
    "avatar_data": "8x8 像素数据",
    "pixel_character": "👨‍💻",
    "avatar_url": "https://example.com/avatar.png"
}
```

---

## 技术栈

### 后端

- **Python 3.11+**：主要编程语言
- **Flask 2.3+**：Web 框架
- **Flask-SocketIO 5.3+**：WebSocket 支持
- **SQLite**：轻量级数据库
- **Eventlet 0.33+**：异步网络库

### 前端

- **Vue.js 3**：前端框架
- **Tailwind CSS**：样式框架
- **Socket.IO Client**：WebSocket 客户端

### 开发工具

- **Docker**：容器化部署
- **pytest**：单元测试
- **Black**：代码格式化
- **flake8**：代码风格检查

---

## 项目结构

```
star-office-ui/
├── backend/                    # 后端代码
│   ├── api/                   # API 路由层
│   │   ├── __init__.py        # Blueprint 导出
│   │   ├── agents.py          # 代理管理 API
│   │   ├── tasks.py           # 任务管理 API
│   │   ├── state.py           # 状态同步 API
│   │   ├── assets.py          # 资源管理 API
│   │   ├── config.py          # 配置管理 API
│   │   ├── avatars.py         # 头像管理 API
│   │   ├── environments.py    # 环境配置 API
│   │   └── join_keys.py       # 加入密钥 API
│   ├── models/                # 数据模型层
│   │   └── __init__.py        # Agent, Task 等数据模型
│   ├── services/              # 业务逻辑层
│   │   ├── database_service.py    # 数据库服务
│   │   ├── task_manager.py        # 任务管理器
│   │   └── environment_manager.py # 环境管理器
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── avatar_manager.py  # 头像管理器
│   │   ├── sync_service.py    # 同步服务
│   │   └── json_utils.py      # JSON 工具
│   ├── config/                # 配置管理
│   │   └── __init__.py        # 全局配置
│   ├── main.py                # 应用入口
│   ├── database.py            # 数据库初始化
│   ├── requirements.txt       # 依赖列表
│   └── test_db.py             # 数据库测试
├── frontend/                  # 前端代码
│   ├── index.html            # 主页面
│   └── (Vue.js 应用文件)
├── github-collab/            # GitHub 协作数据库
│   └── github-collab.db      # SQLite 数据库文件
├── .github/                  # GitHub 工作流
│   └── workflows/
├── asset-positions.json      # 资源位置配置
├── asset-defaults.json       # 资源默认配置
├── runtime-config.json       # 运行时配置
├── join-keys.json            # 加入密钥
├── Dockerfile               # Docker 镜像配置
├── docker-compose.yml       # Docker 编排
├── README.md                # 项目说明（本文件）
├── CONTRIBUTING.md          # 贡献指南
└── SECURITY.md              # 安全说明
```

---

## 安装和运行

### 前置要求

- Python 3.11 或更高版本
- pip 包管理器
- Docker（可选，用于容器化部署）

### 方法一：本地运行

#### 1. 克隆仓库

```bash
git clone https://github.com/your-username/star-office-ui.git
cd star-office-ui
```

#### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend/requirements.txt
```

#### 3. 配置数据库

确保数据库文件存在：

```bash
# 数据库默认位置
github-collab/github-collab.db

# 或通过环境变量指定
export GITHUB_COLLAB_DB=/path/to/your/database.db
```

#### 4. 运行应用

```bash
cd backend
python main.py
```

应用将在 `http://localhost:5000` 启动。

### 方法二：Docker 运行

#### 1. 构建镜像

```bash
docker build -t star-office-ui .
```

#### 2. 运行容器

```bash
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/github-collab:/app/github-collab \
  -v $(pwd)/data:/data \
  --name star-office \
  star-office-ui
```

#### 3. 使用 Docker Compose

```bash
docker-compose up -d
```

### 验证安装

访问 `http://localhost:5000` 查看界面，或测试 API：

```bash
# 测试健康检查
curl http://localhost:5000/api/health

# 获取所有代理
curl http://localhost:5000/api/agents

# 获取所有任务
curl http://localhost:5000/api/tasks
```

---

## API 文档

### 基础信息

- **Base URL**: `http://localhost:5000`
- **Authentication**: 暂无（开发中）
- **Response Format**: JSON

### 代理管理 API

#### 获取所有代理

```http
GET /api/agents
```

**响应示例**：

```json
{
  "ok": true,
  "msg": "操作成功",
  "data": {
    "agents": [
      {
        "agentId": "1",
        "name": "CodeAgent",
        "type": "dev",
        "state": "writing",
        "detail": "正在处理：优化数据库查询",
        "area": "writing",
        "task_id": "task-1",
        "task_name": "优化数据库查询"
      }
    ]
  }
}
```

#### 获取单个代理

```http
GET /api/agents/<agent_id>
```

#### 更新代理状态

```http
POST /api/agents/<agent_id>/status
Content-Type: application/json

{
  "state": "writing"
}
```

### 任务管理 API

#### 获取所有任务

```http
GET /api/tasks
```

#### 创建任务

```http
POST /api/tasks
Content-Type: application/json

{
  "name": "新任务",
  "description": "任务描述",
  "status": "pending",
  "priority": 5,
  "assigned_agent": "agent-123",
  "list_id": "todo"
}
```

#### 更新任务

```http
PUT /api/tasks/<task_id>
Content-Type: application/json

{
  "status": "in_progress",
  "assigned_agent": "agent-456"
}
```

#### 删除任务

```http
DELETE /api/tasks/<task_id>
```

#### 获取代理的任务

```http
GET /api/tasks/agent/<agent_id>
```

#### 完成任务清单项

```http
POST /api/tasks/<task_id>/checklist/<item_id>/complete
```

### 头像管理 API

#### 获取所有头像类型

```http
GET /api/avatars
```

#### 获取代理头像

```http
GET /api/avatars/<agent_id>
```

#### 更新代理头像

```http
POST /api/avatars/<agent_id>
Content-Type: application/json

{
  "avatar_type": "pixel",
  "avatar_data": "8x8 像素数据"
}
```

#### 生成默认头像

```http
POST /api/avatars/<agent_id>/generate
```

### 环境配置 API

#### 获取所有环境

```http
GET /api/environments
```

#### 创建环境

```http
POST /api/environments
Content-Type: application/json

{
  "name": "新环境",
  "theme": "dark",
  "background_image": "/static/bg-dark.jpg",
  "layout_config": {
    "columns": 4
  }
}
```

#### 激活环境

```http
POST /api/environments/<env_id>/activate
```

#### 获取所有主题

```http
GET /api/environments/themes
```

### 工位管理 API

#### 获取所有工位

```http
GET /api/environments/desks
```

#### 分配工位

```http
POST /api/environments/desks/<agent_id>
Content-Type: application/json

{
  "desk_number": 1
}
```

#### 解除工位分配

```http
DELETE /api/environments/desks/<agent_id>
```

### 响应状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器错误 |

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_SECRET_KEY` | Flask 密钥 | `star-office-secret-key` |
| `SOUI_HOST` | 服务器监听地址 | `0.0.0.0` |
| `SOUI_PORT` | 服务器端口 | `5000` |
| `SOUI_DEBUG` | 调试模式 | `true` |
| `SOUI_SYNC_INTERVAL` | 同步间隔（秒） | `5` |
| `GITHUB_COLLAB_DB` | 数据库路径 | `github-collab/github-collab.db` |

### 配置文件

#### runtime-config.json

```json
{
  "app_name": "Star Office UI",
  "version": "1.0.0",
  "features": {
    "real_time_sync": true,
    "avatar_system": true,
    "environment_config": true
  }
}
```

#### asset-positions.json

```json
{
  "positions": {
    "writing": { "x": 0, "y": 0 },
    "breakroom": { "x": 100, "y": 100 },
    "error": { "x": 200, "y": 200 }
  }
}
```

### 数据库配置

数据库使用 SQLite，支持以下表：

- `agents`：代理信息
- `tasks`：任务信息
- `environments`：环境配置
- `agent_desks`：工位分配

数据库迁移示例：

```python
# backend/database.py
import sqlite3
from config import Config

def init_database():
    """初始化数据库和表结构。"""
    conn = sqlite3.connect(str(Config.DATABASE_PATH))
    cursor = conn.cursor()
    
    # 创建代理表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'dev',
            status TEXT DEFAULT 'idle',
            capabilities TEXT,
            address TEXT,
            current_task_id TEXT,
            last_heartbeat TEXT,
            avatar_type TEXT DEFAULT 'pixel',
            avatar_data TEXT,
            pixel_character TEXT,
            avatar_url TEXT,
            desk_number INTEGER
        )
    ''')
    
    # 更多表创建...
    
    conn.commit()
    conn.close()
```

---

## 贡献指南

我们欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 快速开始

```bash
# 1. Fork 仓库
git clone https://github.com/YOUR_USERNAME/star-office-ui.git
cd star-office-ui

# 2. 创建分支
git checkout -b feature/your-feature-name

# 3. 安装依赖
pip install -r backend/requirements.txt

# 4. 运行测试
pytest backend/tests/ -v

# 5. 提交更改
git add .
git commit -m "feat: add your feature"

# 6. 推送并创建 Pull Request
git push origin feature/your-feature-name
```

### 开发规范

- **代码风格**：遵循 PEP 8，使用 Black 格式化
- **提交信息**：使用 conventional commits 格式
- **测试覆盖**：保持至少 80% 的代码覆盖率
- **文档**：更新相关文档和注释

### 提交信息格式

```
feat: 新增头像管理功能

- 实现头像 API 路由
- 添加头像管理器
- 支持像素、emoji、图片三种类型
```

### 联系

- 提交 Issue 报告问题
- 创建 Pull Request 贡献代码
- 联系维护者讨论功能

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

感谢所有贡献者和使用者！

---

**Star Office UI** - 让 AI 代理协作更简单 🌟
