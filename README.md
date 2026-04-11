# Star Office UI 🏢

基于 github-collab 数据库的 Agent 状态可视化界面，支持独立形象、办公室环境和任务列表管理。

## ✨ 核心特性

- 🎨 **Agent 形象系统** - 4 种形象类型 (emoji/pixel/image/3d)，每个 Agent 独立形象
- 🏢 **办公室环境系统** - 7 种环境 (office/breakroom/meeting 等)，自动状态映射
- 📋 **独立任务列表** - 每个 Agent 独立任务队列，优先级调度
- 🔄 **实时状态同步** - WebSocket 实时通信，状态自动更新
- 🎯 **智能工位分配** - 4 种分配策略 (first/round-robin/nearest/smart)

## 数据库适配

### 数据库路径
- 主路径：`/workspace/star-office-ui/github-collab/github-collab.db`
- 备用路径：`/workspace/skills/github-collab/github-collab.db`

### 表结构

#### agents 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | Agent 名称 |
| type | TEXT | Agent 类型 (manager/coder/tester/architect) |
| status | TEXT | 状态 (idle/active/completed) |
| current_task_id | INTEGER | 当前任务 ID |
| last_heartbeat | TEXT | 最后心跳时间 |
| capabilities | TEXT | 能力描述 |
| address | TEXT | 通信地址 |
| avatar_type | TEXT | 形象类型 (emoji/pixel/image/3d) |
| avatar_data | TEXT | 形象数据 (JSON) |
| pixel_character | TEXT | 像素角色标识 |
| avatar_url | TEXT | 头像 URL |

#### tasks 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 项目 ID |
| name | TEXT | 任务名称 |
| description | TEXT | 任务描述 |
| status | TEXT | 状态 (pending/active/completed) |
| assigned_agent | INTEGER | 分配给哪个 Agent |
| priority | INTEGER | 优先级 (1-10) |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |
| completed_at | TEXT | 完成时间 |
| list_id | TEXT | 任务列表 ID |
| position | INTEGER | 任务位置 |
| checklist | TEXT | 检查清单 (JSON) |

#### environments 表 (新增)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 环境 ID |
| name | TEXT | 环境名称 |
| description | TEXT | 环境描述 |
| theme | TEXT | 主题 |
| background_image | TEXT | 背景图片 |
| layout_config | TEXT | 布局配置 (JSON) |
| settings | TEXT | 设置 (JSON) |
| is_active | INTEGER | 是否激活 |

#### agent_desks 表 (新增)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 主键 |
| agent_id | TEXT | Agent ID |
| desk_number | INTEGER | 工位编号 |
| position_x | REAL | X 坐标 |
| position_y | REAL | Y 坐标 |

## 状态映射

### status → state
- `idle` → `idle`
- `active` → `writing`
- `working` → `writing`
- `pending` → `idle`
- `completed` → `idle`
- `failed` → `error`

### state → area
- `idle` → `breakroom`
- `writing/researching/executing/syncing` → `writing`
- `error` → `error`

## API 端点

### 基础端点

#### GET /api/agents
获取所有 Agent 列表（包含形象信息）

#### GET /api/agents/<id>
获取指定 Agent 详情

#### GET /api/tasks
获取所有任务列表

#### GET /api/state
获取当前办公室状态

### 形象系统 API

#### GET /api/avatars
获取所有可用的形象类型

#### GET /api/avatars/<agent_id>
获取指定 Agent 的形象

#### POST /api/avatars/<agent_id>
更新 Agent 形象

#### POST /api/avatars/generate/<agent_id>
为 Agent 生成默认形象

### 环境系统 API

#### GET /api/environments
获取所有环境列表

#### GET /api/environments/<env_id>
获取指定环境详情

#### POST /api/environments
创建新环境

#### PUT /api/environments/<env_id>
更新环境配置

#### POST /api/environments/<env_id>/activate
激活环境（其他环境自动停用）

#### GET /api/environments/themes
获取所有可用主题

#### GET /api/environments/desks
获取所有工位分配

#### POST /api/environments/desks/<agent_id>
为 Agent 分配工位

### 任务列表 API

#### GET /api/tasks/<agent_id>
获取指定 Agent 的任务列表

#### POST /api/tasks
创建新任务

#### PUT /api/tasks/<task_id>
更新任务

#### DELETE /api/tasks/<task_id>
删除任务

#### POST /api/tasks/<task_id>/start
开始任务

#### POST /api/tasks/<task_id>/complete
完成任务

#### POST /api/tasks/<task_id>/fail
标记任务失败

#### POST /api/tasks/<task_id>/retry
重试任务

## 测试

### 集成测试

```bash
cd backend
python3 test_integration.py
```

### 数据库检查

```bash
python3 check_db.py
python3 check_schema.py
```

### 验证安装

```bash
python3 -c "from utils.avatar_manager import AvatarManager; print('Avatar OK')"
python3 -c "from services.environment_manager import EnvironmentManager; print('Environment OK')"
python3 -c "from services.task_manager import TaskManager; print('Task OK')"
```

## 快速开始

### 1. 安装依赖

```bash
cd ~/star-office-ui/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 运行数据库迁移

```bash
python backend/migrations/001_add_avatar_and_environment.py
```

### 3. 启动服务

```bash
python main.py
```

### 4. 访问界面

打开浏览器访问：`http://localhost:5000`

## 依赖

- Python 3.11+
- sqlite3
- Flask>=2.3.0
- Flask-SocketIO>=5.3.0
- python-socketio>=5.10.0
- eventlet>=0.33.0
- python-engineio>=4.8.0

## 配置

设置环境变量：
```bash
export GITHUB_COLLAB_DB=/path/to/github-collab.db
```

或使用默认路径：
- `/workspace/star-office-ui/github-collab/github-collab.db`
- `/workspace/skills/github-collab/github-collab.db`

## 使用示例

### 为 Agent 生成形象

```bash
curl -X POST http://localhost:5000/api/avatars/generate/agent-1
```

### 分配工位

```bash
curl -X POST http://localhost:5000/api/environments/desks/agent-1 \
  -H "Content-Type: application/json" \
  -d '{"desk_number": 101}'
```

### 创建任务

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "开发新功能",
    "description": "实现用户登录功能",
    "assigned_agent": "agent-1",
    "priority": 8
  }'
```

## 技术架构

- **后端**: Flask + Flask-SocketIO
- **前端**: HTML5 + CSS3 + JavaScript
- **数据库**: SQLite (github-collab.db)
- **实时通信**: WebSocket

## 核心模块

- `avatar_manager.py` - 形象管理
- `environment_manager.py` - 环境管理
- `task_manager.py` - 任务管理
- `database_service.py` - 数据库服务

## 注意事项

1. 数据库由 github-collab 项目管理，star-office-ui 只读
2. Agent 状态通过 github-collab 的 status 字段转换
3. 任务信息通过 LEFT JOIN 关联查询
4. 缺少字段（如 pixel_character）返回 null
5. 首次运行需要执行数据库迁移脚本
6. 形象数据支持自定义，但需符合 JSON 格式

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
