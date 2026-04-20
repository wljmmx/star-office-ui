# Star Office UI - 部署指南

## 📋 目录

- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [本地开发](#本地开发)
- [生产部署](#生产部署)
- [Docker 部署](#docker-部署)
- [安全配置](#安全配置)

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/wljmmx/star-office-ui.git
cd star-office-ui
```

### 2. 初始化环境

```bash
# 运行环境配置脚本
./setup-env.sh
```

### 3. 安装依赖

```bash
# 安装 Python 依赖
pip install -r backend/requirements.txt

# 安装前端依赖（Vue 3 版本）
cd frontend-v3
npm install
```

### 4. 初始化数据库

```bash
python backend/init_db.py
```

### 5. 启动服务

```bash
# 启动后端
python backend/main.py

# 启动前端（Vue 3）
cd frontend-v3
npm run dev
```

访问：http://localhost:5000

---

## 环境配置

### 环境变量说明

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `FLASK_SECRET_KEY` | Flask 密钥（32+ 字符） | - | ✅ |
| `JWT_SECRET_KEY` | JWT 密钥（32+ 字符） | - | ✅ |
| `SOUI_DEBUG` | 调试模式 | `false` | ❌ |
| `SOUI_HOST` | 服务器地址 | `0.0.0.0` | ❌ |
| `SOUI_PORT` | 服务器端口 | `5000` | ❌ |
| `SOUI_CORS_ORIGINS` | CORS 允许的域名 | - | ✅(生产) |
| `SOUI_SYNC_INTERVAL` | WebSocket 同步间隔 | `5` | ❌ |
| `SOUI_COOKIE_SECURE` | Cookie 安全标志 | `false` | ❌ |
| `SOUI_LOG_LEVEL` | 日志级别 | `INFO` | ❌ |

### 配置示例

**开发环境 (.env.development)**:
```bash
FLASK_SECRET_KEY=dev-secret-key-min-32-chars-with-special!
JWT_SECRET_KEY=dev-jwt-secret-key-min-32-chars-with-special!
SOUI_DEBUG=true
SOUI_HOST=127.0.0.1
SOUI_PORT=5000
SOUI_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SOUI_COOKIE_SECURE=false
SOUI_LOG_LEVEL=DEBUG
```

**生产环境 (.env.production)**:
```bash
FLASK_SECRET_KEY=<生成的安全密钥>
JWT_SECRET_KEY=<生成的安全密钥>
SOUI_DEBUG=false
SOUI_HOST=0.0.0.0
SOUI_PORT=5000
SOUI_CORS_ORIGINS=https://yourdomain.com
SOUI_COOKIE_SECURE=true
SOUI_LOG_LEVEL=INFO
```

---

## 本地开发

### 启动开发服务器

```bash
# 1. 配置环境变量
source .env

# 2. 启动后端（热重载）
python backend/main.py

# 3. 启动前端（Vue 3）
cd frontend-v3
npm run dev
```

### 开发模式特性

- ✅ 代码热重载
- ✅ 详细日志输出
- ✅ 自动 CORS 配置
- ✅ 开发工具支持

---

## 生产部署

### 1. 安全配置

```bash
# 生成安全密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 配置环境变量
export FLASK_SECRET_KEY=<生成的密钥>
export JWT_SECRET_KEY=<生成的密钥>
export SOUI_DEBUG=false
export SOUI_COOKIE_SECURE=true
```

### 2. 使用 Gunicorn 部署

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn -w 4 -b 0.0.0.0:5000 backend.main:app
```

### 3. Nginx 反向代理

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. HTTPS 配置

```bash
# 使用 Let's Encrypt
sudo certbot --nginx -d yourdomain.com
```

---

## Docker 部署

### 1. 构建镜像

```bash
# 构建 Docker 镜像
docker build -t star-office-ui .

# 或使用 Docker Compose
docker-compose build
```

### 2. 启动容器

```bash
# 使用 Docker
docker run -d \
  -p 5000:5000 \
  -e FLASK_SECRET_KEY=<密钥> \
  -e JWT_SECRET_KEY=<密钥> \
  -e SOUI_DEBUG=false \
  --name star-office-ui \
  star-office-ui

# 使用 Docker Compose
docker-compose up -d
```

### 3. 数据持久化

```bash
# 创建数据目录
mkdir -p ./data

# 挂载数据卷
docker run -d \
  -p 5000:5000 \
  -v ./data:/data \
  --name star-office-ui \
  star-office-ui
```

### 4. 生产环境 Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SOUI_DEBUG=false
      - SOUI_COOKIE_SECURE=true
    volumes:
      - star-office-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  star-office-data:
    driver: local
```

---

## 安全配置

### 1. 密钥管理

```bash
# ❌ 错误：硬编码密钥
FLASK_SECRET_KEY='hardcoded-key'

# ✅ 正确：从环境变量读取
FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
```

### 2. CORS 配置

```bash
# ❌ 错误：通配符
SOUI_CORS_ORIGINS=*

# ✅ 正确：明确域名
SOUI_CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### 3. 安全头配置

在 `backend/main.py` 中添加：

```python
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### 4. 日志安全

```python
# 过滤敏感信息
from backend.utils.logger import filter_sensitive_headers

safe_headers = filter_sensitive_headers(request.headers)
logger.info("request_received", headers=safe_headers)
```

---

## 故障排查

### 问题 1: 密钥验证失败

**错误**: `ConfigError: SECRET_KEY must be at least 32 characters`

**解决**: 生成符合要求的密钥
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 问题 2: CORS 错误

**错误**: `No 'Access-Control-Allow-Origin' header`

**解决**: 配置正确的 CORS 域名
```bash
SOUI_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 问题 3: 数据库连接失败

**错误**: `sqlite3.OperationalError: no such table`

**解决**: 初始化数据库
```bash
python backend/init_db.py
```

### 问题 4: WebSocket 连接失败

**错误**: `WebSocket connection failed`

**解决**: 检查 Nginx 配置
```nginx
location /socket.io {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 性能优化

### 1. 数据库优化

```python
# 启用 WAL 模式
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;
```

### 2. 缓存配置

```python
# 使用 Redis 缓存
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})
```

### 3. 静态文件优化

```python
# 使用 CDN 或 Nginx 服务静态文件
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 年
```

---

## 监控与日志

### 1. 应用监控

```bash
# 查看日志
docker logs -f star-office-ui

# 查看实时日志
tail -f /var/log/star-office/app.log
```

### 2. 健康检查

```bash
# 检查 API 健康状态
curl http://localhost:5000/api/health

# 检查 WebSocket 状态
curl -N http://localhost:5000/socket.io/
```

### 3. 性能监控

```python
# 使用 Prometheus 监控
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Star Office UI', version='1.0.0')
```

---

## 更新与维护

### 1. 更新代码

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

### 2. 备份数据

```bash
# 备份数据库
cp /data/github-collab.db /backup/github-collab.db.$(date +%Y%m%d)

# 备份配置文件
tar -czf backup-$(date +%Y%m%d).tar.gz .env data/
```

---

## 支持

- 📧 技术支持：support@example.com
- 📚 文档：https://docs.staroffice.ui
- 🐛 问题反馈：https://github.com/wljmmx/star-office-ui/issues

---

**最后更新**: 2026-04-20
