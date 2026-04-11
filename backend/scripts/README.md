# 管理脚本

本目录包含 Star Office UI 后端的管理脚本，用于数据库初始化、备份、清理等运维操作。

## 脚本列表

### init_db.py

**功能**: 初始化数据库，创建表结构并插入示例数据

**用途**:
- 创建 `agents` 表（存储智能体信息）
- 创建 `tasks` 表（存储任务信息）
- 插入 4 个示例智能体
- 插入 3 个示例任务

**使用方法**:
```bash
python3 scripts/init_db.py
```

**输出示例**:
```
✅ Database initialized: /path/to/github-collab.db
   - Created tables: agents, tasks
   - Inserted 4 agents
   - Inserted 3 tasks
```

**注意事项**:
- 数据库文件保存在 `../../skills/github-collab/github-collab.db`
- 如果数据库已存在，会覆盖示例数据
- 首次运行会自动创建数据库目录

## 目录结构

```
scripts/
├── README.md              # 本文件
├── init_db.py            # 数据库初始化脚本
└── archived/             # 归档脚本目录
    └── optimizations_archived.py
```

## 依赖

- Python 3.8+
- sqlite3 (Python 标准库)

## 贡献

添加新脚本时请：
1. 在脚本顶部添加清晰的文档字符串
2. 在本 README 中更新脚本列表
3. 确保脚本有适当的错误处理
4. 添加 `if __name__ == "__main__":` 入口点
