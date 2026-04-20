"""
认证中间件 - Star Office UI
提供 JWT 认证相关的装饰器和工具函数
"""
import jwt
import functools
import os
from datetime import datetime, timedelta
from typing import Optional, Callable
from flask import request, jsonify, g
from backend.database import db
from backend.models.user import User


# JWT 配置 - 从环境变量读取，生产环境必须配置
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-only-change-in-production')
if 'dev-only' in JWT_SECRET_KEY:
    import warnings
    warnings.warn("⚠️ Using default JWT secret key! Set JWT_SECRET_KEY environment variable for production!")

JWT_ACCESS_EXPIRY = timedelta(hours=24)
JWT_REFRESH_EXPIRY = timedelta(days=7)


def generate_access_token(user: User) -> str:
    """生成访问令牌（24 小时）"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + JWT_ACCESS_EXPIRY,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user: User) -> str:
    """生成刷新令牌（7 天）"""
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + JWT_REFRESH_EXPIRY,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithms=['HS256'])


def decode_token(token: str) -> Optional[dict]:
    """解码并验证令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') not in ['access', 'refresh']:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user() -> Optional[User]:
    """获取当前用户（从 g 对象）"""
    return getattr(g, 'current_user', None)


def require_auth(f: Callable) -> Callable:
    """
    认证装饰器 - 要求用户已登录
    从 Authorization header 中读取 Bearer token
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # 获取 token
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'missing_token',
                'message': '缺少认证令牌'
            }), 401

        # 解析 Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'success': False,
                'error': 'invalid_token_format',
                'message': '认证令牌格式错误'
            }), 401

        token = parts[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'invalid_token',
                'message': '无效的认证令牌'
            }), 401

        # 验证 token 类型
        if payload.get('type') != 'access':
            return jsonify({
                'success': False,
                'error': 'invalid_token_type',
                'message': '令牌类型错误'
            }), 401

        # 获取用户
        user = db.session.get(User, payload['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'user_not_found',
                'message': '用户不存在'
            }), 401

        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'user_inactive',
                'message': '用户已被禁用'
            }), 401

        # 存储到 g 对象供后续使用
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated


def require_admin(f: Callable) -> Callable:
    """
    管理员装饰器 - 要求用户是管理员
    内部调用 require_auth，然后检查角色
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # 先执行认证
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'missing_token',
                'message': '缺少认证令牌'
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'success': False,
                'error': 'invalid_token_format',
                'message': '认证令牌格式错误'
            }), 401

        token = parts[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'invalid_token',
                'message': '无效的认证令牌'
            }), 401

        if payload.get('type') != 'access':
            return jsonify({
                'success': False,
                'error': 'invalid_token_type',
                'message': '令牌类型错误'
            }), 401

        user = db.session.get(User, payload['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'user_not_found',
                'message': '用户不存在'
            }), 401

        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'user_inactive',
                'message': '用户已被禁用'
            }), 401

        # 检查管理员权限
        if not user.is_admin():
            return jsonify({
                'success': False,
                'error': 'forbidden',
                'message': '需要管理员权限'
            }), 403

        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated
