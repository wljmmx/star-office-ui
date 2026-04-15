# 部署配置说明

## 挂载映射配置

### 开发环境（docker-compose）

```yaml
volumes:
  # 数据持久化
  - star-office-data:/data
  # 热重载挂载
  - /home/wljmmx/star-office-ui/backend:/app/backend
  - /home/wljmmx/star-office-ui/frontend:/app/frontend
  - /home/wljmmx/.openclaw/skills/github-collab:/app/skills/github-collab
```

### 映射说明

| 主机路径 | 容器路径 | 用途 |
|---------|---------|------|
| `/home/wljmmx/star-office-ui/backend` | `/app/backend` | 后端代码热重载 |
| `/home/wljmmx/star-office-ui/frontend` | `/app/frontend` | 前端代码热重载 |
| `/home/wljmmx/.openclaw/skills/github-collab` | `/app/skills/github-collab` | GitHub Collab 技能数据 |
| `star-office-data` (volume) | `/data` | 数据库持久化 |

### 生产环境部署

生产环境应移除代码挂载，使用镜像内置代码：

```bash
docker run -d \
  --name star-office-ui \
  --restart unless-stopped \
  -p 5000:5000 \
  -e DATABASE_PATH=/data/github-collab.db \
  -e DEBUG=false \
  -e HOST=0.0.0.0 \
  -e PORT=5000 \
  -v star-office-data:/data \
  star-office-ui:latest
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|-------|--------|------|
| `DATABASE_PATH` | `/data/github-collab.db` | 数据库文件路径 |
| `DEBUG` | `true` | 调试模式 |
| `HOST` | `0.0.0.0` | 监听地址 |
| `PORT` | `5000` | 监听端口 |

## 构建与部署

### 开发环境

```bash
# 使用 docker-compose 启动（支持热重载）
docker-compose up -d

# 查看日志
docker-compose logs -f star-office-ui
```

### 生产环境

```bash
# 构建镜像
docker build -t star-office-ui:latest .

# 运行容器
docker run -d \
  --name star-office-ui \
  --restart unless-stopped \
  -p 5000:5000 \
  -e DATABASE_PATH=/data/github-collab.db \
  -e DEBUG=false \
  -v star-office-data:/data \
  star-office-ui:latest
```

## 注意事项

1. **开发环境**：使用 docker-compose，挂载本地代码实现热重载
2. **生产环境**：使用 docker run，不挂载代码，使用镜像内置版本
3. **数据持久化**：无论哪种环境，都需要挂载 `star-office-data` volume 保证数据库不丢失
4. **路径一致性**：确保挂载路径与 Dockerfile 中的 WORKDIR 一致
