import time
import unittest

from fastergerman.game import SimpleGameTimer, TimerError, GameTimer


class GameTimerCommon:
    class GameTimerTest(unittest.TestCase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.tolerance = 10

        def _create_timer(self, interval_millis: int = 1000) -> GameTimer:
            raise NotImplementedError("Please implement me")

        def test_timings(self):
            uut = self._create_timer()
            expected = 3000
            uut.start(expected)
            uut.stop()
            time.sleep(1)
            uut.resume()
            result = uut.get_time_spent_millis() + uut.get_time_left_millis()
            self.assertLessEqual(expected - result, self.tolerance)
            result = uut.get_end_time_millis() - uut.get_start_time_millis() - uut.get_stop_period_millis()
            self.assertLessEqual(expected - result, self.tolerance)

        def test_start_should_succeed_when_already_started(self):
            uut = self._create_timer()
            uut.start(3000)
            uut.start(3000)

        def test_start_should_succeed_when_no_arg(self):
            self._create_timer().start()

        def test_stop_should_succeed_when_not_started(self):
            self._create_timer().stop()

        def test_resume_should_succeed_when_already_started(self):
            uut = self._create_timer()
            uut.start(3000)
            uut.resume()

        def test_resume_should_fail_when_not_started(self):
            uut = self._create_timer()
            self.assertRaises(TimerError, uut.resume)

        def test_get_time_remaining_millis_not_affected_by_time_spent_after_stop(self):
            uut = self._create_timer()
            uut.start(3000)
            time.sleep(1)
            uut.stop()
            time.sleep(1)
            self.assertLessEqual(2000 - uut.get_time_left_millis(), self.tolerance)

        def test_get_time_remaining_millis_not_affected_by_time_spent_after_stop2(self):
            uut = self._create_timer()
            uut.start(3000)
            time.sleep(1)
            uut.stop()
            time.sleep(1)
            uut.resume()
            time.sleep(1)
            self.assertLessEqual(1000 - uut.get_time_left_millis(), self.tolerance)

        def test_get_time_remaining_millis(self):
            uut = self._create_timer()
            rem = 3000
            sleep_time = 1
            uut.start(rem)
            time.sleep(sleep_time)
            val = uut.get_time_left_millis()

            lhs = int(rem/1000) - sleep_time
            rhs = int(val/1000)
            self.assertLessEqual(lhs - rhs, self.tolerance)

        def test_is_timed_out_when_timed_out(self):
            uut = self._create_timer()
            uut.start(500)
            time.sleep(0.5)
            self.assertTrue(uut.is_timed_out())

        def test_is_timed_out_when_not_timed_out(self):
            uut = self._create_timer()
            uut.start(3000)
            self.assertFalse(uut.is_timed_out())

        def test_tick_listeners_can_be_added(self):
            uut = self._create_timer()
            uut.add_tick_listener(lambda x: x)
            self.assertEqual(1, len(uut.get_tick_listeners()))

        def test_tick_listeners_cannot_be_updated(self):
            uut = self._create_timer()
            uut.add_tick_listener(lambda x: x)
            uut.get_tick_listeners().clear()
            self.assertEqual(1, len(uut.get_tick_listeners()))


class SimpleGameTimerTest(GameTimerCommon.GameTimerTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _create_timer(self, interval_millis: int = 1000) -> GameTimer:
        return SimpleGameTimer(interval_millis)


if __name__ == '__main__':
    unittest.main()
