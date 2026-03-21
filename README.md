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
├── docker-compose.yml    # Docker Compose
└── README.md
```

## 🎯 核心功能

### 1. 多 Agent 协作
- **DeployBot**: 部署自动化
- **CoderBot**: 代码开发
- **TestMaster**: 测试验证
- **Star**: 主协调器

### 2. 实时状态同步
- WebSocket 实时推送
- 定时轮询备份
- 状态可视化展示

### 3. 任务管理
- 任务分配
- 进度追踪
- 状态监控

### 4. 性能优化
- LRU 缓存
- 数据库连接池
- 异步任务队列
- 性能监控

## 🔧 CI/CD 流水线

### 自动测试
```yaml
- 代码质量检查 (flake8, black, mypy)
- 单元测试 (pytest + coverage)
- 性能测试 (locust)
```

### 自动部署
```yaml
- 构建 Docker 镜像
- 推送到 Docker Hub
- 部署到生产环境
```

## 📊 性能测试

### 运行 Locust 测试
```bash
# 安装 Locust
pip install locust

# 启动测试
locust -f backend/locustfile.py --host=http://localhost:5000

# 访问测试界面
http://localhost:8089
```

### 性能指标
- **并发用户**: 100
- **请求/秒**: 500+
- **平均响应**: < 50ms
- **P99 延迟**: < 200ms

## 🎨 美术资源

### 头像系统
- 使用 DiceBear API 生成动态头像
- 支持自定义种子和颜色
- 自动映射 Agent 角色

### 主题配色
- **默认主题**: 深色模式
- **浅色主题**: 明亮模式
- **自定义主题**: 支持动态切换

### 区域布局
- **Breakroom**: 休息区
- **Writing**: 工作区
- **Meeting**: 会议区
- **Error**: 错误区

## 🛠️ 开发指南

### 添加新 API
```python
from flask import Blueprint, jsonify
from backend.services.database_service import get_db_service

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    db = get_db_service()
    data = db.get_data()
    return jsonify(data)
```

### 添加新模型
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class NewModel:
    id: str
    name: str
    status: str
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status
        }
```

### 性能优化
```python
from backend.optimizations import cached, async_task, monitor_time

@cached(ttl=300)
def expensive_operation():
    # 缓存结果 5 分钟
    pass

@async_task
def background_job():
    # 异步执行
    pass

@monitor_time("my_function")
def my_function():
    # 自动记录性能
    pass
```

## 📝 配置说明

### 环境变量
```bash
DATABASE_PATH=/data/github-collab.db
DEBUG=true
HOST=0.0.0.0
PORT=5000
SYNC_INTERVAL=5
```

### 数据库配置
- 默认使用 SQLite
- 支持 PostgreSQL/MySQL
- 自动创建表结构

## 🐛 故障排查

### 常见问题

**Q: Flask 未安装？**
```bash
pip install flask flask-socketio
```

**Q: 数据库连接失败？**
```bash
# 检查数据库路径
ls -la /workspace/skills/github-collab/github-collab.db
```

**Q: 端口被占用？**
```bash
# 修改端口
export PORT=8080
```

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Star Office UI** - 让协作更高效 ⭐
