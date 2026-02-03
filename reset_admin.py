# -*- coding: utf-8 -*-
"""
重置管理员密码工具
"""
import hashlib
import sqlite3

DB_PATH = "birthday.db"


def reset_admin_password(new_password=None):
    """重置管理员密码"""
    if new_password is None:
        new_password = "admin123"

    print(f"🔄 正在重置管理员密码...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 生成密码哈希
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()

        # 更新密码
        cursor.execute(
            "UPDATE admin_users SET password_hash = ? WHERE username = ?",
            (password_hash, "admin")
        )

        conn.commit()

        print(f"✅ 密码已重置！")
        print(f"\n📋 登录信息:")
        print(f"   用户名: admin")
        print(f"   密码: {new_password}")

    except Exception as e:
        print(f"❌ 重置失败: {e}")
    finally:
        conn.close()


def list_admins():
    """列出所有管理员"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, role, is_active FROM admin_users")
        admins = cursor.fetchall()

        print(f"\n📋 管理员列表:")
        print(f"{'ID':<5} {'用户名':<15} {'角色':<10} {'状态':<10}")
        print("-" * 45)
        for admin in admins:
            status = "启用" if admin[3] else "禁用"
            print(f"{admin[0]:<5} {admin[1]:<15} {admin[2]:<10} {status:<10}")

    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         🔐 管理员密码重置工具 🔐                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    list_admins()

    if len(sys.argv) > 1:
        new_password = sys.argv[1]
        print(f"\n使用命令行指定的新密码: {new_password}")
    else:
        print(f"\n未指定新密码，使用默认密码: admin123")
        new_password = "admin123"

    reset_admin_password(new_password)
