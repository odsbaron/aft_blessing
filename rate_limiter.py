# -*- coding: utf-8 -*-
"""
邮件发送速率限制器
防止邮件服务被滥用，避免触发邮箱服务商的频率限制
"""

import time
from threading import Lock
from collections import defaultdict
from datetime import datetime, timedelta
from config import Config


class RateLimiter:
    """
    令牌桶算法实现的速率限制器

    功能:
    - 每小时最大发送数量限制
    - 每日最大发送数量限制
    - 同一接收者冷却时间（防止短时间内重复发送）
    - 平滑发送控制（避免瞬间爆发）
    """

    def __init__(self):
        # 速率配置
        self.max_per_hour = getattr(Config, 'MAX_EMAILS_PER_HOUR', 50)
        self.max_per_day = getattr(Config, 'MAX_EMAILS_PER_DAY', 200)
        self.cooldown_seconds = getattr(Config, 'EMAIL_COOLDOWN_SECONDS', 300)  # 5分钟
        self.min_interval_seconds = getattr(Config, 'MIN_EMAIL_INTERVAL', 2)  # 最小间隔2秒

        # 记录状态
        self.hourly_count = 0
        self.daily_count = 0
        self.last_email_time = 0
        self.hour_start = datetime.now()
        self.day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 用户冷却记录 (email -> timestamp)
        self.user_cooldowns = defaultdict(float)

        # 线程锁
        self.lock = Lock()

        # 统计信息
        self.total_sent = 0
        self.total_blocked = 0

    def _reset_if_needed(self):
        """检查并重置计数器"""
        now = datetime.now()

        # 检查小时计数器
        if now - self.hour_start >= timedelta(hours=1):
            self.hourly_count = 0
            self.hour_start = now

        # 检查日计数器
        if now.date() > self.day_start.date():
            self.daily_count = 0
            self.day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    def check_limit(self, recipient_email=None):
        """
        检查是否可以发送邮件

        Args:
            recipient_email: 收件人邮箱（可选，用于检查冷却时间）

        Returns:
            (can_send: bool, reason: str or None)
        """
        with self.lock:
            self._reset_if_needed()

            # 检查小时限制
            if self.hourly_count >= self.max_per_hour:
                return False, f"超过每小时限制 ({self.max_per_hour}封/小时)"

            # 检查日限制
            if self.daily_count >= self.max_per_day:
                return False, f"超过每日限制 ({self.max_per_day}封/天)"

            # 检查收件人冷却时间
            if recipient_email:
                last_sent = self.user_cooldowns.get(recipient_email, 0)
                cooldown_remaining = self.cooldown_seconds - (time.time() - last_sent)
                if cooldown_remaining > 0:
                    minutes = int(cooldown_remaining // 60)
                    seconds = int(cooldown_remaining % 60)
                    return False, f"收件人冷却中，请等待 {minutes}分{seconds}秒"

            # 检查最小发送间隔
            interval_remaining = self.min_interval_seconds - (time.time() - self.last_email_time)
            if interval_remaining > 0:
                return False, f"发送间隔过短，请等待 {int(interval_remaining)}秒"

            return True, None

    def record_sent(self, recipient_email=None):
        """记录成功发送的邮件"""
        with self.lock:
            self._reset_if_needed()
            self.hourly_count += 1
            self.daily_count += 1
            self.last_email_time = time.time()
            self.total_sent += 1

            if recipient_email:
                self.user_cooldowns[recipient_email] = time.time()

    def record_blocked(self):
        """记录被阻止的发送尝试"""
        with self.lock:
            self.total_blocked += 1

    def get_stats(self):
        """获取速率限制器统计信息"""
        with self.lock:
            self._reset_if_needed()

            now = datetime.now()
            hour_remaining = 60 - int((now - self.hour_start).total_seconds() / 60)
            day_remaining = 24 - now.hour - 1

            return {
                'hourly_sent': self.hourly_count,
                'hourly_limit': self.max_per_hour,
                'hour_remaining': hour_remaining,
                'daily_sent': self.daily_count,
                'daily_limit': self.max_per_day,
                'day_remaining': day_remaining,
                'total_sent': self.total_sent,
                'total_blocked': self.total_blocked,
                'active_cooldowns': len([
                    t for t in self.user_cooldowns.values()
                    if time.time() - t < self.cooldown_seconds
                ])
            }

    def reset(self):
        """重置所有计数器（管理员功能）"""
        with self.lock:
            self.hourly_count = 0
            self.daily_count = 0
            self.hour_start = datetime.now()
            self.day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            self.user_cooldowns.clear()

    def clear_cooldown(self, email):
        """清除指定邮箱的冷却时间（管理员功能）"""
        with self.lock:
            if email in self.user_cooldowns:
                del self.user_cooldowns[email]
                return True
            return False


# 全局单例
_rate_limiter_instance = None
_rate_limiter_lock = Lock()


def get_rate_limiter():
    """获取全局速率限制器实例"""
    global _rate_limiter_instance
    with _rate_limiter_lock:
        if _rate_limiter_instance is None:
            _rate_limiter_instance = RateLimiter()
        return _rate_limiter_instance


def check_rate_limit(recipient_email=None):
    """便捷函数：检查速率限制"""
    limiter = get_rate_limiter()
    return limiter.check_limit(recipient_email)


def record_email_sent(recipient_email=None):
    """便捷函数：记录邮件发送"""
    limiter = get_rate_limiter()
    limiter.record_sent(recipient_email)


def get_rate_limit_stats():
    """便捷函数：获取速率限制统计"""
    limiter = get_rate_limiter()
    return limiter.get_stats()


# ============ 装饰器版本 ============

def rate_limit(func):
    """
    速率限制装饰器
    用于装饰邮件发送函数
    """
    def wrapper(*args, **kwargs):
        limiter = get_rate_limiter()

        # 尝试从参数中获取收件人邮箱
        recipient = None
        if len(args) > 0:
            recipient = args[0]  # 假设第一个参数是邮箱

        can_send, reason = limiter.check_limit(recipient)

        if not can_send:
            limiter.record_blocked()
            raise RateLimitExceeded(reason)

        try:
            result = func(*args, **kwargs)
            limiter.record_sent(recipient)
            return result
        except Exception as e:
            # 发送失败，不记录计数
            raise e

    return wrapper


class RateLimitExceeded(Exception):
    """速率限制异常"""

    def __init__(self, reason):
        self.reason = reason
        super().__init__(f"邮件发送受限: {reason}")


# ============ 测试代码 ============

if __name__ == "__main__":
    # 测试速率限制器
    print("📧 邮件速率限制器测试")
    print("=" * 40)

    limiter = RateLimiter()

    # 测试检查
    can_send, reason = limiter.check_limit("test@example.com")
    print(f"检查发送 test@example.com: {can_send}, {reason}")

    # 记录发送
    limiter.record_sent("test@example.com")
    print("已记录发送")

    # 获取统计
    stats = limiter.get_stats()
    print(f"统计信息: {stats}")

    # 测试冷却
    can_send, reason = limiter.check_limit("test@example.com")
    print(f"再次检查 test@example.com: {can_send}, {reason}")
