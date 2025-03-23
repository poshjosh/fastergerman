import time
import unittest

from fastergerman.web import RateLimiter


class RatelimiterTestCase(unittest.TestCase):
    def test_exceeds_limit(self):
        limiter = RateLimiter(1, 1000)
        limiter.is_within_limit("key")
        self.assertFalse(limiter.is_within_limit("key"))

    def test_time_spent_removes_limit(self):
        limiter = RateLimiter(1, 1000)
        limiter.is_within_limit("key")
        self.assertFalse(limiter.is_within_limit("key"))
        time.sleep(1.5)
        self.assertTrue(limiter.is_within_limit("key"))
        self.assertFalse(limiter.is_within_limit("key"))

    def test_within_limit(self):
        limiter = RateLimiter(2, 1000)
        limiter.is_within_limit("key")
        self.assertTrue(limiter.is_within_limit("key"))

    def test_within_limit_with_timeout(self):
        limiter = RateLimiter(2, 1000)
        limiter.is_within_limit("key")
        time.sleep(0.5)
        self.assertTrue(limiter.is_within_limit("key"))

if __name__ == '__main__':
    unittest.main()
