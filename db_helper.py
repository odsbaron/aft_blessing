# -*- coding: utf-8 -*-
"""
数据库辅助工具
提供数据库类型判断和SQL语法转换等公共功能
"""

from config import Config


class DBType:
    """数据库类型枚举"""
    SQLITE = 'sqlite'
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'


class DBHelper:
    """数据库辅助工具类"""

    @staticmethod
    def get_placeholder(db_type=None):
        """
        获取SQL占位符

        Args:
            db_type: 数据库类型，None则使用Config中的配置

        Returns:
            str: '?' 或 '%s'
        """
        if db_type is None:
            db_type = Config.DB_TYPE.lower()

            # 检查是否有 PostgreSQL 连接字符串
            if Config.DB_URL:
                db_type = DBType.POSTGRESQL

        return '?' if db_type == DBType.SQLITE else '%s'

    @staticmethod
    def get_now_function(db_type=None):
        """获取当前时间的SQL函数"""
        if db_type is None:
            db_type = Config.DB_TYPE.lower()
            if Config.DB_URL:
                db_type = DBType.POSTGRESQL

        if db_type == DBType.SQLITE:
            return "datetime('now')"
        elif db_type == DBType.POSTGRESQL:
            return "CURRENT_TIMESTAMP"
        else:  # MySQL
            return "NOW()"

    @staticmethod
    def get_date_extract(db_type=None, part='month', column='dob'):
        """
        获取日期提取SQL表达式

        Args:
            db_type: 数据库类型
            part: month 或 day
            column: 日期列名

        Returns:
            str: SQL表达式
        """
        if db_type is None:
            db_type = Config.DB_TYPE.lower()
            if Config.DB_URL:
                db_type = DBType.POSTGRESQL

        if db_type == DBType.SQLITE:
            if part == 'month':
                return f"cast(strftime('%m', {column}) as integer)"
            else:  # day
                return f"cast(strftime('%d', {column}) as integer)"
        elif db_type == DBType.POSTGRESQL:
            return f"EXTRACT({part.upper()} FROM {column})"
        else:  # MySQL
            return f"{part.upper()}({column})"

    @staticmethod
    def get_random_function(db_type=None):
        """获取随机排序SQL函数"""
        if db_type is None:
            db_type = Config.DB_TYPE.lower()
            if Config.DB_URL:
                db_type = DBType.POSTGRESQL

        if db_type == DBType.SQLITE or db_type == DBType.POSTGRESQL:
            return "RANDOM()"
        else:  # MySQL
            return "RAND()"

    @staticmethod
    def get_ignore_syntax(db_type=None):
        """
        获取 INSERT IGNORE 语法

        Returns:
            tuple: (insert_syntax, or_syntax)
        """
        if db_type is None:
            db_type = Config.DB_TYPE.lower()
            if Config.DB_URL:
                db_type = DBType.POSTGRESQL

        if db_type == DBType.SQLITE:
            return ("INSERT OR IGNORE", "OR")
        else:  # MySQL, PostgreSQL
            return ("INSERT IGNORE", "OR")

    @staticmethod
    def get_auto_increment_syntax(db_type=None):
        """获取自增列语法"""
        if db_type is None:
            db_type = Config.DB_TYPE.lower()
            if Config.DB_URL:
                db_type = DBType.POSTGRESQL

        if db_type == DBType.SQLITE:
            return "INTEGER PRIMARY KEY AUTOINCREMENT"
        elif db_type == DBType.POSTGRESQL:
            return "SERIAL PRIMARY KEY"
        else:  # MySQL
            return "INT AUTO_INCREMENT PRIMARY KEY"

    @staticmethod
    def is_sqlite(db_type=None):
        """判断是否是SQLite"""
        if db_type is None:
            db_type = Config.DB_TYPE.lower()
            if Config.DB_URL:
                return False
        return db_type == DBType.SQLITE

    @staticmethod
    def is_mysql(db_type=None):
        """判断是否是MySQL"""
        if db_type is None:
            db_type = Config.DB_TYPE.lower()
            if Config.DB_URL:
                return False
        return db_type == DBType.MYSQL

    @staticmethod
    def is_postgresql(db_type=None):
        """判断是否是PostgreSQL"""
        if db_type is None:
            return bool(Config.DB_URL)
        return db_type == DBType.POSTGRESQL


# 便捷函数
def get_placeholder():
    """获取SQL占位符"""
    return DBHelper.get_placeholder()


def get_now_function():
    """获取当前时间SQL函数"""
    return DBHelper.get_now_function()


def is_sqlite():
    """判断是否是SQLite"""
    return DBHelper.is_sqlite()


def is_mysql():
    """判断是否是MySQL"""
    return DBHelper.is_mysql()


def is_postgresql():
    """判断是否是PostgreSQL"""
    return DBHelper.is_postgresql()


if __name__ == "__main__":
    # 测试
    print("占位符:", get_placeholder())
    print("时间函数:", get_now_function())
    print("随机函数:", DBHelper.get_random_function())
    print("是否SQLite:", is_sqlite())
    print("是否MySQL:", is_mysql())
    print("是否PostgreSQL:", is_postgresql())
