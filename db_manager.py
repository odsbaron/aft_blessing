# -*- coding: utf-8 -*-
"""
数据库管理模块
支持 SQLite、MySQL 和 PostgreSQL 三种数据库
"""

import sqlite3
import pymysql
import psycopg2
import psycopg2.extras
from datetime import datetime
from config import Config


class DBManager:
    """数据库管理类"""

    def __init__(self):
        """初始化数据库连接"""
        self.db_type = Config.DB_TYPE.lower()

        # 检测是否有 DATABASE_URL (Railway PostgreSQL)
        if Config.DB_URL:
            self.db_type = "postgresql"

        if self.db_type == "sqlite":
            self._init_sqlite()
        elif self.db_type == "postgresql":
            self._init_postgresql()
        else:
            self._init_mysql()

    def _init_sqlite(self):
        """初始化 SQLite 连接"""
        self.conn = sqlite3.connect(
            Config.DB_SQLITE_PATH,
            check_same_thread=False
        )
        self.conn.row_factory = sqlite3.Row

    def _init_mysql(self):
        """初始化 MySQL 连接"""
        self.conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )

    def _init_postgresql(self):
        """初始化 PostgreSQL 连接（Railway）"""
        self.conn = psycopg2.connect(Config.DB_URL)
        self.conn.autocommit = False

    def _execute(self, sql, params=None, fetch=False):
        """统一执行SQL的方法"""
        if self.db_type == "postgresql":
            # PostgreSQL 使用 RealDictCursor 返回字典
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = self.conn.cursor()

        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        if fetch:
            if self.db_type == "sqlite":
                rows = cursor.fetchall()
                # 将 Row 对象转换为字典
                return [dict(row) for row in rows]
            else:
                # MySQL 和 PostgreSQL 已经返回字典
                return cursor.fetchall()
        return None

    # ========== 生日相关 ==========

    def get_todays_birthdays(self):
        """获取今天过生日且今年未发送的用户"""
        today = datetime.now()

        if self.db_type == "sqlite":
            # SQLite 日期函数
            sql = """
                SELECT id, name, email, dob
                FROM users
                WHERE cast(strftime('%m', dob) as integer) = ?
                  AND cast(strftime('%d', dob) as integer) = ?
                  AND (last_sent_year IS NULL OR last_sent_year < ?)
                ORDER BY id
            """
            return self._execute(sql, (today.month, today.day, today.year), fetch=True)
        elif self.db_type == "postgresql":
            # PostgreSQL 日期函数
            sql = """
                SELECT id, name, email, dob
                FROM users
                WHERE EXTRACT(MONTH FROM dob) = %s
                  AND EXTRACT(DAY FROM dob) = %s
                  AND (last_sent_year IS NULL OR last_sent_year < %s)
                ORDER BY id
            """
            return self._execute(sql, (today.month, today.day, today.year), fetch=True)
        else:
            # MySQL 日期函数
            sql = """
                SELECT id, name, email, dob
                FROM users
                WHERE MONTH(dob) = %s
                  AND DAY(dob) = %s
                  AND (last_sent_year IS NULL OR last_sent_year < %s)
                ORDER BY id
            """
            return self._execute(sql, (today.month, today.day, today.year), fetch=True)

    def update_send_status(self, user_id, success=True, error_msg=None):
        """更新用户发送状态"""
        if success:
            if self.db_type == "sqlite":
                sql = "UPDATE users SET last_sent_year = ? WHERE id = ?"
                self._execute(sql, (datetime.now().year, user_id))
                log_sql = """
                    INSERT INTO send_logs (user_id, sent_at, status)
                    VALUES (?, datetime('now'), 'success')
                """
                self._execute(log_sql, (user_id,))
            else:
                # MySQL 和 PostgreSQL 都使用 %s 和 NOW()
                sql = "UPDATE users SET last_sent_year = %s WHERE id = %s"
                self._execute(sql, (datetime.now().year, user_id))
                log_sql = """
                    INSERT INTO send_logs (user_id, sent_at, status)
                    VALUES (%s, NOW(), 'success')
                """
                self._execute(log_sql, (user_id,))
        else:
            # 记录失败日志
            if self.db_type == "sqlite":
                log_sql = """
                    INSERT INTO send_logs (user_id, sent_at, status, error_msg)
                    VALUES (?, datetime('now'), 'failed', ?)
                """
                self._execute(log_sql, (user_id, error_msg))
            else:
                log_sql = """
                    INSERT INTO send_logs (user_id, sent_at, status, error_msg)
                    VALUES (%s, NOW(), 'failed', %s)
                """
                self._execute(log_sql, (user_id, error_msg))

        self.conn.commit()

    # ========== 祝福语相关 ==========

    def get_random_wish(self):
        """随机获取一条启用的祝福语"""
        if self.db_type == "sqlite":
            sql = """
                SELECT content
                FROM wishes
                WHERE is_active = 1
                ORDER BY RANDOM()
                LIMIT 1
            """
        elif self.db_type == "postgresql":
            sql = """
                SELECT content
                FROM wishes
                WHERE is_active = 1
                ORDER BY RANDOM()
                LIMIT 1
            """
        else:
            sql = """
                SELECT content
                FROM wishes
                WHERE is_active = 1
                ORDER BY RAND()
                LIMIT 1
            """
        rows = self._execute(sql, fetch=True)
        return rows[0]['content'] if rows else "生日快乐！愿你天天开心，万事如意！"

    def add_wish(self, content, category='general'):
        """添加祝福语"""
        if self.db_type == "sqlite":
            sql = "INSERT OR IGNORE INTO wishes (content, category) VALUES (?, ?)"
            self._execute(sql, (content, category))
        else:
            sql = "INSERT IGNORE INTO wishes (content, category) VALUES (%s, %s)"
            self._execute(sql, (content, category))
        self.conn.commit()
        return True

    def get_all_wishes(self):
        """获取所有祝福语"""
        sql = "SELECT * FROM wishes ORDER BY category, id"
        return self._execute(sql, fetch=True)

    # ========== 用户管理 ==========

    def add_user(self, name, email, dob):
        """添加单个用户"""
        if self.db_type == "sqlite":
            sql = "INSERT OR IGNORE INTO users (name, email, dob) VALUES (?, ?, ?)"
            self._execute(sql, (name, email, dob))
        else:
            sql = "INSERT IGNORE INTO users (name, email, dob) VALUES (%s, %s, %s)"
            self._execute(sql, (name, email, dob))
        self.conn.commit()
        return True

    def get_all_users(self):
        """获取所有用户"""
        sql = "SELECT * FROM users ORDER BY dob"
        return self._execute(sql, fetch=True)

    def get_user_stats(self):
        """获取用户统计信息"""
        if self.db_type == "sqlite":
            sql = """
                SELECT
                    COUNT(*) as total_users,
                    SUM(CASE WHEN cast(strftime('%m', dob) as integer) = cast(strftime('%m', 'now') as integer)
                              AND cast(strftime('%d', dob) as integer) = cast(strftime('%d', 'now') as integer)
                         THEN 1 ELSE 0 END) as today_birthdays,
                    SUM(CASE WHEN cast(strftime('%m', dob) as integer) = cast(strftime('%m', 'now') as integer)
                         THEN 1 ELSE 0 END) as this_month_birthdays
                FROM users
            """
        elif self.db_type == "postgresql":
            sql = """
                SELECT
                    COUNT(*) as total_users,
                    SUM(CASE WHEN EXTRACT(MONTH FROM dob) = EXTRACT(MONTH FROM CURRENT_DATE)
                              AND EXTRACT(DAY FROM dob) = EXTRACT(DAY FROM CURRENT_DATE)
                         THEN 1 ELSE 0 END) as today_birthdays,
                    SUM(CASE WHEN EXTRACT(MONTH FROM dob) = EXTRACT(MONTH FROM CURRENT_DATE)
                         THEN 1 ELSE 0 END) as this_month_birthdays
                FROM users
            """
        else:
            sql = """
                SELECT
                    COUNT(*) as total_users,
                    SUM(CASE WHEN MONTH(dob) = MONTH(CURDATE()) AND DAY(dob) = DAY(CURDATE()) THEN 1 ELSE 0 END) as today_birthdays,
                    SUM(CASE WHEN MONTH(dob) = MONTH(CURDATE()) THEN 1 ELSE 0 END) as this_month_birthdays
                FROM users
            """
        rows = self._execute(sql, fetch=True)
        return rows[0] if rows else {'total_users': 0, 'today_birthdays': 0, 'this_month_birthdays': 0}

    # ========== 发送日志 ==========

    def get_send_logs(self, limit=100):
        """获取发送日志"""
        if self.db_type == "sqlite":
            sql = """
                SELECT l.*, u.name, u.email
                FROM send_logs l
                JOIN users u ON l.user_id = u.id
                ORDER BY l.sent_at DESC
                LIMIT ?
            """
            return self._execute(sql, (limit,), fetch=True)
        else:
            sql = """
                SELECT l.*, u.name, u.email
                FROM send_logs l
                JOIN users u ON l.user_id = u.id
                ORDER BY l.sent_at DESC
                LIMIT %s
            """
            return self._execute(sql, (limit,), fetch=True)

    def get_today_send_count(self):
        """获取今天发送成功的数量"""
        if self.db_type == "sqlite":
            sql = """
                SELECT COUNT(*) as count
                FROM send_logs
                WHERE date(sent_at) = date('now')
                AND status = 'success'
            """
        elif self.db_type == "postgresql":
            sql = """
                SELECT COUNT(*) as count
                FROM send_logs
                WHERE DATE(sent_at) = CURRENT_DATE
                AND status = 'success'
            """
        else:
            sql = """
                SELECT COUNT(*) as count
                FROM send_logs
                WHERE DATE(sent_at) = CURDATE()
                AND status = 'success'
            """
        rows = self._execute(sql, fetch=True)
        return rows[0]['count'] if rows else 0

    # ========== 连接管理 ==========

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()


# 测试代码
if __name__ == "__main__":
    try:
        db = DBManager()
        print(f"✅ 数据库连接成功 ({Config.DB_TYPE})")

        # 测试统计
        stats = db.get_user_stats()
        print(f"📊 用户统计:")
        print(f"  - 总用户数: {stats['total_users']}")
        print(f"  - 今日生日: {stats['today_birthdays']}")
        print(f"  - 本月生日: {stats['this_month_birthdays']}")

        # 测试今日寿星
        birthdays = db.get_todays_birthdays()
        print(f"\n🎂 今日寿星 ({len(birthdays)}人):")
        for user in birthdays:
            print(f"  - {user['name']} ({user['email']})")

        db.close()

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
