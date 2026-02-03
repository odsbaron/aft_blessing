# -*- coding: utf-8 -*-
"""
用户认证模块
提供登录、登出和会话管理功能
"""

import hashlib
import secrets
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, redirect, url_for, flash
from db_manager import DBManager


class AuthManager:
    """认证管理器"""

    # 会话配置
    SESSION_DURATION = timedelta(hours=12)

    # 密码强度要求
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False

    # 默认管理员配置（仅用于首次初始化）
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """初始化Flask应用"""
        app.config['SESSION_PERMANENT'] = True
        app.config['PERMANENT_SESSION_LIFETIME'] = self.SESSION_DURATION

    @staticmethod
    def hash_password(password):
        """哈希密码"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, hashed):
        """验证密码"""
        return AuthManager.hash_password(password) == hashed

    @staticmethod
    def validate_password_strength(password):
        """
        验证密码强度

        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        errors = []

        if len(password) < AuthManager.PASSWORD_MIN_LENGTH:
            errors.append(f"密码长度至少需要 {AuthManager.PASSWORD_MIN_LENGTH} 位")

        if AuthManager.PASSWORD_REQUIRE_UPPER and not re.search(r'[A-Z]', password):
            errors.append("密码需要包含至少一个大写字母")

        if AuthManager.PASSWORD_REQUIRE_LOWER and not re.search(r'[a-z]', password):
            errors.append("密码需要包含至少一个小写字母")

        if AuthManager.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("密码需要包含至少一个数字")

        if AuthManager.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("密码需要包含至少一个特殊字符")

        # 检查是否是弱密码
        weak_passwords = ['12345678', 'password', 'qwerty123', 'admin123', 'abcd1234']
        if password.lower() in weak_passwords:
            errors.append("密码过于简单，请使用更复杂的密码")

        return len(errors) == 0, errors

    @staticmethod
    def is_default_password(password):
        """检查是否是默认密码"""
        return password == AuthManager.DEFAULT_ADMIN_PASSWORD

    @staticmethod
    def create_reset_token():
        """创建密码重置令牌"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def authenticate(username, password):
        """
        验证用户登录
        返回: (成功与否, 用户信息或错误消息)
        """
        db = DBManager()
        try:
            if db.db_type == "sqlite":
                users = db._execute(
                    "SELECT * FROM admin_users WHERE username = ?",
                    (username,),
                    fetch=True
                )
            else:
                users = db._execute(
                    "SELECT * FROM admin_users WHERE username = %s",
                    (username,),
                    fetch=True
                )

            if not users:
                return False, "用户名不存在"

            user = users[0]

            # 检查账户状态
            if not user.get('is_active', 1):
                return False, "账户已被禁用"

            # 验证密码
            if AuthManager.verify_password(password, user['password_hash']):
                # 更新最后登录时间
                if db.db_type == "sqlite":
                    db._execute(
                        "UPDATE admin_users SET last_login = datetime('now') WHERE id = ?",
                        (user['id'],)
                    )
                else:
                    db._execute(
                        "UPDATE admin_users SET last_login = NOW() WHERE id = %s",
                        (user['id'],)
                    )
                db.conn.commit()

                # 返回用户信息（不包含密码）
                user.pop('password_hash', None)
                return True, user
            else:
                return False, "密码错误"

        finally:
            db.close()

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        修改密码

        Returns:
            (success, message): 是否成功和消息
        """
        db = DBManager()
        try:
            # 获取用户当前密码
            if db.db_type == "sqlite":
                users = db._execute(
                    "SELECT password_hash FROM admin_users WHERE id = ?",
                    (user_id,),
                    fetch=True
                )
            else:
                users = db._execute(
                    "SELECT password_hash FROM admin_users WHERE id = %s",
                    (user_id,),
                    fetch=True
                )

            if not users:
                return False, "用户不存在"

            # 验证旧密码
            if not AuthManager.verify_password(old_password, users[0]['password_hash']):
                return False, "原密码错误"

            # 验证新密码强度
            is_valid, errors = AuthManager.validate_password_strength(new_password)
            if not is_valid:
                return False, "；".join(errors)

            # 更新密码
            new_hash = AuthManager.hash_password(new_password)
            if db.db_type == "sqlite":
                db._execute(
                    "UPDATE admin_users SET password_hash = ? WHERE id = ?",
                    (new_hash, user_id)
                )
            else:
                db._execute(
                    "UPDATE admin_users SET password_hash = %s WHERE id = %s",
                    (new_hash, user_id)
                )
            db.conn.commit()

            return True, "密码修改成功"

        finally:
            db.close()

    @staticmethod
    def check_password_change_required(user_id):
        """检查用户是否需要修改密码（首次登录或使用默认密码）"""
        db = DBManager()
        try:
            if db.db_type == "sqlite":
                users = db._execute(
                    "SELECT password_hash, password_changed FROM admin_users WHERE id = ?",
                    (user_id,),
                    fetch=True
                )
            else:
                users = db._execute(
                    "SELECT password_hash, password_changed FROM admin_users WHERE id = %s",
                    (user_id,),
                    fetch=True
                )

            if not users:
                return False

            user = users[0]

            # 检查是否是默认密码或未修改过
            if (user.get('password_changed', 0) == 0 or
                AuthManager.verify_password(AuthManager.DEFAULT_ADMIN_PASSWORD, user['password_hash'])):
                return True

            return False

        finally:
            db.close()

    @staticmethod
    def mark_password_changed(user_id):
        """标记密码已修改"""
        db = DBManager()
        try:
            # 添加password_changed字段（如果不存在）
            if db.db_type == "sqlite":
                # SQLite不支持ALTER TABLE ADD COLUMN IF NOT EXISTS，需要检查
                try:
                    db._execute("SELECT password_changed FROM admin_users LIMIT 1")
                except:
                    db._execute("ALTER TABLE admin_users ADD COLUMN password_changed INTEGER DEFAULT 0")

                db._execute(
                    "UPDATE admin_users SET password_changed = 1 WHERE id = ?",
                    (user_id,)
                )
            else:
                try:
                    db._execute("SELECT password_changed FROM admin_users LIMIT 1")
                except:
                    db._execute("ALTER TABLE admin_users ADD COLUMN password_changed TINYINT(1) DEFAULT 0")

                db._execute(
                    "UPDATE admin_users SET password_changed = 1 WHERE id = %s",
                    (user_id,)
                )
            db.conn.commit()

        except Exception as e:
            print(f"Warning: Could not mark password as changed: {e}")
        finally:
            db.close()

    @staticmethod
    def login_user(user):
        """将用户登录到会话"""
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user.get('role', 'admin')
        session['login_time'] = datetime.now().isoformat()

        # 标记是否需要修改密码（用于显示警告，不强制跳转）
        if AuthManager.check_password_change_required(user['id']):
            session['password_change_required'] = True
        else:
            session['password_change_required'] = False

    @staticmethod
    def logout_user():
        """登出用户"""
        session.clear()

    @staticmethod
    def get_current_user():
        """获取当前登录用户"""
        if 'user_id' in session:
            return {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'role': session.get('role', 'admin')
            }
        return None

    @staticmethod
    def is_logged_in():
        """检查用户是否已登录"""
        return 'user_id' in session

    @staticmethod
    def is_password_change_required():
        """检查当前用户是否需要修改密码"""
        return session.get('password_change_required', False)

    @staticmethod
    def require_role(allowed_roles):
        """检查用户角色权限"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not AuthManager.is_logged_in():
                    return redirect(url_for('login', next=request.url))

                user_role = session.get('role', 'admin')
                if user_role not in allowed_roles:
                    flash('您没有权限访问此页面', 'error')
                    return redirect(url_for('index'))

                return f(*args, **kwargs)
            return decorated_function
        return decorator


# 便捷装饰器
def login_required(f):
    """要求用户登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthManager.is_logged_in():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """要求管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthManager.is_logged_in():
            return redirect(url_for('login', next=request.url))

        if session.get('role') != 'admin':
            flash('需要管理员权限', 'error')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function


def ensure_default_admin():
    """确保存在默认管理员账户"""
    db = DBManager()
    try:
        # 检查是否有管理员（表已由 init_db.py 创建）
        if db.db_type == "sqlite":
            users = db._execute("SELECT COUNT(*) as count FROM admin_users", fetch=True)
        else:
            users = db._execute("SELECT COUNT(*) as count FROM admin_users", fetch=True)

        if users[0]['count'] == 0:
            # 创建默认管理员
            password_hash = AuthManager.hash_password(AuthManager.DEFAULT_ADMIN_PASSWORD)
            if db.db_type == "sqlite":
                db._execute(
                    "INSERT INTO admin_users (username, password_hash, role, is_active, password_changed) VALUES (?, ?, ?, ?, ?)",
                    (AuthManager.DEFAULT_ADMIN_USERNAME, password_hash, 'admin', 1, 0)
                )
            else:
                db._execute(
                    "INSERT INTO admin_users (username, password_hash, role, is_active, password_changed) VALUES (%s, %s, %s, %s, %s)",
                    (AuthManager.DEFAULT_ADMIN_USERNAME, password_hash, 'admin', 1, 0)
                )
            db.conn.commit()
            print(f"✅ 已创建默认管理员账户: {AuthManager.DEFAULT_ADMIN_USERNAME}")
            print(f"🔐 默认密码: {AuthManager.DEFAULT_ADMIN_PASSWORD}")
            print("⚠️  请在首次登录后立即修改默认密码！")

    except Exception as e:
        print(f"⚠️ 创建默认管理员时出错: {e}")
        print("ℹ️ 请确保已运行 python init_db.py 初始化数据库")
    finally:
        db.close()
