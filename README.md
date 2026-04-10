# Star Office UI

基于 github-collab 数据库的 Agent 状态可视化界面。

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
| type | TEXT | Agent 类型 (manager/coder/tester) |
| status | TEXT | 状态 (idle/active/completed) |
| current_task_id | INTEGER | 当前任务 ID |
| last_heartbeat | TEXT | 最后心跳时间 |
| capabilities | TEXT | 能力描述 |
| address | TEXT | 通信地址 |

#### tasks 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 项目 ID |
| name | TEXT | 任务名称 |
| description | TEXT | 任务描述 |
| status | TEXT | 状态 (pending/active/completed) |
| assigned_agent | INTEGER | 分配给哪个 Agent |
| priority | INTEGER | 优先级 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |
| completed_at | TEXT | 完成时间 |

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

### GET /api/agents
获取所有 Agent 列表

### GET /api/agents/<id>
获取指定 Agent 详情

### GET /api/tasks
获取所有任务列表

### GET /api/state
获取当前办公室状态

## 测试

```bash
cd backend
python3 test_integration.py
```

## 依赖

- Python 3.11+
- sqlite3
- Flask (可选，用于 API 服务)
- Flask-SocketIO (可选，用于实时通信)

## 配置

设置环境变量：
```bash
export GITHUB_COLLAB_DB=/path/to/github-collab.db
```

## 注意事项

1. 数据库由 github-collab 项目管理，star-office-ui 只读
2. Agent 状态通过 github-collab 的 status 字段转换
3. 任务信息通过 LEFT JOIN 关联查询
4. 缺少字段（如 pixel_character）返回 null
