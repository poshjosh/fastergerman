import logging

from fastergerman.game import GameTimer

logger = logging.getLogger(__name__)


class UIGameTimer(GameTimer):
    def __init__(self, root, interval_millis: int):
        super().__init__(interval_millis)
        self.__root = root
        self.__id = None

    def start(self, duration: int or None = None):
        super().start(duration)
        self._cancel()
        self._schedule_next()

    def stop(self):
        super().stop()
        self._cancel()

    def resume(self):
        super().resume()
        self._schedule_next()

    def _cancel(self):
        if self.__id:
            self.__root.after_cancel(self.__id)
            self.__id = None

    def _schedule_next(self):
        self.__id = self.__root.after(self.get_interval_millis(), self._tick)

    def _tick(self):
        if self.is_started() is False or self.is_stopped() is True:
            return
        if self.get_time_left_millis() > 0:
            self._schedule_next()
        [e(self.get_time_left_millis()) for e in self.get_tick_listeners()]


    def __str__(self):
        return (f"UIGameTimer(started={self.is_started()}, interval={self.get_interval_millis()}millis"
                f", time left={self.get_time_left_millis()}millis)")
