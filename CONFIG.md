# Star Office UI - 配置说明

本文档详细说明 Star Office UI 的所有配置选项、环境变量和最佳实践。

## 📋 目录

- [配置概览](#配置概览)
- [环境变量](#环境变量)
- [安全配置](#安全配置)
- [网络配置](#网络配置)
- [数据库配置](#数据库配置)
- [性能调优](#性能调优)
- [Docker 配置](#docker-配置)
- [配置验证](#配置验证)

---

## 配置概览

Star Office UI 支持多种配置方式：

1. **环境变量** - 通过 `.env` 文件或系统环境变量
2. **Docker Compose** - 通过 `docker-compose.yml` 的 `environment` 部分
3. **代码配置** - `backend/config/__init__.py` 中的默认值

配置优先级（从高到低）：
1. 容器环境变量
2. `.env` 文件
3. 系统环境变量
4. 代码默认值

---

## 环境变量

### 必需配置

#### `FLASK_SECRET_KEY`

Flask 会话管理和安全加密的密钥。

**要求**：
- 至少 32 个字符
- 包含大写字母、小写字母、数字和特殊字符
- 每个环境使用唯一密钥

**生成方法**：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**示例**：
```bash
FLASK_SECRET_KEY="aB3$dE6#gI9*jL2@mN5+pQ8-rS1=tU4!vW7^x"
```

---

### 服务器配置

#### `SOUI_DEBUG`

启用/禁用调试模式。

- **类型**: boolean
- **默认值**: `false`
- **选项**: `true`, `false`

**影响**：
- `true`: 启用 Flask 调试器，自动重载，详细错误页面
- `false`: 生产模式，无调试器

**安全警告**: 生产环境必须设置为 `false`

#### `SOUI_HOST`

服务器监听的 IP 地址。

- **类型**: string
- **默认值**: `127.0.0.1` (调试模式：`0.0.0.0`)
- **选项**: IP 地址

**常见值**：
- `127.0.0.1` - 仅本地访问
- `0.0.0.0` - 所有网络接口（Docker/生产）
- `::1` - IPv6 本地

#### `SOUI_PORT`

服务器监听的端口号。

- **类型**: integer
- **默认值**: `5000`
- **范围**: 1-65535

**注意**: 确保端口未被占用

---

### CORS 配置

#### `SOUI_CORS_ORIGINS`

允许跨域请求的源列表。

- **类型**: string (逗号分隔)
- **默认值**: `http://localhost:3000`
- **格式**: `http://domain1.com,https://domain2.com:8080`

**示例**：
```bash
# 开发环境
SOUI_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 生产环境
SOUI_CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

**安全注意**：
- 生产环境不要使用通配符 `*`
- 仅添加必要的域名
- 包含协议（http/https）

---

### Session/Cookie 配置

#### `SOUI_COOKIE_SECURE`

是否设置 Cookie 的 Secure 标志。

- **类型**: boolean
- **默认值**: `false`
- **推荐**: HTTPS 环境设为 `true`

**影响**：
- `true`: Cookie 仅通过 HTTPS 传输
- `false`: Cookie 可通过 HTTP 传输

---

### 同步配置

#### `SOUI_SYNC_INTERVAL`

后台同步服务的间隔时间（秒）。

- **类型**: integer
- **默认值**: `5`
- **范围**: 1-60

**性能影响**：
- 更短间隔 = 更实时但更高资源消耗
- 更长间隔 = 延迟更高但资源消耗更低

**推荐值**：
- 开发：5 秒
- 生产：10-30 秒
- 低资源环境：60 秒

---

## 安全配置

### 密钥管理

#### 生成安全的 FLASK_SECRET_KEY

```bash
# 方法 1: Python
python -c "import secrets; print(secrets.token_hex(32))"

# 方法 2: OpenSSL
openssl rand -hex 32

# 方法 3: /dev/urandom
head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'
```

#### 密钥强度要求

| 要求 | 说明 |
|------|------|
| 长度 | ≥ 32 字符 |
| 大写字母 | ≥ 1 个 |
| 小写字母 | ≥ 1 个 |
| 数字 | ≥ 1 个 |
| 特殊字符 | ≥ 1 个 |

### 生产环境安全检查清单

- [ ] `FLASK_SECRET_KEY` 已设置且符合强度要求
- [ ] `SOUI_DEBUG=false`
- [ ] `SOUI_CORS_ORIGINS` 仅包含必要域名
- [ ] `SOUI_COOKIE_SECURE=true` (如使用 HTTPS)
- [ ] 使用强密码保护数据库（如适用）
- [ ] 定期轮换密钥
- [ ] 启用防火墙规则

---

## 网络配置

### 端口映射

```yaml
# docker-compose.yml
ports:
  - "5000:5000"  # host:container
```

**说明**：
- 左侧：主机端口
- 右侧：容器端口
- 格式：`HOST_PORT:CONTAINER_PORT`

### 网络模式

#### Bridge 网络（默认）

```yaml
networks:
  star-office-network:
    driver: bridge
```

**特点**：
- 容器通过内部 IP 通信
- 端口映射到主机
- 隔离性好

#### Host 网络（不推荐）

```yaml
network_mode: host
```

**特点**：
- 直接使用主机网络栈
- 性能略高
- 安全性较低

### WebSocket 配置

SocketIO 默认配置：

```python
SOCKETIO_CORS_ORIGINS = CORS_ORIGINS  # 从环境变量继承
SOCKETIO_ASYNC_MODE = "threading"
```

**传输方式**：
- WebSocket（优先）
- Polling（降级）

---

## 数据库配置

### 数据库路径

自动解析逻辑：

1. 首选：`skills/github-collab/github-collab.db`
2. 备选：`../skills/github-collab/github-collab.db`

### 数据库连接池

```python
# 默认配置
pool_size = 5
timeout = 30.0  # 秒
```

### SQLite 优化

```sql
-- WAL 模式（已启用）
PRAGMA journal_mode=WAL;

-- 超时设置
PRAGMA busy_timeout=30000;
```

---

## 性能调优

### 同步间隔优化

```bash
# 低负载环境
SOUI_SYNC_INTERVAL=10

# 高负载环境
SOUI_SYNC_INTERVAL=30
```

### 连接池调整

编辑 `backend/services/database_service.py`：

```python
# 增加连接池大小
db_service = DatabaseService(pool_size=10)
```

### 内存限制

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 128M
```

---

## Docker 配置

### 构建参数

```bash
# 默认值
BUILD_TARGET=production
PYTHON_VERSION=3.11
```

### 卷配置

```yaml
volumes:
  - star-office-data:/data  # 命名卷
  # 或
  - ./data:/data            # 绑定挂载
```

### 健康检查

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

**参数说明**：
- `interval`: 检查间隔
- `timeout`: 超时时间
- `retries`: 失败重试次数
- `start_period`: 启动宽限期

---

## 配置验证

### 启动前检查

```bash
# 1. 检查环境变量
cat .env | grep -E "^(FLASK_SECRET_KEY|SOUI_)"

# 2. 验证密钥强度
python -c "
from backend.config import Config
try:
    Config.validate()
    print('✓ 配置验证通过')
except Exception as e:
    print(f'✗ 配置错误：{e}')
"
```

### 运行时检查

```bash
# 查看容器环境变量
docker exec star-office-ui env | grep -E "(FLASK|SOUI)"

# 测试健康端点
curl http://localhost:5000/api/health

# 查看启动日志
docker-compose logs star-office-ui | grep -E "(Starting|Error|Config)"
```

### 配置测试脚本

创建 `test-config.py`：

```python
#!/usr/bin/env python3
"""Configuration validation script."""

import os
from backend.config import Config, ConfigError

def test_config():
    """Test configuration."""
    print("Testing configuration...")
    
    try:
        # Test secret key
        print(f"✓ SECRET_KEY length: {len(Config.SECRET_KEY)}")
        
        # Test CORS origins
        print(f"✓ CORS origins: {Config.CORS_ORIGINS}")
        
        # Test server config
        print(f"✓ Host: {Config.HOST}:{Config.PORT}")
        print(f"✓ Debug: {Config.DEBUG}")
        
        # Validate
        Config.validate()
        print("✓ All checks passed!")
        
    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(test_config())
```

运行：
```bash
python test-config.py
```

---

## 故障排除

### 配置未生效

```bash
# 检查 .env 文件位置
ls -la .env

# 验证 Docker 环境变量
docker-compose config | grep environment

# 检查容器内环境变量
docker exec star-office-ui printenv
```

### 密钥无效

```bash
# 重新生成
export FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 更新 .env 文件
echo "FLASK_SECRET_KEY=$FLASK_SECRET_KEY" >> .env
```

### CORS 错误

```bash
# 添加当前域名
SOUI_CORS_ORIGINS="http://localhost:3000,http://yourdomain.com"

# 重启服务
docker-compose restart
```

---

## 最佳实践

### 1. 环境分离

```bash
# 开发环境
.env.development

# 生产环境
.env.production
```

### 2. 密钥管理

- 使用环境变量管理敏感信息
- 不要在代码中硬编码密钥
- 定期轮换密钥
- 使用密钥管理服务（生产环境）

### 3. 配置版本控制

```bash
# .gitignore 应包含
.env
.env.*
! .env.template
```

### 4. 文档化

- 记录所有自定义配置
- 维护配置变更历史
- 提供配置示例

---

*最后更新：2024 年 4 月*
