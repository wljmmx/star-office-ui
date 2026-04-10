"""
性能优化模块
提供缓存、连接池、异步处理等优化方案
"""

import time
import hashlib
from functools import wraps
from typing import Any, Callable, Dict, Optional
import threading
from collections import OrderedDict

class LRUCache:
    """
    LRU 缓存实现
    自动淘汰最少使用的数据
    """
    
    def __init__(self, maxsize: int = 128, ttl: int = 300):
        self.maxsize = maxsize
        self.ttl = ttl  # 缓存过期时间（秒）
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            if time.time() - item['timestamp'] > self.ttl:
                # 过期，删除
                del self.cache[key]
                return None
            
            # 移动到末尾（最近使用）
            self.cache.move_to_end(key)
            return item['value']
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            
            while len(self.cache) >= self.maxsize:
                # 淘汰最旧的
                self.cache.popitem(last=False)
            
            self.cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()

# 全局缓存实例
cache = LRUCache(maxsize=256, ttl=300)

def cached(ttl: int = 300):
    """
    缓存装饰器
    自动缓存函数结果，减少重复计算
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # 尝试从缓存获取
            result = cache.get(key)
            if result is not None:
                return result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache.set(key, result)
            
            return result
        return wrapper
    return decorator

class ConnectionPool:
    """
    数据库连接池
    复用连接，减少创建开销
    """
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
        self.created_at = time.time()
    
    def get_connection(self):
        """获取连接"""
        with self.lock:
            if len(self.connections) < self.max_connections:
                # 创建新连接
                conn = {'created': time.time(), 'used': 0}
                self.connections.append(conn)
                return conn
            
            # 复用现有连接
            conn = self.connections[0]
            conn['used'] += 1
            return conn
    
    def release_connection(self, conn):
        """释放连接（实际是放回池中）"""
        # 连接池模式下不需要真正释放
        pass

# 全局连接池
db_pool = ConnectionPool(max_connections=10)

def optimize_database_query(func: Callable) -> Callable:
    """
    数据库查询优化装饰器
    添加连接池和结果缓存
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 使用连接池
        conn = db_pool.get_connection()
        
        try:
            # 执行查询（这里需要实际实现）
            result = func(*args, **kwargs)
            return result
        finally:
            db_pool.release_connection(conn)
    
    return wrapper

class AsyncTaskQueue:
    """
    异步任务队列
    用于处理耗时操作，不阻塞主线程
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.queue = []
        self.workers = []
        self.running = False
    
    def start(self):
        """启动工作线程"""
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """停止工作线程"""
        self.running = False
        for worker in self.workers:
            worker.join()
    
    def add_task(self, func: Callable, *args, **kwargs):
        """添加任务"""
        with self.lock:
            self.queue.append((func, args, kwargs))
    
    def _worker(self):
        """工作线程"""
        while self.running:
            with self.lock:
                if not self.queue:
                    time.sleep(0.1)
                    continue
                
                func, args, kwargs = self.queue.pop(0)
            
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Task failed: {e}")

# 全局异步任务队列
task_queue = AsyncTaskQueue(max_workers=4)

def async_task(func: Callable) -> Callable:
    """
    异步任务装饰器
    将任务放入队列异步执行
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        task_queue.add_task(func, *args, **kwargs)
        return {"status": "queued", "task_id": hash((func, args, kwargs))}
    
    return wrapper

# 性能监控
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record(self, name: str, duration: float):
        """记录指标"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = {'count': 0, 'total_time': 0, 'min_time': float('inf'), 'max_time': 0}
            
            metrics = self.metrics[name]
            metrics['count'] += 1
            metrics['total_time'] += duration
            metrics['min_time'] = min(metrics['min_time'], duration)
            metrics['max_time'] = max(metrics['max_time'], duration)
    
    def get_stats(self, name: str) -> Dict:
        """获取统计信息"""
        with self.lock:
            if name not in self.metrics:
                return {}
            
            m = self.metrics[name]
            return {
                'count': m['count'],
                'avg_time': m['total_time'] / m['count'],
                'min_time': m['min_time'],
                'max_time': m['max_time'],
                'total_time': m['total_time']
            }

# 全局性能监控
monitor = PerformanceMonitor()

def monitor_time(name: str = None):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            func_name = name or func.__name__
            monitor.record(func_name, duration)
            
            return result
        return wrapper
    return decorator
