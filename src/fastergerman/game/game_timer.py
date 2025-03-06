import logging
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, unique
from typing import Callable

logger = logging.getLogger(__name__)


class TimerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


class AbstractGameTimer(ABC):
    def __init__(self):
        self.__tick_listeners = []

    def add_tick_listener(self, listener: Callable[[int], None]):
        self.__tick_listeners.append(listener)

    def get_tick_listeners(self) -> list[Callable[[int], None]]:
        return [e for e in self.__tick_listeners]

    @abstractmethod
    def is_started(self):
        raise NotImplementedError("Subclasses should implement this method to return whether the timer is started.")

    @abstractmethod
    def is_stopped(self):
        raise NotImplementedError("Subclasses should implement this method to return whether the timer is stopped.")

    @abstractmethod
    def start(self, duration: int or None = None):
        raise NotImplementedError("Subclasses should implement this method to start the timer.")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Subclasses should implement this method to stop the timer.")

    @abstractmethod
    def resume(self):
        raise NotImplementedError("Subclasses should implement this method to resume the timer.")

    @abstractmethod
    def get_interval_millis(self) -> int:
        raise NotImplementedError("Subclasses should implement this method to return the interval in millis.")

    @abstractmethod
    def get_time_left_millis(self) -> int:
        raise NotImplementedError("Subclasses should implement this method to return the time left in millis.")

    @abstractmethod
    def get_time_spent_millis(self) -> int:
        raise NotImplementedError("Subclasses should implement this method to return the time spent in millis.")

    @abstractmethod
    def get_start_time_millis(self) -> int:
        raise NotImplementedError("Subclasses should implement this method to return the start time in millis.")

    @abstractmethod
    def get_end_time_millis(self) -> int:
        raise NotImplementedError("Subclasses should implement this method to return the end time in millis.")

    @abstractmethod
    def get_stop_period_millis(self):
        raise NotImplementedError("Subclasses should implement this method to return the stop period in millis.")

    @abstractmethod
    def is_timed_out(self) -> bool:
        raise NotImplementedError("Subclasses should implement this method to return whether the timer has timed out.")

@unique
class GameTimerState(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    STOPPED = "Stopped"

class GameTimer(AbstractGameTimer):
    def __init__(self, interval_millis: int):
        super().__init__()
        self.__interval_millis = interval_millis
        self._reset()

    def is_started(self):
        return self.__start_time is not None

    def is_stopped(self):
        return self.__stop_time is not None

    def start(self, duration: int or None = None):
        logger.debug("Starting timer: %s", self)
        self._reset()
        self.__start_time = self._now_millis()
        self.__duration = sys.maxsize if duration is None else duration

    def stop(self):
        logger.debug("Stopping timer: %s", self)
        self.__stop_time = self._now_millis()

    def resume(self):
        logger.debug("Resuming timer: %s", self)
        if self.is_started() is False:
            raise self._was_never_started_error()
        if self.__stop_time is not None:
            self.__stop_period += (self._now_millis() - self.__stop_time)
            # logger.debug("Stop period: %d", self.__stop_period)
            self.__stop_time = None

    def get_interval_millis(self) -> int:
        return self.__interval_millis

    def get_time_left_millis(self) -> int:
        if self.__duration is None:
            return 0
        return max(0, self.__duration - self.get_time_spent_millis())

    def get_time_spent_millis(self) -> int:
        if self.__start_time is None:
            return 0
        if self.__stop_period < 0: # This should not happen
            raise TimerError("Timer is in an illegal state")
        bookmark = self.__stop_time if self.__stop_time is not None else self._now_millis()
        return int(bookmark - self.__start_time - self.__stop_period)

    def get_start_time_millis(self) -> int:
        return self.__start_time

    def get_end_time_millis(self) -> int:
        if self.__start_time is None or self.__duration is None:
            return 0
        if self.__stop_period < 0: # This should not happen
            raise TimerError("Timer is in an illegal state")
        return int(self.__start_time + self.__duration + self.__stop_period)

    def get_stop_period_millis(self):
        return self.__stop_period

    def is_timed_out(self) -> bool:
        if self.is_started() is False:
            return False
        return self.get_time_left_millis() <= 99 # allow for drifts in time

    @staticmethod
    def _now_millis() -> int:
        return int(datetime.now().timestamp() * 1000)

    @staticmethod
    def _was_never_started_error():
        return TimerError("Timer was never started in the first place")

    def _reset(self):
        self.__start_time = None
        self.__duration = None
        self.__stop_time = None
        self.__stop_period = 0

    def __str__(self):
        return (f"SimpleGameTimer(started={self.is_started()}, interval={self.get_interval_millis()}millis"
                f", time left={self.get_time_left_millis()}millis)")