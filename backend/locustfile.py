"""
性能测试脚本 - Locust
用于测试 API 响应时间和并发能力
"""

from locust import HttpUser, task, between
import random
import json

class StarOfficeUser(HttpUser):
    """模拟用户行为"""
    
    wait_time = between(1, 3)
    
    @task(3)
    def get_agents(self):
        """获取 Agent 列表 - 高频操作"""
        self.client.get("/api/agents")
    
    @task(2)
    def get_tasks(self):
        """获取任务列表"""
        self.client.get("/api/tasks")
    
    @task(2)
    def get_state(self):
        """获取系统状态"""
        self.client.get("/api/state")
    
    @task(1)
    def get_config(self):
        """获取配置"""
        self.client.get("/api/config")
    
    @task(1)
    def get_assets(self):
        """获取资源"""
        self.client.get("/api/assets/avatars")
    
    @task(1)
    def health_check(self):
        """健康检查"""
        self.client.get("/api/health")
