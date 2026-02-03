# -*- coding: utf-8 -*-
"""
数据库初始化脚本
支持 SQLite 和 MySQL 两种数据库
"""

import sqlite3
import os
import sys
from config import Config


def init_sqlite():
    """初始化 SQLite 数据库"""
    print(f"🔄 正在初始化 SQLite 数据库...")

    conn = None
    try:
        # 确保使用绝对路径
        db_path = Config.DB_SQLITE_PATH
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                db_path
            ))

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"✅ 已创建数据库文件: {db_path}")

        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                dob TEXT NOT NULL,
                last_sent_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 表 'users' 已创建")

        # 创建祝福语表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 表 'wishes' 已创建")

        # 创建发送日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS send_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success',
                error_msg TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✅ 表 'send_logs' 已创建")

        # 创建管理员用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                password_changed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 表 'admin_users' 已创建")

        # 创建邮件模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                html_template TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 表 'email_templates' 已创建")

        # 插入初始祝福语数据
        initial_wishes = [
            ("生日快乐！愿你的每一天都充满阳光和欢笑！", "general"),
            ("在这特别的日子里，祝你心想事成，万事如意！", "formal"),
            ("又年长了一岁，愿你智慧与财富双丰收！", "formal"),
            ("生日快乐！愿你永远保持一颗年轻的心。", "warm"),
            ("恭喜你又成功升级了！等级+1，经验+1！", "humor"),
            ("今天你是主角，尽情享受属于你的快乐时光！", "warm"),
            ("愿你的生日充满无穷的快乐，愿你今天的回忆温馨，愿你今天的梦想甜美！", "general"),
            ("生日快乐！愿你年年皆胜意，岁岁都欢愉！", "poetic"),
            ("愿你每天都能笑靥如花，愿你所有的梦想都能实现！", "warm"),
            ("生日快乐！愿你在新的一岁里，收获满满的幸福！", "general"),
        ]

        for wish_content, category in initial_wishes:
            cursor.execute(
                "INSERT OR IGNORE INTO wishes (content, category) VALUES (?, ?)",
                (wish_content, category)
            )

        conn.commit()
        print(f"✅ 已插入 {len(initial_wishes)} 条初始祝福语")

        print("\n🎉 SQLite 数据库初始化完成！")

        # 显示统计信息
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) as count FROM wishes")
        wish_count = cursor.fetchone()[0]

        print(f"\n📊 当前数据统计:")
        print(f"   - 用户数: {user_count}")
        print(f"   - 祝福语数: {wish_count}")

        return True

    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        return False

    finally:
        if conn:
            conn.close()


def init_mysql():
    """初始化 MySQL 数据库"""
    import pymysql

    print("🔄 正在初始化 MySQL 数据库...")

    conn = None
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            charset=Config.DB_CHARSET
        )
        print(f"✅ 已连接到 MySQL 服务器")

        # 创建数据库
        with conn.cursor() as cursor:
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}
                CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            print(f"✅ 数据库 '{Config.DB_NAME}' 已就绪")

        conn.select_db(Config.DB_NAME)

        # 创建表
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    dob DATE NOT NULL,
                    last_sent_year INT DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_birthday (MONTH(dob), DAY(dob))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ 表 'users' 已创建")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wishes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category VARCHAR(20) DEFAULT 'general',
                    is_active TINYINT(1) DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ 表 'wishes' 已创建")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS send_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'success',
                    error_msg TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ 表 'send_logs' 已创建")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(64) NOT NULL,
                    role VARCHAR(20) DEFAULT 'admin',
                    is_active TINYINT(1) DEFAULT 1,
                    last_login TIMESTAMP NULL,
                    password_changed TINYINT(1) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ 表 'admin_users' 已创建")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    title VARCHAR(100) NOT NULL,
                    subject VARCHAR(200) NOT NULL,
                    html_template TEXT NOT NULL,
                    description TEXT,
                    is_active TINYINT(1) DEFAULT 1,
                    is_default TINYINT(1) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("✅ 表 'email_templates' 已创建")

            # 插入初始祝福语
            initial_wishes = [
                ("生日快乐！愿你的每一天都充满阳光和欢笑！", "general"),
                ("在这特别的日子里，祝你心想事成，万事如意！", "formal"),
                ("又年长了一岁，愿你智慧与财富双丰收！", "formal"),
                ("生日快乐！愿你永远保持一颗年轻的心。", "warm"),
                ("恭喜你又成功升级了！等级+1，经验+1！", "humor"),
            ]

            for wish_content, category in initial_wishes:
                cursor.execute(
                    "INSERT IGNORE INTO wishes (content, category) VALUES (%s, %s)",
                    (wish_content, category)
                )

        conn.commit()
        print("✅ 已插入初始祝福语数据")
        print("\n🎉 MySQL 数据库初始化完成！")

        return True

    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        return False

    finally:
        if conn:
            conn.close()


def init_database():
    """根据配置初始化数据库"""
    if Config.DB_TYPE.lower() == "sqlite":
        return init_sqlite()
    else:
        return init_mysql()


def reset_database():
    """重置数据库"""
    print("⚠️ 警告：此操作将删除所有数据！")

    confirm = input("确认重置数据库？请输入 'yes' 继续: ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return False

    if Config.DB_TYPE.lower() == "sqlite":
        import os
        if os.path.exists(Config.DB_SQLITE_PATH):
            os.remove(Config.DB_SQLITE_PATH)
            print(f"✅ 已删除数据库文件")
        return init_sqlite()
    else:
        # MySQL 重置
        import pymysql
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                charset=Config.DB_CHARSET
            )
            with conn.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS {Config.DB_NAME}")
                print(f"✅ 数据库 '{Config.DB_NAME}' 已删除")
            conn.close()
            return init_mysql()
        except Exception as e:
            print(f"❌ 重置失败: {e}")
            return False


def show_status():
    """显示数据库状态"""
    if Config.DB_TYPE.lower() == "sqlite":
        import os
        if os.path.exists(Config.DB_SQLITE_PATH):
            print(f"📊 SQLite 数据库状态:")
            print(f"   文件: {Config.DB_SQLITE_PATH}")

            conn = sqlite3.connect(Config.DB_SQLITE_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count} 条记录")

            conn.close()
        else:
            print(f"📭 数据库文件不存在: {Config.DB_SQLITE_PATH}")
            print("   请先运行 'python init_db.py' 初始化数据库")
    else:
        # MySQL 状态
        import pymysql
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASS,
                database=Config.DB_NAME,
                charset=Config.DB_CHARSET
            )
            with conn.cursor() as cursor:
                cursor.execute(f"SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"📊 MySQL 数据库状态:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   - {table}: {count} 条记录")
            conn.close()
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")


def main():
    """主入口"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         🎂 数据库初始化工具 🎂                         ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    print(f"当前数据库类型: {Config.DB_TYPE}")

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command in ['--reset', 'reset']:
            reset_database()
        elif command in ['--status', 'status']:
            show_status()
        else:
            print("未知参数")
    else:
        # 默认：初始化数据库
        init_database()


if __name__ == "__main__":
    main()
