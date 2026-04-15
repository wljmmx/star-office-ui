# 数据库结构对比报告

## github-collab 项目数据库结构

### 1. projects 表
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    github_url TEXT UNIQUE NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    work_dir TEXT
);
```

### 2. agents 表
```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    pixel_character TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'dev',
    status TEXT DEFAULT 'idle',
    current_task_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (current_task_id) REFERENCES tasks(id)
);
```

### 3. tasks 表
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    assigned_to TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (assigned_to) REFERENCES agents(id)
);
```

### 4. 其他表
- `agent_task_queue` - Agent 任务队列
- `task_logs` - 任务日志
- `task_assignments` - 任务分配
- `task_history` - 任务历史
- `task_dependencies` - 任务依赖

---

## star-office-ui 项目模型对比

### ✅ 已匹配

| 表名 | 字段 | 状态 |
|------|------|------|
| **projects** | id, name, github_url, description, status, created_at, updated_at, work_dir | ✅ 完全匹配 |
| **agents** | id, name, pixel_character, avatar_url, role, status, current_task_id, created_at, updated_at | ✅ 完全匹配 |
| **tasks** | id, title, status, progress, assigned_to, created_at, updated_at | ✅ 完全匹配 |

### ⚠️ 注意事项

1. **projects 表**
   - ✅ 所有字段已正确映射
   - ✅ `work_dir` 字段已包含

2. **agents 表**
   - ✅ 所有字段已正确映射
   - ⚠️ 模型中新增字段（`project_id`, `project_name`, `project_url`, `parent_agent_id`, `subagents`）是计算字段，不直接对应数据库列

3. **tasks 表**
   - ✅ 所有字段已正确映射
   - ⚠️ 模型中新增字段（`project_id`, `project_name`, `project_url`）是计算字段，需要通过关联查询获取

---

## 数据关联关系

### 当前状态
- `agents.current_task_id` → `tasks.id` ✅
- `tasks.assigned_to` → `agents.id` ✅

### 缺失关联
- ❌ `tasks` 表没有 `project_id` 字段
- ❌ `agents` 表没有 `project_id` 字段

### 建议改进
如果需要支持任务/Agent 与项目的关联，需要：
1. 在 `tasks` 表添加 `project_id` 字段
2. 在 `agents` 表添加 `current_project_id` 字段
3. 或者通过 `task_assignments` 表间接关联

---

## 结论

✅ **数据库结构基本一致**

- `projects`、`agents`、`tasks` 三个核心表的字段完全匹配
- 模型中的额外字段（`project_id`, `project_name`, `project_url`）需要通过数据库关联查询获取
- 当前实现通过 `load_all_agents()` 中的多表查询来补充项目信息

**建议**：如果项目关联是核心需求，考虑在数据库层面添加外键关联。
