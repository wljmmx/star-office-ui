# Star Office UI - Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# 创建数据目录
RUN mkdir -p /data

# 挂载映射说明（用于 docker-compose 开发环境）：
# - /home/wljmmx/star-office-ui/backend → /app/backend
# - /home/wljmmx/star-office-ui/frontend → /app/frontend
# - /home/wljmmx/.openclaw/skills/github-collab → /app/skills/github-collab
# 注意：生产环境部署时请移除这些挂载，使用镜像内置代码

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# 启动命令
CMD ["python", "backend/main.py"]
