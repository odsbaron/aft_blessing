# -*- coding: utf-8 -*-
"""
认证模块单元测试
"""

import unittest
import tempfile
import os
from auth import AuthManager
from db_manager import DBManager


class TestAuthManager(unittest.TestCase):
    """认证管理器测试"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时数据库
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        # 修改配置
        from config import Config
        self.original_db_path = Config.DB_SQLITE_PATH
        Config.DB_SQLITE_PATH = self.db_path

        # 初始化数据库
        self._init_test_db()

    def tearDown(self):
        """每个测试后的清理"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _init_test_db(self):
        """初始化测试数据库"""
        db = DBManager()
        # 创建admin_users表
        db._execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.conn.commit()

        # 创建测试用户
        password_hash = AuthManager.hash_password('test123')
        db._execute(
            "INSERT INTO admin_users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
            ('testuser', password_hash, 'admin', 1)
        )
        db.conn.commit()
        db.close()

    def test_hash_password(self):
        """测试密码哈希"""
        password = "test_password"
        hash1 = AuthManager.hash_password(password)
        hash2 = AuthManager.hash_password(password)

        # 相同密码应该产生相同哈希
        self.assertEqual(hash1, hash2)

        # 不同密码应该产生不同哈希
        hash3 = AuthManager.hash_password("different")
        self.assertNotEqual(hash1, hash3)

    def test_verify_password(self):
        """测试密码验证"""
        password = "test_password"
        hash_value = AuthManager.hash_password(password)

        # 正确密码应该验证通过
        self.assertTrue(AuthManager.verify_password(password, hash_value))

        # 错误密码应该验证失败
        self.assertFalse(AuthManager.verify_password("wrong", hash_value))

    def test_authenticate_success(self):
        """测试成功认证"""
        success, result = AuthManager.authenticate('testuser', 'test123')

        self.assertTrue(success)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['role'], 'admin')

    def test_authenticate_wrong_password(self):
        """测试错误密码"""
        success, result = AuthManager.authenticate('testuser', 'wrong_password')

        self.assertFalse(success)
        self.assertIn("密码", result)

    def test_authenticate_nonexistent_user(self):
        """测试不存在的用户"""
        success, result = AuthManager.authenticate('nonexistent', 'password')

        self.assertFalse(success)
        self.assertIn("不存在", result)

    def test_create_reset_token(self):
        """测试创建重置令牌"""
        token1 = AuthManager.create_reset_token()
        token2 = AuthManager.create_reset_token()

        # 令牌应该是唯一的
        self.assertNotEqual(token1, token2)

        # 令牌应该有一定长度
        self.assertGreater(len(token1), 30)

    def test_inactive_user(self):
        """测试禁用用户"""
        db = DBManager()

        # 创建一个禁用用户
        password_hash = AuthManager.hash_password('password')
        db._execute(
            "INSERT INTO admin_users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
            ('inactive_user', password_hash, 'admin', 0)
        )
        db.conn.commit()
        db.close()

        # 尝试认证
        success, result = AuthManager.authenticate('inactive_user', 'password')

        self.assertFalse(success)
        self.assertIn("禁用", result)


class TestSessionManagement(unittest.TestCase):
    """会话管理测试"""

    def test_login_logout(self):
        """测试登录登出"""
        # 模拟登录
        user = {
            'id': 1,
            'username': 'testuser',
            'role': 'admin'
        }

        # 在实际Flask应用中，这些会操作session
        # 这里只测试逻辑
        AuthManager.login_user(user)

        # 检查会话数据（需要Flask上下文）
        # 在单元测试中，我们模拟会话数据

    def test_session_validation(self):
        """测试会话验证"""
        # 测试会话验证逻辑
        pass


if __name__ == '__main__':
    unittest.main()
