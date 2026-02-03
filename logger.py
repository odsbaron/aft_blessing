# -*- coding: utf-8 -*-
"""
统一日志系统
提供结构化的日志记录功能
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from flask import request
from config import Config


class Logger:
    """统一日志管理器"""

    _instances = {}
    _initialized = False

    # 日志级别
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def init(cls, log_dir='logs', log_level=logging.INFO):
        """初始化日志系统"""
        if cls._initialized:
            return

        # 创建日志目录
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # 清除现有处理器
        root_logger.handlers.clear()

        # 日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 文件处理器 - 普通日志
        file_handler = RotatingFileHandler(
            log_path / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # 文件处理器 - 错误日志
        error_handler = RotatingFileHandler(
            log_path / 'error.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

        cls._initialized = True

    @classmethod
    def get(cls, name):
        """获取指定名称的日志记录器"""
        if not cls._initialized:
            cls.init()

        if name not in cls._instances:
            cls._instances[name] = logging.getLogger(name)
        return cls._instances[name]

    @classmethod
    def log_request(cls, request, response_time=None):
        """记录HTTP请求"""
        logger = cls.get('http')
        logger.info(f"{request.method} {request.path} - {response_time}ms" if response_time else f"{request.method} {request.path}")

    @classmethod
    def log_email_sent(cls, to, subject, success=True):
        """记录邮件发送"""
        logger = cls.get('email')
        if success:
            logger.info(f"邮件发送成功: {to} - {subject}")
        else:
            logger.error(f"邮件发送失败: {to}")

    @classmethod
    def log_auth_event(cls, event, username=None):
        """记录认证事件"""
        logger = cls.get('auth')
        logger.info(f"认证事件: {event}" + (f" - 用户: {username}" if username else ""))

    @classmethod
    def log_error(cls, error, context=None):
        """记录错误"""
        logger = cls.get('error')
        logger.exception(f"错误: {str(error)}" + (f" - 上下文: {context}" if context else ""))

    @classmethod
    def log_api_call(cls, endpoint, params=None, user=None):
        """记录API调用"""
        logger = cls.get('api')
        logger.debug(f"API调用: {endpoint}" + (f" - 参数: {params}" if params else ""))

    @classmethod
    def log_nft_event(cls, event, address=None, tx_hash=None):
        """记录NFT事件"""
        logger = cls.get('nft')
        logger.info(f"NFT事件: {event}" + (f" - 地址: {address}" if address else "") + (f" - 交易: {tx_hash}" if tx_hash else ""))


# 便捷函数
def get_logger(name):
    """获取日志记录器"""
    return Logger.get(name)


def log_request(request, response_time=None):
    """记录HTTP请求"""
    Logger.log_request(request, response_time)


def log_email_sent(to, subject, success=True):
    """记录邮件发送"""
    Logger.log_email_sent(to, subject, success)


def log_auth_event(event, username=None):
    """记录认证事件"""
    Logger.log_auth_event(event, username)


def log_error(error, context=None):
    """记录错误"""
    Logger.log_error(error, context)


def init_logger(log_dir='logs', log_level=logging.INFO):
    """初始化日志系统"""
    Logger.init(log_dir, log_level)


# Flask日志中间件
def log_request_middleware(app):
    """添加请求日志中间件"""
    @app.before_request
    def before_request():
        request.start_time = datetime.now()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            response_time = (datetime.now() - request.start_time).total_seconds() * 1000
            Logger.log_request(request, response_time)
        return response


if __name__ == "__main__":
    # 测试日志系统
    Logger.init()

    logger = Logger.get('test')
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")

    # 测试各种日志
    log_email_sent("test@example.com", "测试邮件", success=True)
    log_auth_event("登录成功", "admin")
    log_error(Exception("测试错误"), "测试上下文")
