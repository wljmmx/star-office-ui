# Star Office UI - 部署指南

本文档提供 Star Office UI 的完整部署说明，包括本地开发、Docker 部署和生产环境配置。

## 📋 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [本地开发部署](#本地开发部署)
- [Docker 部署](#docker-部署)
- [生产环境部署](#生产环境部署)
- [配置说明](#配置说明)
- [故障排查](#故障排查)

---

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/star-office-ui.git
cd star-office-ui

# 2. 配置环境变量
cp .env.template .env
# 编辑 .env 文件，设置必要的配置

# 3. 启动服务（Docker）
docker-compose up -d

# 4. 访问应用
# http://localhost:5000
```

---

## 环境要求

### 系统要求
- **操作系统**: Linux, macOS, Windows (WSL2)
- **内存**: 最小 512MB，推荐 1GB+
- **磁盘**: 最小 100MB 可用空间
- **网络**: 稳定的网络连接

### 依赖项

#### Docker 部署（推荐）
- Docker Engine 20.10+
- Docker Compose 2.0+

#### 本地开发
- Python 3.11+
- pip 21.0+
- Node.js 16+ (可选，用于前端开发)

---

## 本地开发部署

### 1. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend/requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑配置
nano .env  # 或使用其他编辑器
```

### 3. 启动服务

```bash
# 确保数据库存在
ls skills/github-collab/github-collab.db

# 启动 Flask 应用
cd backend
python main.py
```

### 4. 访问应用

打开浏览器访问：`http://localhost:5000`

---

## Docker 部署

### 基本部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用自定义配置

```bash
# 使用自定义环境变量
export FLASK_SECRET_KEY="your-secret-key"
export SOUI_CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"

docker-compose up -d
```

### 数据库持久化

Docker Compose 已配置命名卷 `star-office-data`，数据会持久化存储：

```bash
# 查看卷位置
docker volume inspect star-office-star-office-data

# 备份数据
docker run --rm \
  -v star-office-star-office-data:/data:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/star-office-backup.tar.gz /data
```

---

## 生产环境部署

### 1. 安全配置

```bash
# 生成安全的密钥
python -c "import secrets; print(secrets.token_hex(32))"

# 在 .env 中设置
FLASK_SECRET_KEY="生成的密钥"
SOUI_DEBUG=false
SOUI_COOKIE_SECURE=true
```

### 2. CORS 配置

```bash
# 仅允许特定域名
SOUI_CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### 3. 使用 Nginx 反向代理

#### 启用 Nginx

1. 编辑 `docker-compose.yml`，取消 Nginx 服务的注释
2. 配置 `nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream star_office {
        server star-office-ui:5000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://star_office;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static {
            proxy_pass http://star_office/static;
            add_header Cache-Control "public, max-age=3600";
        }
    }
}
```

#### 配置 SSL（可选）

```bash
# 放置证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/selfsigned.key \
  -out ssl/selfsigned.crt

# 更新 nginx.conf 添加 SSL 配置
```

### 4. 启动生产环境

```bash
# 构建生产镜像
docker-compose build

# 启动服务
docker-compose -f docker-compose.yml up -d

# 验证健康检查
docker-compose ps
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `FLASK_SECRET_KEY` | Flask 会话密钥 | 无 | ✅ |
| `SOUI_DEBUG` | 调试模式 | `false` | ❌ |
| `SOUI_HOST` | 监听地址 | `127.0.0.1` | ❌ |
| `SOUI_PORT` | 监听端口 | `5000` | ❌ |
| `SOUI_CORS_ORIGINS` | 允许的 CORS 源 | `http://localhost:3000` | ❌ |
| `SOUI_COOKIE_SECURE` | Cookie Secure 标志 | `false` | ❌ |
| `SOUI_SYNC_INTERVAL` | 同步间隔（秒） | `5` | ❌ |

### 端口配置

| 端口 | 用途 | 协议 |
|------|------|------|
| 5000 | Flask 应用 | HTTP/WebSocket |
| 80 | Nginx HTTP | HTTP |
| 443 | Nginx HTTPS | HTTPS |

### 数据目录

| 路径 | 说明 |
|------|------|
| `/data` | 数据库和持久化数据 |
| `/app` | 应用代码（容器内） |

---

## 故障排查

### 常见问题

#### 1. 容器无法启动

```bash
# 查看日志
docker-compose logs star-office-ui

# 检查端口占用
netstat -tlnp | grep 5000

# 检查卷权限
ls -la /var/lib/docker/volumes/
```

#### 2. 数据库连接失败

```bash
# 验证数据库文件存在
ls -la skills/github-collab/github-collab.db

# 检查数据库权限
docker exec star-office-ui ls -la /data/
```

#### 3. WebSocket 连接失败

```bash
# 检查 CORS 配置
grep CORS .env

# 验证 SocketIO 端点
curl -i http://localhost:5000/socket.io/?EIO=4&transport=websocket
```

#### 4. 内存不足

```bash
# 调整资源限制
# 编辑 docker-compose.yml，增加内存限制
deploy:
  resources:
    limits:
      memory: 1G
```

### 日志查看

```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f star-office-ui

# 查看最近 100 行
docker-compose logs --tail=100 star-office-ui
```

### 健康检查

```bash
# 检查容器状态
docker-compose ps

# 测试健康端点
curl http://localhost:5000/api/health

# 查看容器健康状态
docker inspect --format='{{.State.Health.Status}}' star-office-ui
```

---

## 性能优化

### 1. 调整同步间隔

```bash
# 降低同步频率以减少资源消耗
SOUI_SYNC_INTERVAL=10
```

### 2. 启用 Gunicorn（生产推荐）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动命令
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 3. 数据库优化

```bash
# 在数据库连接中启用 WAL 模式
PRAGMA journal_mode=WAL;
```

---

## 更新和维护

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 重启服务
docker-compose up -d
```

### 备份数据

```bash
# 备份数据库
docker run --rm \
  -v star-office-star-office-data:/data:ro \
  -v $(pwd)/backups:/backup \
  alpine cp /data/github-collab.db /backup/
```

### 恢复数据

```bash
# 停止服务
docker-compose stop

# 恢复数据库
docker run --rm \
  -v star-office-star-office-data:/data:rw \
  -v $(pwd)/backups:/backup \
  alpine cp /backup/github-collab.db /data/

# 启动服务
docker-compose start
```

---

## 支持

- **文档**: https://github.com/your-username/star-office-ui/wiki
- **问题反馈**: https://github.com/your-username/star-office-ui/issues
- **安全报告**: 参见 SECURITY.md

---

*最后更新：2024 年 4 月*
