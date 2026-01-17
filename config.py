# -*- coding: utf-8 -*-
"""
配置文件
从环境变量或 .env 文件读取配置
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """配置类"""

    # ========== 邮件配置 ==========
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.163.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
    MAIL_USER = os.getenv("MAIL_USER")
    MAIL_AUTH_CODE = os.getenv("MAIL_AUTH_CODE")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "生日祝福助手")

    # ========== 数据库配置 ==========
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # sqlite, mysql, postgresql

    # Railway / PostgreSQL 连接字符串（自动提供）
    DB_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")

    # MySQL 配置（当 DB_TYPE=mysql 时使用）
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME", "birthday_db")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")
    # SQLite 配置（当 DB_TYPE=sqlite 时使用）
    DB_SQLITE_PATH = os.getenv("DB_SQLITE_PATH", "birthday.db")

    # ========== 定时任务配置 ==========
    SEND_TIME = os.getenv("SEND_TIME", "09:00")

    # ========== 系统配置 ==========
    # 时区设置
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")

    @classmethod
    def validate(cls):
        """验证必要配置是否完整"""
        errors = []

        # 邮件配置必须
        if not cls.MAIL_USER:
            errors.append("缺少 MAIL_USER 配置")
        if not cls.MAIL_AUTH_CODE:
            errors.append("缺少 MAIL_AUTH_CODE 配置")

        # MySQL 配置（仅当使用 MySQL 时验证）
        if cls.DB_TYPE == "mysql":
            if not cls.DB_PASS:
                errors.append("使用 MySQL 时缺少 DB_PASS 配置")

        return errors


# 测试配置是否正确加载
if __name__ == "__main__":
    errors = Config.validate()
    if errors:
        print("❌ 配置错误：")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 配置加载成功")
        print(f"邮件服务器: {Config.MAIL_SERVER}:{Config.MAIL_PORT}")
        print(f"发件人: {Config.MAIL_USER}")
        print(f"数据库: {Config.DB_HOST}/{Config.DB_NAME}")
        print(f"发送时间: {Config.SEND_TIME}")
