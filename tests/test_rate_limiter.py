# -*- coding: utf-8 -*-
"""
速率限制器单元测试
"""

import unittest
import time
from rate_limiter import RateLimiter, RateLimitExceeded


class TestRateLimiter(unittest.TestCase):
    """速率限制器测试"""

    def setUp(self):
        """每个测试前的设置"""
        self.limiter = RateLimiter()

    def test_initial_state(self):
        """测试初始状态"""
        stats = self.limiter.get_stats()
        self.assertEqual(stats['hourly_sent'], 0)
        self.assertEqual(stats['daily_sent'], 0)
        self.assertEqual(stats['total_sent'], 0)

    def test_check_limit_pass(self):
        """测试通过限制检查"""
        can_send, reason = self.limiter.check_limit("test@example.com")
        self.assertTrue(can_send)
        self.assertIsNone(reason)

    def test_record_sent(self):
        """测试记录发送"""
        self.limiter.record_sent("test@example.com")
        stats = self.limiter.get_stats()
        self.assertEqual(stats['hourly_sent'], 1)
        self.assertEqual(stats['daily_sent'], 1)
        self.assertEqual(stats['total_sent'], 1)

    def test_cooldown(self):
        """测试冷却时间"""
        # 第一次发送
        self.limiter.record_sent("test@example.com")

        # 立即再次检查应该被冷却限制
        can_send, reason = self.limiter.check_limit("test@example.com")
        self.assertFalse(can_send)
        self.assertIn("冷却", reason)

    def test_hourly_limit(self):
        """测试每小时限制"""
        # 设置一个很小的限制用于测试
        self.limiter.max_per_hour = 3

        # 发送3次
        for _ in range(3):
            self.limiter.record_sent(f"user{i}@example.com")

        # 第4次应该被限制
        can_send, reason = self.limiter.check_limit("user4@example.com")
        self.assertFalse(can_send)
        self.assertIn("小时", reason)

    def test_daily_limit(self):
        """测试每日限制"""
        # 设置一个很小的限制用于测试
        self.limiter.max_per_day = 5

        # 发送5次
        for _ in range(5):
            self.limiter.record_sent(f"user{i}@example.com")

        # 第6次应该被限制
        can_send, reason = self.limiter.check_limit("user6@example.com")
        self.assertFalse(can_send)
        self.assertIn("天", reason)

    def test_reset(self):
        """测试重置功能"""
        # 发送一些记录
        for i in range(3):
            self.limiter.record_sent(f"user{i}@example.com")

        # 重置
        self.limiter.reset()

        # 检查状态
        stats = self.limiter.get_stats()
        self.assertEqual(stats['hourly_sent'], 0)
        self.assertEqual(stats['daily_sent'], 0)

    def test_clear_cooldown(self):
        """测试清除冷却"""
        # 发送一次
        self.limiter.record_sent("test@example.com")

        # 应该被冷却限制
        can_send, _ = self.limiter.check_limit("test@example.com")
        self.assertFalse(can_send)

        # 清除冷却
        result = self.limiter.clear_cooldown("test@example.com")
        self.assertTrue(result)

        # 现在应该可以通过
        can_send, _ = self.limiter.check_limit("test@example.com")
        self.assertTrue(can_send)

    def test_different_users(self):
        """测试不同用户独立计数"""
        # 用户A发送
        self.limiter.record_sent("usera@example.com")

        # 用户B应该不受影响
        can_send, _ = self.limiter.check_limit("userb@example.com")
        self.assertTrue(can_send)

        # 但用户A应该被冷却限制
        can_send, _ = self.limiter.check_limit("usera@example.com")
        self.assertFalse(can_send)


class TestRateLimiterIntegration(unittest.TestCase):
    """速率限制器集成测试"""

    def test_rate_limit_decorator(self):
        """测试速率限制装饰器"""
        from rate_limiter import rate_limit, RateLimitExceeded

        limiter = RateLimiter()
        limiter.max_per_hour = 2

        @rate_limit
        def send_email(email, content):
            return f"Sent to {email}"

        # 正常发送
        result = send_email("test@example.com", "Hello")
        self.assertEqual(result, "Sent to test@example.com")

        # 超过限制
        send_email("test2@example.com", "Hello")

        with self.assertRaises(RateLimitExceeded):
            send_email("test3@example.com", "Hello")


if __name__ == '__main__':
    unittest.main()
